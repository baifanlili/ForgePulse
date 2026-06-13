from fastapi import FastAPI

app = FastAPI(title="ForgePulse Platform API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "platform-api"}
