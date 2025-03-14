from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
from app.routes import user, admin, webhook
import uvicorn

app = FastAPI(title="ArmenApp")

app.include_router(user.router)
app.include_router(admin.router)
app.include_router(webhook.router)

app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_index():
    base_dir = Path(__file__).resolve().parent.parent
    index_file = base_dir / "frontend" / "index.html"
    return index_file.read_text(encoding="utf-8")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
