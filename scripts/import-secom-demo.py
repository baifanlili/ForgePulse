"""Import a small SECOM semiconductor manufacturing sample into ForgePulse.

Source:
    https://archive.ics.uci.edu/ml/machine-learning-databases/secom/

The raw dataset is downloaded into data/secom/ and is intentionally ignored by Git.
"""

from __future__ import annotations

import argparse
import math
import os
from datetime import datetime
from pathlib import Path
from typing import Iterable
from urllib.request import urlretrieve

import psycopg
from psycopg.types.json import Jsonb


SECOM_DATA_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/secom/secom.data"
SECOM_LABELS_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/secom/secom_labels.data"
DATA_SOURCE = "SECOM"
DEVICE_CODE = "SECOM-FAB-01"
LOT_CODE = "SECOM-REAL-2008"
SELECTED_SENSOR_INDICES = [0, 1, 2, 3, 4, 5, 6, 12, 14, 15, 16, 20]


def env(name: str, fallback: str) -> str:
    return os.getenv(name, fallback)


def database_url(args: argparse.Namespace) -> str:
    host = args.db_host or env("POSTGRES_HOST", "localhost")
    port = args.db_port or env("POSTGRES_PORT", "5432")
    db = args.db_name or env("POSTGRES_DB", "forgepulse")
    user = args.db_user or env("POSTGRES_USER", "forgepulse")
    password = args.db_password or env("POSTGRES_PASSWORD", "forgepulse")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def ensure_download(url: str, path: Path) -> None:
    if path.exists() and path.stat().st_size > 0:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url} -> {path}", flush=True)
    urlretrieve(url, path)


def parse_label_line(line: str) -> tuple[int, datetime]:
    label, raw_timestamp = line.strip().split(maxsplit=1)
    timestamp = datetime.strptime(raw_timestamp.strip('"'), "%d/%m/%Y %H:%M:%S")
    return int(label), timestamp


def parse_float(value: str) -> float | None:
    try:
        parsed = float(value)
    except ValueError:
        return None
    if math.isnan(parsed):
        return None
    return parsed


def iter_samples(data_path: Path, labels_path: Path, limit: int) -> Iterable[tuple[int, datetime, list[float | None]]]:
    with data_path.open("r", encoding="utf-8") as data_file, labels_path.open("r", encoding="utf-8") as label_file:
        for index, (data_line, label_line) in enumerate(zip(data_file, label_file), start=1):
            if index > limit:
                break
            label, timestamp = parse_label_line(label_line)
            values = [parse_float(value) for value in data_line.strip().split()]
            yield label, timestamp, values


def clean_existing(cur: psycopg.Cursor, sample_tag: str) -> None:
    cur.execute(
        """
        DELETE FROM telemetry_points
        WHERE tags ->> 'data_source' = %s
        """,
        (sample_tag,),
    )
    cur.execute("DELETE FROM alarms WHERE alarm_code LIKE 'SECOM-FAIL-%%'")
    cur.execute("DELETE FROM bin_counts WHERE lot_code = %s", (LOT_CODE,))
    cur.execute("DELETE FROM wafer_yields WHERE lot_code = %s", (LOT_CODE,))
    cur.execute("DELETE FROM lots WHERE lot_code = %s", (LOT_CODE,))


