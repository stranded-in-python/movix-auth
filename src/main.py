import uvicorn

if __name__ == "__main__":
    uvicorn.run(  # pyright: ignore
        "app:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=['/app']
    )
