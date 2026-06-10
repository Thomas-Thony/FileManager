from fastapi import APIRouter, Request, HTTPException, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from core.Options import Options
from core.Converter import Converter
from core.Compression import Compression
from core.Globals import REG_STR

router = APIRouter()
templates = Jinja2Templates(directory="core/Templates")

# region Miscellaneous paths
@router.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@router.get("/host")
def get_client_host(request: Request):
    if request.client is None:
        raise HTTPException(status_code=400, detail="Impossible de déterminer l'hôte client")
    return {"client_host": request.client.host} # In localhost, this should return 127.0.0.1

#endregion

# region File's conversion
@router.post("/convert")
async def convert_file(request: Request, file: UploadFile, new_extension: str = Form(...)):
    # Check if the new extension given is right according to the regex
    if not REG_STR.fullmatch(new_extension):
        raise HTTPException(status_code=400, detail="Please, enter a valid extension !")
    
    # Check if the new extension given exist among thoses in the options    
    options = Options("./core/Options.json")
    if options.is_in_extension(file, new_extension):
        return await Converter.is_convertion_valid(file, new_extension, request)
    else:
        raise HTTPException(status_code=400, detail="New extension unknown !")
# endregion

#region File's compression
@router.post("/compression")
def compress_file():
    return Compression.compression()
#endregion