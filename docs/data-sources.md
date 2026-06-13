# 数据来源

本文档记录 ForgePulse 可使用的公开数据集、用途建议和许可证注意事项。

项目默认优先使用合成数据；如引入外部数据，应在导入脚本、文档和演示页面中标明来源、许可证与用途。

## 推荐优先级

| 优先级 | 数据集 | 类型 | 建议用途 | 许可证/注意事项 |
| --- | --- | --- | --- | --- |
| P0 | SECOM | 半导体制造过程传感器与良率标签 | 缺陷检测、异常检测、SPC/质量分析演示 | UCI 标注为 CC BY 4.0，适合优先接入 |
| P0 | AI4I 2020 Predictive Maintenance | 合成预测性维护数据 | 设备健康、故障分类、维护预测演示 | UCI 标注为 CC BY 4.0，体量小，适合快速导入 |
| P1 | WM-811K / LSWMD | 晶圆图/缺陷模式 | Wafer map、缺陷分类、良率可视化 | Kaggle 页面标注 CC0，但文件较大，不建议直接提交到仓库 |
| P2 | NASA Milling Wear | 刀具磨损/加工过程数据 | 通用工业设备退化与 RUL 演示 | NASA 页面标注为 other-license-specified，接入前需再次确认使用条款 |
| P2 | PHM / PCB 生产线类数据 | 质量预测、SPI/AOI | 扩展到电子制造质量预测 | 不同挑战赛许可证不同，接入前需逐项确认 |

## 数据集说明

### SECOM

SECOM 是半导体制造过程数据，包含多维传感器特征和通过/失败标签。它适合补充 ForgePulse 的质量分析场景，例如：

- 将特征列映射为 `telemetry_points`
- 将标签映射为 Lot/Wafer 质量结果
- 构造异常检测和良率预测示例

建议做法：

1. 不把原始数据提交到 Git。
2. 使用 `scripts/import-secom-demo.py`，从 UCI 下载文件导入 PostgreSQL。
3. 在 `docs/data-sources.md` 和导入脚本中保留来源与许可证说明。

导入命令：

```bash
docker run --rm --network forgepulse_default -v "$PWD:/workspace" forgepulse/platform-api:dev \
  python /workspace/scripts/import-secom-demo.py --db-host postgres --data-dir /workspace/data/secom
```

默认导入前 300 条 SECOM 样本，映射为：

- 设备：`SECOM-FAB-01`
- Lot：`SECOM-REAL-2008`
- 遥测指标：`sensor_000`、`sensor_001` 等传感器列
- 告警：标签为 `1` 的失效样本生成 `SECOM-FAIL-*` 告警

### AI4I 2020 Predictive Maintenance

AI4I 2020 是面向预测性维护的合成数据集，体量小、字段规整，适合先做导入脚本和设备健康演示。

适合映射为：

- `devices`：设备或产品类型
- `telemetry_points`：温度、转速、扭矩、磨损等指标
- `alarms`：故障类型或失效标签

因为它是合成数据，更适合公开 demo 和 CI 测试。

### WM-811K / LSWMD

WM-811K 是晶圆图数据集，包含大量 wafer map 和缺陷模式标注。它更贴合半导体良率和缺陷分析，但文件较大。

建议后续作为独立可选数据包处理：

- 不提交原始 `.pkl` 或 `.mat` 文件
- 只导入少量抽样数据做 demo
- 新增 Wafer map 可视化页面时再接入

## 仓库约定

- `data/`、`datasets/`、`*.pkl`、`*.mat`、`*.csv` 原始大文件不应提交到 Git。
- 允许提交小型、人工构造的 demo fixture。
- 外部数据应通过脚本导入，脚本必须说明数据来源、许可证和下载位置。
- 如数据许可证限制商业用途或再分发，不得把原始数据随仓库发布。

## 下一步建议

优先接入 AI4I 2020 或 SECOM：

1. 先接入 AI4I 2020，快速形成设备健康和故障预测 demo。
2. 再接入 SECOM，增强半导体制造质量分析场景。
3. 最后抽样接入 WM-811K，做晶圆图缺陷分类和可视化。
