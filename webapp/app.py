from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 현재 스크립트의 위치를 기준으로 uploads 폴더의 절대 경로를 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'dcm'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 파일 이름과 환자 정보를 연결해 저장할 딕셔너리
file_patient_info = {}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def list_files():
    """업로드된 파일 목록과 관련된 환자 정보를 보여주는 페이지를 렌더링합니다."""
    return render_template('upload.html', files=file_patient_info)


@app.route('/upload', methods=['POST'])
def upload_file():
    """파일을 업로드하고 환자 정보를 저장합니다."""
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return 'No selected file', 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file.save(file_path)

    # 환자 정보를 딕셔너리에 저장
    patient_name = request.form.get('patient_name', 'Unknown')
    patient_id = request.form.get('patient_id', 'Unknown')
    file_patient_info[filename] = {'name': patient_name, 'id': patient_id}

    return redirect(url_for('list_files'))


@app.route('/download/<filename>')
def download_file(filename):
    """업로드된 파일을 다운로드합니다."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
