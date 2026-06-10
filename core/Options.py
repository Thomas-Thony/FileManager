import json
from fastapi import UploadFile
from typing import Any
from fastapi import HTTPException
from core.Globals import REG_STR

class Options: 
    accpeted_mime: list[str]
    accepted_extensions: list[str]
    mimes_source: str
    extensions_source: str
    max_size: float
    
    def __init__(self, source: str) -> None:
        self.mimes_source = source
        self.extensions_source = source
        self.load()
    
    # On charge les données à partir des fichiers json
    def load(self): 
        with open(self.mimes_source, "r") as f:
            data = json.load(f)
            self.accpeted_mime = data["mimes"] 
            self.accepted_extensions = data["extensions"]
            self.max_size = data["parameters"]["max_size"]
        
    # Chargement d'options spécifiques par rapport à un type de fichiers
    def get_type_options(self, type: str) -> dict[str, Any]:
        with open(self.mimes_source) as f:
            data = json.load(f)
        for category, mimes in data["mimes"].items():
            # "image/png" est dans data["mimes"]["image"] => category = "image"
            if type in mimes:
                return {
                    "mimes": mimes,
                    "extensions": data["extensions"][category]  # data["extensions"]["image"]
                }
        raise ValueError(f"Type MIME non supporté : {type}")
    
    # Vérifie si l'extension de fichier correspond bien au type attendu
    def is_in_extension(self, file: UploadFile, new_extension: str) -> bool :
        if not REG_STR.fullmatch(new_extension):
            raise HTTPException(status_code=400, detail="New extension invalid format")
        
        list_option = self.get_type_options(file.content_type or "")
        
        if new_extension in list_option["extensions"]:
            return True
        else: 
            return False