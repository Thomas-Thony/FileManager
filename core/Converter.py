from core.Options import Options
from core.Classes.Converters.ConvertImage import ConvertImage
from core.Classes.Converters.ConvertAudio import ConvertAudio
from core.Classes.Converters.ConvertVideo import ConvertVideo
from core.templates import templates
from typing import  Any
from fastapi import HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from core.Globals import REG_STR, ERROR_PAGE
from io import BytesIO   
import pypandoc
import os
import tempfile
import shutil
import mimetypes

class Converter:
    
    @staticmethod
    async def is_convertion_valid(file: UploadFile, new_extension: str, request: Request) -> Any:
        try:
            options = Options('./core/Options.json')
            if not REG_STR.fullmatch(new_extension):
                raise HTTPException(status_code=400, detail="New extension invalid format")
            if options.is_in_extension(file, new_extension) != True :
                return templates.TemplateResponse(request=request, name=ERROR_PAGE, context={"error_detail": "The original and choosen format are not compatible !"})
                
            file_size_mb = (file.size or 0) / 1000000 # Convert bytes to MB
            
            # Check if file heavy or not 
            if file_size_mb >= options.max_size:
                return templates.TemplateResponse(request=request, name=ERROR_PAGE, context={"error_detail": f"Your file must be {options.max_size} MB or lighter !"})

            return await Converter.select_converter(file, new_extension, request)
        except Exception as e:
            return templates.TemplateResponse(request=request, name=ERROR_PAGE, context={"error_detail": f"Error while verifying your file : {e}"})

    @staticmethod
    async def select_converter(file: UploadFile, new_extension: str, request: Request):
        # Temporary save on the disk
        suffix = os.path.splitext(file.filename or "")[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path: str = tmp.name or ""
        
        mime_file = (file.content_type or "").split("/")[0]
        match mime_file :
            case "image":
                converter = ConvertImage.convert_image(tmp_path, file, new_extension)
            
            case "application": 
                converter = Converter.convert_document(tmp_path, file, new_extension, request)
            
            case "audio":
                converter = ConvertAudio.convert_audio(file, new_extension)
                
            case "video":
                converter = await ConvertVideo.convert_video(file, new_extension)
            
            case "text":
                converter = Converter.convert_text(tmp_path, file, new_extension, request)
            
            case _:
                return templates.TemplateResponse(request=request, name=ERROR_PAGE, context={"error_detail": "The file has an unknown type!"})

        # Cleaning of the temporary file in each cases (Success or Error)
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
            
        return converter

    @staticmethod
    def convert_text(tmp_path: str, file: UploadFile,  new_extension: str, request: Request):
        try:
            buf = BytesIO()
            binary_file = buf.read(-1)
            output: str = (tmp_path + "." + new_extension) or ""
            new_file_name = (file.filename or "").rsplit(".", 1)[0]
            pypandoc.convert_text(source=binary_file, to=new_extension, format=new_extension)
            new_file = FileResponse(
                path=output,
                media_type=mimetypes.types_map["."+new_extension],
                filename=new_file_name + "." + new_extension
            )
            return new_file
        except Exception as e:
            return templates.TemplateResponse(request=request, name=ERROR_PAGE, context={"error_detail": f"An error was encountered during the text conversion : {e}"})
        
    @staticmethod
    def convert_document(tmp_path: str, file: UploadFile,  new_extension: str, request: Request) -> Any | bool:
        try:
            # PDF conversion is not aviable by default in pypandoc, so we have to 'force' it
            extra_args = []
            if new_extension == "pdf":
                extra_args = ["--pdf-engine=weasyprint"]
            
            output: str = tmp_path + "." + new_extension
            new_file_name = (file.filename or "").rsplit(".", 1)[0]
            pypandoc.convert_file(tmp_path, new_extension, outputfile=output, extra_args=extra_args)
            new_file = FileResponse(
                path=output,
                media_type=mimetypes.types_map["."+new_extension],
                filename=new_file_name + "." + new_extension
            )
            return new_file
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"An error was encountered during the document conversion : {e}")