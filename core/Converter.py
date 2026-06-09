from core.Options import Options
from core.Classes.Converters.ConvertImage import ConvertImage
from core.Classes.Converters.ConvertAudio import ConvertAudio
from core.Classes.Converters.ConvertVideo import ConvertVideo
from core.templates import templates
#from core.Handlers.templates import templates
from typing import  Any
from fastapi import HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from io import BytesIO   
import pypandoc
# import exiftool
import os
import tempfile
import shutil
import mimetypes

class Converter:
    
    @staticmethod
    async def is_convertion_valid(file: UploadFile, new_extension: str, request: Request) -> Any:
        try:
            options = Options('./core/Options.json')
            if options.is_in_extension(file, new_extension) != True :
                return templates.TemplateResponse(request=request, name="error.html", context={"error_detail": f"Le format d'origine et de destination ne sont pas compatibles !"})
                
            file_size_mb = (file.size or 0) / 1000000 # Convert bytes to MB
            
            if file_size_mb >= options.max_size:
                return templates.TemplateResponse(request=request, name="error.html", context={"error_detail": f"Votre fichier doit faire strictement moins de {options.max_size} MO !"})

            return await Converter.select_converter(file, new_extension, request)
        except Exception as e:
            return templates.TemplateResponse(request=request, name="error.html", context={"error_detail": f"Erreur lors de la vérification du fichier : {e}"})

    @staticmethod
    async def select_converter(file: UploadFile, new_extension: str, request: Request):
        # Sauvegarde temporaire sur le disque
        suffix = os.path.splitext(file.filename or "")[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
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
                return templates.TemplateResponse(request=request, name="error.html", context={"error_detail": "Le fichier possède un format non pris en charge"})
        
        # Nettoyage du fichier temporaire dans tous les cas (succès ou erreur)
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
            
        return converter

    @staticmethod
    def convert_text(tmp_path: str, file: UploadFile,  new_extension: str, request: Request):
        try:
            buf = BytesIO()
            binary_file = buf.read(-1)
            output: str = tmp_path + "." + new_extension
            new_file_name = (file.filename or "").rsplit(".", 1)[0]
            pypandoc.convert_text(source=binary_file, to=new_extension, format=new_extension)
            new_file = FileResponse(
                path=output,
                media_type=mimetypes.types_map["."+new_extension],
                filename=new_file_name + "." + new_extension
            )
            return new_file
        except Exception as e:
            return templates.TemplateResponse(request=request, name="error.html", context={"error_detail": f"Une erreur a été rencontrée lors de la conversion du texte : {e}"})
        
    @staticmethod
    def convert_document(tmp_path: str, file: UploadFile,  new_extension: str, request: Request) -> Any | bool:
        try:
            extra_args = []
            if new_extension == "pdf":
                extra_args = ["--pdf-engine=weasyprint"]
            
            output = tmp_path + "." + new_extension
            new_file_name = (file.filename or "").rsplit(".", 1)[0]
            pypandoc.convert_file(tmp_path, new_extension, outputfile=output, extra_args=extra_args)
            new_file = FileResponse(
                path=output,
                media_type=mimetypes.types_map["."+new_extension],
                filename=new_file_name + "." + new_extension
            )
            return new_file
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Une erreur a été rencontrée lors de la conversion du document : {e}")

    #
    # @staticmethod
    # def extract_file_properties(path: str) -> List[dict[str, Any]]:
    #    absolute_path = os.path.abspath(path)
    #    with exiftool.ExifToolHelper() as et:
    #        metadata = et.get_metadata(absolute_path)
    #    return metadata