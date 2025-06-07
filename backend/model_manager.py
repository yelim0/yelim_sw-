import os
from werkzeug.utils import secure_filename

class ModelManager:
    MODEL_DIR = 'models' 
    ALLOWED_EXTENSIONS = {'pkl', 'joblib'}

    def __init__(self):
        os.makedirs(self.MODEL_DIR, exist_ok=True)

    def list_models(self):
        """현재 등록된 모델 목록을 반환"""
        return os.listdir(self.MODEL_DIR)

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def upload_model(self, file):
        if not file or file.filename == '':
            return False, "파일이 선택되지 않았습니다."

        if not self.allowed_file(file.filename):
            return False, "허용되지 않은 파일 형식입니다."

        filename = secure_filename(file.filename)
        file_path = os.path.join(self.MODEL_DIR, filename)
        file.save(file_path)
        return True, f"모델 '{filename}' 이(가) 업로드되었습니다."

    def delete_model(self, filename):
        file_path = os.path.join(self.MODEL_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True, f"모델 '{filename}' 이(가) 삭제되었습니다."
        else:
            return False, "해당 모델이 존재하지 않습니다."
