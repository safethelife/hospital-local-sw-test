import base64

from flask import Flask, request, redirect, url_for, render_template, send_file
from pymongo import MongoClient
import gridfs
from pydicom import dcmread, dcmwrite
import qrcode
import io
from werkzeug.utils import secure_filename

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client['dicom_database']
fs = gridfs.GridFS(db)
collection = db['dicom_files']

ALLOWED_EXTENSIONS = {'dcm'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def list_files():
    files = list(collection.find({}, {'_id': 0, 'name': 1, 'patient_id': 1, 'filename': 1}))
    return render_template('upload.html', files=files)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return 'No selected file', 400

    dicom_data = dcmread(file.stream)
    # Add code to anonymize DICOM data here

    binary_data = io.BytesIO()
    dcmwrite(binary_data, dicom_data)
    binary_data.seek(0)

    fs_id = fs.put(binary_data, filename=secure_filename(file.filename))

    collection.insert_one({
        'name': request.form.get('patient_name', 'Unknown'),
        'patient_id': request.form.get('patient_id', 'Unknown'),
        'filename': secure_filename(file.filename), # 이 줄을 추가
        'fs_id': fs_id  # Store the file's GridFS ID
    })

    return redirect(url_for('list_files'))


@app.route('/download/<filename>')
def download_file(filename):
    # Check if the filename is valid
    if not filename:
        print("No filename provided for download.")
        return 'No filename provided', 400

    # Attempt to find the document in the database
    file_doc = collection.find_one({'filename': filename})
    if not file_doc:
        print(f"File {filename} not found in the database.")
        return 'File not found', 404

    # Attempt to retrieve the file from GridFS
    try:
        fs_file = fs.get(file_doc['fs_id'])
        # Read the DICOM file into a pydicom Dataset
        dicom_data = dcmread(fs_file)

        # Anonymize the DICOM dataset (remove or replace patient information)
        tags_to_anonymize = ['PatientName', 'PatientID', 'PatientBirthDate', 'PatientSex',
                             'PatientAge', 'PatientWeight', 'PatientAddress']

        for tag in tags_to_anonymize:
            if tag in dicom_data:
                delattr(dicom_data, tag)

        # Convert the anonymized dataset back to binary
        anonymized_data = io.BytesIO()
        dcmwrite(anonymized_data, dicom_data)
        anonymized_data.seek(0)

        # Send the anonymized DICOM file as a response
        return send_file(
            anonymized_data,
            mimetype='application/dicom',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"Error retrieving file {filename} from GridFS: {e}")
        return 'Error downloading file', 500


@app.route('/show_qr/<filename>')
def show_qr(filename):
    # 변경된 ngrok URL 사용
    download_url = f'https://f367-61-81-223-102.ngrok-free.app/download/{filename}'

    # 기존 QR 코드 생성 로직 유지
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(download_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    img_data = base64.b64encode(img_io.getvalue()).decode('utf-8')
    return render_template('show_qr.html', qr_code_data=img_data)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
