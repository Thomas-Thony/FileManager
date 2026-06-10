from fastapi import UploadFile, HTTPException
from fastapi.responses import Response
from typing import Literal
from io import BytesIO  
import tempfile
import os
import ffmpeg
import magic
import shlex

class ConvertVideo:

    @staticmethod
    async def convert_video(file: UploadFile, new_extension: str):
        input_path: str = ""
        output_path: str = ""
        buf = BytesIO()
        
        try:
            await file.seek(0)
            input_bytes = await file.read()

            filename = file.filename or "video" # If filename start with ".", add a default title 
            basename = filename.rsplit(".", 1)[0]

            # Temporary input file
            with tempfile.NamedTemporaryFile(delete=False) as input_tmp:
                input_tmp.write(input_bytes)
                input_path = input_tmp.name

            output_path = shlex.quote(f"{input_path}.{new_extension}") #Filter with escape shells args

            buf.seek(0)
            output_bytes = buf.read(-1)

            mime = magic.Magic(mime=True)
            new_mime: Literal["application/octet-stream"] = mime.from_buffer(output_bytes)

            return Response(
                content=output_bytes,
                media_type=new_mime,
                headers={
                    "Content-Disposition": f'attachment; filename="{basename}.{new_extension}"'
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
                if input_path and os.path.exists(input_path):
                    os.remove(input_path)

                if output_path and os.path.exists(output_path):
                    os.remove(output_path)

            except Exception:
                pass