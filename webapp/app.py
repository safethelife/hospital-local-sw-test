from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 현재 스크립트의 위치를 기준으로 uploads 폴더의 절대 경로를 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'dcm'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 허용된 파일 확장자 확인 함수
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def list_files():
    """업로드된 파일 목록을 보여주는 페이지를 렌더링합니다."""
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('upload.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    """파일을 업로드하고 업로드 폼을 다시 렌더링합니다."""
    # 요청에서 파일 부분이 없는 경우
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    # 사용자가 파일을 선택하지 않고 제출한 경우
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 파일 저장 디렉토리가 존재하는지 확인하고, 없으면 생성
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('list_files'))

@app.route('/download/<filename>')
def download_file(filename):
    """업로드된 파일을 다운로드합니다."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