def import_samples(conn: psycopg.Connection, samples: list[tuple[int, datetime, list[float | None]]]) -> dict[str, int | float]:
    if not samples:
        raise RuntimeError("No SECOM samples were loaded")

    pass_count = sum(1 for label, _, _ in samples if label == -1)
    fail_count = sum(1 for label, _, _ in samples if label == 1)
    total_count = len(samples)
    yield_rate = round(pass_count / total_count * 100, 2)
    started_at = min(timestamp for _, timestamp, _ in samples)
    completed_at = max(timestamp for _, timestamp, _ in samples)

    with conn.cursor() as cur:
        clean_existing(cur, DATA_SOURCE)

        cur.execute(
            """
            INSERT INTO devices (
                device_code,
                device_name,
                device_type,
                area,
                line,
                status,
                last_heartbeat_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (device_code) DO UPDATE SET
                device_name = EXCLUDED.device_name,
                device_type = EXCLUDED.device_type,
                area = EXCLUDED.area,
                line = EXCLUDED.line,
                status = EXCLUDED.status,
                last_heartbeat_at = EXCLUDED.last_heartbeat_at,
                updated_at = NOW()
            """,
            (
                DEVICE_CODE,
                "SECOM 半导体制造线",
                "Semiconductor Process",
                "UCI-SECOM",
                "Real Dataset",
                "warning" if fail_count else "running",
                completed_at,
            ),
        )

        cur.execute(
            """
            INSERT INTO lots (
                lot_code,
                product_code,
                route_name,
                started_at,
                completed_at,
                wafer_count,
                total_die,
                pass_die,
                fail_die,
                yield_rate
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (lot_code) DO UPDATE SET
                product_code = EXCLUDED.product_code,
                route_name = EXCLUDED.route_name,
                started_at = EXCLUDED.started_at,
                completed_at = EXCLUDED.completed_at,
                wafer_count = EXCLUDED.wafer_count,
                total_die = EXCLUDED.total_die,
                pass_die = EXCLUDED.pass_die,
                fail_die = EXCLUDED.fail_die,
                yield_rate = EXCLUDED.yield_rate
            """,
            (
                LOT_CODE,
                "SECOM-UCI",
                "secom-real-process",
                started_at,
                completed_at,
                total_count,
                total_count,
                pass_count,
                fail_count,
                yield_rate,
            ),
        )

        cur.executemany(
            """
            INSERT INTO bin_counts (lot_code, bin_name, die_count)
            VALUES (%s, %s, %s)
            ON CONFLICT (lot_code, bin_name) DO UPDATE SET
                die_count = EXCLUDED.die_count
            """,
            [
                (LOT_CODE, "Pass label -1", pass_count),
                (LOT_CODE, "Fail label 1", fail_count),
            ],
        )

        telemetry_rows = []
        alarm_rows = []
        for sample_index, (label, timestamp, values) in enumerate(samples, start=1):
            sample_id = f"SECOM-{sample_index:04d}"
            for sensor_index in SELECTED_SENSOR_INDICES:
                if sensor_index >= len(values):
                    continue
                value = values[sensor_index]
                if value is None:
                    continue
                telemetry_rows.append(
                    (
                        timestamp,
                        DEVICE_CODE,
                        f"sensor_{sensor_index:03d}",
                        value,
                        Jsonb(
                            {
                                "data_source": DATA_SOURCE,
                                "dataset": "UCI SECOM",
                                "sample_id": sample_id,
                                "label": label,
                                "label_meaning": "fail" if label == 1 else "pass",
                            }
                        ),
                    )
                )

            if label == 1:
                alarm_rows.append(
                    (
                        f"SECOM-FAIL-{sample_index:04d}",
                        DEVICE_CODE,
                        "warning",
                        "SECOM 失效样本",
                        f"UCI SECOM 样本 {sample_id} 标记为失效标签 1。",
                        "active",
                        timestamp,
                    )
                )

        cur.executemany(
            """
            INSERT INTO telemetry_points (
                time,
                device_code,
                metric_name,
                metric_value,
                tags
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            telemetry_rows,
        )

        cur.executemany(
            """
            INSERT INTO alarms (
                alarm_code,
                device_code,
                severity,
                title,
                description,
                status,
                started_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            alarm_rows,
        )

    conn.commit()
    return {
        "samples": total_count,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "yield_rate": yield_rate,
        "telemetry_points": len(telemetry_rows),
        "alarms": len(alarm_rows),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import UCI SECOM demo data into ForgePulse")
    parser.add_argument("--data-dir", default="data/secom", help="Directory for downloaded raw files")
    parser.add_argument("--limit", type=int, default=300, help="Maximum SECOM samples to import")
    parser.add_argument("--db-host")
    parser.add_argument("--db-port")
    parser.add_argument("--db-name")
    parser.add_argument("--db-user")
    parser.add_argument("--db-password")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_dir = Path(args.data_dir)
    data_path = data_dir / "secom.data"
    labels_path = data_dir / "secom_labels.data"

    ensure_download(SECOM_DATA_URL, data_path)
    ensure_download(SECOM_LABELS_URL, labels_path)

    samples = list(iter_samples(data_path, labels_path, args.limit))
    with psycopg.connect(database_url(args)) as conn:
        summary = import_samples(conn, samples)

    print("Imported UCI SECOM dataset sample:")
    for key, value in summary.items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    main()
