from fastapi import FastAPI

app = FastAPI(title="FastAPI Project Management Mess", version="1.0.0")


@app.get("/")
async def root():
    return {"message": "server is up!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", port=7777, reload=True)
