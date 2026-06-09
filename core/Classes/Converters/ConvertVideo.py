from fastapi import UploadFile, HTTPException
from fastapi.responses import Response
from io import BytesIO
import tempfile
import os
import ffmpeg
import magic
import asyncio


class ConvertVideo:

    @staticmethod
    async def convert_video(file: UploadFile, new_extension: str):

        def run_ffmpeg(input_path: str, output_path: str):
            try:
                out, err = (
                    ffmpeg
                    .input(input_path)
                    .output(
                        output_path,
                        vcodec="libx264",
                        acodec="aac",
                        format=new_extension
                    )
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )

            
            except Exception as e:
                print("FFmpeg crash:", str(e))
                raise

        input_path = None
        output_path = None

        try:
            await file.seek(0)
            input_bytes = await file.read()

            filename = file.filename or "video"
            basename = filename.rsplit(".", 1)[0]

            # fichier temporaire input
            with tempfile.NamedTemporaryFile(delete=False) as input_tmp:
                input_tmp.write(input_bytes)
                input_path = input_tmp.name

            output_path = f"{input_path}.{new_extension}"

            await asyncio.to_thread(run_ffmpeg, input_path, output_path)

            with open(output_path, "rb") as f:
                output_bytes = f.read()

            output_buf = BytesIO(output_bytes)

            mime = magic.Magic(mime=True)
            new_mime = mime.from_buffer(output_bytes)

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
                detail=f"Erreur lors de la conversion vidéo : {str(e)}"
            )

        finally:
            try:
                if input_path and os.path.exists(input_path):
                    os.remove(input_path)

                if output_path and os.path.exists(output_path):
                    os.remove(output_path)

            except Exception:
                pass