from fastapi import FastAPI
from routes.main import router
from fastapi.staticfiles import StaticFiles


def include_router(app: FastAPI):
    app.include_router(router)

def start_api() -> FastAPI :
    app = FastAPI(title="Files Manager", version="1.0.1")
    
    # Set the style folder for HTMLResponses 
    app.mount("/static", StaticFiles(directory="core/Templates/styles"), name="static")
    
    include_router(app)
    
    return app

api = start_api()