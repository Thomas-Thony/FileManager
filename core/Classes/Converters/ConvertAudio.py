from fastapi.responses import StreamingResponse
from fastapi import UploadFile, HTTPException
from pydub import AudioSegment
from io import BytesIO
from typing import Any
import magic


class ConvertAudio:
    
    @staticmethod
    def convert_audio(file: UploadFile, new_extension: str) -> Any:
        try:
            file.file.seek(0) # Reviens au début du fichier
            input_buf = BytesIO(file.file.read()) # Lis les octets du fichier
            output_buf = BytesIO()
            mime = magic.Magic(mime=True)
            new_mime = mime.from_buffer(output_buf.getvalue())
            new_file_name = (file.filename or "").rsplit(".", 1)[0]

            # Lire le fichier uploadé dans un buffer
            audio: Any = AudioSegment.from_file(input_buf)

            # Exporter dans un buffer de sortie
            audio.export(output_buf, format=new_extension)
            output_buf.seek(0)

            return StreamingResponse(
                output_buf,
                media_type=new_mime,
                headers={
                    "Content-Disposition": f"attachment; filename={new_file_name}.{new_extension}"
                }
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la conversion audio : {e}")