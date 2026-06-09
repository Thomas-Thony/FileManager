from fastapi import Request, UploadFile

class Compression: 
    @staticmethod
    def select_compression(file: UploadFile, request: Request):
        return False
    
    @staticmethod
    def compression():
        return True