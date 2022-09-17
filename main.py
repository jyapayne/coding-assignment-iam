from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

html = open("index.html").read()

@app.get("/")
async def root():
    return HTMLResponse(html)
