import os
import shutil

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def save_uploaded_file(file, filename):
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file, buffer)
    return file_path

def delete_file(file_path):
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False