from fastapi import UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from PIL import Image
from io import BytesIO
import mimetypes

class ConvertImage:
    
    @staticmethod
    def convert_image(tmp_path: str, file: UploadFile, new_extension:str):
        try:
            new_file_name = (file.filename or "").rsplit(".", 1)[0]
            new_mime = mimetypes.types_map["."+new_extension]
            image = Image.open(file.file)
            buf = BytesIO()
            if image.mode in ("RGBA", "P", "LA"):
                image = image.convert("RGB")

            image.save(buf, format=new_extension.upper())
            buf.seek(0)
            new_file = StreamingResponse(
                    buf,
                    media_type=new_mime,
                    headers={
                        "Content-Disposition": 'attachment; filename='+ new_file_name + "." + new_extension
                    }
                )
            return new_file
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la conversion d'image : {e}")
    