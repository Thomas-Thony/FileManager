from fastapi import UploadFile
import re
import os

REG_STR = re.compile(r"^[a-z]+$") 
ERROR_PAGE: str = "error.html"

def get_extension(file: UploadFile) -> str: 
    name: str = file.filename or ""
    return os.path.basename(name).strip().lower().lstrip(".")

def filter_extension(extension: str) -> str :
    name: str = extension or ""
    return os.path.basename(name).strip().lower().lstrip(".")