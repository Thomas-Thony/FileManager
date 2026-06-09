from fastapi import APIRouter, Request, HTTPException, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from core.Options import Options
from core.Converter import Converter
from core.Compression import Compression
import re

router = APIRouter()
templates = Jinja2Templates(directory="core/Templates")
EXT_REGEX = re.compile(r"^[a-z]+$")

# region Routes divers
@router.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@router.get("/host")
def get_client_host(request: Request):
    if request.client is None:
        raise HTTPException(status_code=400, detail="Impossible de déterminer l'hôte client")
    return {"client_host": request.client.host}

#endregion

# region Conversion de fichier
@router.post("/convert")
async def convert_file(request: Request, file: UploadFile, new_extension: str = Form(...)):
    options = Options("./core/Options.json")
    if not EXT_REGEX.fullmatch(new_extension):
        raise HTTPException(status_code=400, detail="New extension invalid format")
    
    if options.is_in_extension(file, new_extension):  
        return await Converter.is_convertion_valid(file, new_extension, request)
    else:
        raise HTTPException(status_code=400, detail="New extension unknown !")
# endregion

#region Compression de fichier
@router.post("/compression")
def compress_file():
    return Compression.compression()
#endregion