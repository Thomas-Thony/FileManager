from fastapi import UploadFile, HTTPException
from fastapi.responses import Response
from typing import Literal
from io import BytesIO  
import tempfile
import os
import ffmpeg
import magic
class ConvertVideo:

    @staticmethod
    async def convert_video(file: UploadFile, new_extension: str):
        input_path: str = ""
        output_path: str = ""
        
        extension = (new_extension or "").lstrip(".")
        if not extension.isalnum():
            raise HTTPException(status_code=400, detail="Invalid extension format")
                
        try:
            await file.seek(0)
            input_bytes = await file.read()

            filename = file.filename or "video" # If filename start with ".", add a default title 
            basename = filename.rsplit(".", 1)[0]

            # Temporary input file(Security by recreating the file )
            with tempfile.NamedTemporaryFile(delete=False) as input_tmp:
                input_tmp.write(input_bytes)
                input_path = input_tmp.name
             
            # Temporary output file(Security by recreating the file )
            with tempfile.NamedTemporaryFile(delete=False) as output_tmp:
                input_tmp.write(input_bytes)
                output_path = output_tmp.name
                
            # output_path =  output_path = f"{input_path}.{extension}"
            
            buf = BytesIO()
            buf.seek(0)
            
            output_bytes = buf.read(-1)

            mime = magic.Magic(mime=True)
            new_mime: str | Literal["application/octet-stream"] = mime.from_buffer(output_bytes)

            return Response(
                content=output_bytes,
                media_type=new_mime,
                headers={
                    "Content-Disposition": f'attachment; filename="{basename}.{extension}"'
                }
            )

        except ffmpeg.Error as e:
            raise HTTPException(
                status_code=500,
                detail=e.stderr.decode("utf-8", errors="ignore")
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error while converting the video : {str(e)}"
            )

        finally:
            try:
                if os.path.exists(input_path):
                    os.remove(input_path)

                if os.path.exists(output_path):
                    os.remove(output_path)

            except Exception:
                pass