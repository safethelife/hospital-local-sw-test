import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
from queue import Queue, Empty
import pydicom
import boto3
from botocore.exceptions import NoCredentialsError
import os
from env import settings



def extract_patient_info(dicom_file_path):
    ds = pydicom.dcmread(dicom_file_path)
    patient_name = str(ds.PatientName) if 'PatientName' in ds else 'Unknown'
    patient_id = str(ds.PatientID) if 'PatientID' in ds else 'Unknown'
    patient_birth_date = str(ds.PatientBirthDate) if 'PatientBirthDate' in ds else 'Unknown'
    patient_sex = str(ds.PatientSex) if 'PatientSex' in ds else 'Unknown'
    return patient_name, patient_id, patient_birth_date, patient_sex


def upload_to_s3(file_name, bucket, object_name=None, metadata=None):
    if object_name is None:
        object_name = file_name
    if metadata is None:
        metadata = {}

    # S3 클라이언트 생성
    s3_client = boto3.client('s3',
                             aws_access_key_id=settings.AWS['access_key_id'],
                             aws_secret_access_key=settings.AWS['secret_access_key'])

    try:
        # 파일 내용 읽기
        with open(file_name, 'rb') as file_data:
            s3_client.put_object(Bucket=bucket, Key=object_name, Body=file_data, Metadata=metadata)
        print(f"File {object_name} uploaded successfully with metadata.")
    except NoCredentialsError:
        print("Credentials not available")
        return False
    return True



class FileEventHandler(FileSystemEventHandler):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal
        self.buffer = Queue()
        self.buffer_timeout = 2  # 버퍼 타임아웃을 2초로 설정
        self.last_event_time = time.time()

        # 버퍼 처리 스레드 시작
        threading.Thread(target=self.process_buffer, daemon=True).start()

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.dcm'):
            self.buffer.put(event.src_path)
            self.last_event_time = time.time()

    def process_buffer(self):
        while True:
            try:
                # 버퍼 타임아웃 동안 대기
                time.sleep(self.buffer_timeout)
                current_time = time.time()
                if current_time - self.last_event_time >= self.buffer_timeout:
                    # 타임아웃이 지나면 로그 출력 및 파일 업로드
                    try:
                        while True:
                            # 큐에서 파일 경로를 가져와 환자 정보를 추출
                            file_path = self.buffer.get_nowait()
                            patient_info = extract_patient_info(file_path)
                            message = f"New DICOM file: {os.path.basename(file_path)}, Patient Name: {patient_info[0]}, Patient ID: {patient_info[1]}, Birth Date: {patient_info[2]}, Sex: {patient_info[3]}"

                            # 파일을 S3에 업로드하면서 환자 이름과 ID를 메타데이터로 추가
                            metadata = {
                                'patient_name': patient_info[0],
                                'patient_id': patient_info[1]
                            }
                            upload_to_s3(file_path, settings.AWS['bucket'], os.path.basename(file_path), metadata)
                    except Empty:
                        pass
            except Exception as e:
                print(f"Error in process_buffer: {e}")


class DirectoryMonitorThread(QThread):
    newFileSignal = pyqtSignal(str)

    def __init__(self, directory):
        super().__init__()
        self.directory = directory

    def run(self):
        event_handler = FileEventHandler(self.newFileSignal)
        observer = Observer()
        observer.schedule(event_handler, self.directory, recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
                print("Monitoring...")
        finally:
            observer.stop()
            observer.join()



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.monitorThread = None

    def initUI(self):
        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('Directory Monitor')

        self.btnSelect = QPushButton("Select Directory", self)
        self.btnSelect.clicked.connect(self.openDirectoryDialog)
        self.selectedDirLabel = QLabel("Selected Directory: None", self)
        self.btnFinish = QPushButton("설정 완료", self)
        self.btnFinish.clicked.connect(self.finishSetup)
        self.logLabel = QLabel("Logs:", self)

        layout = QVBoxLayout()
        layout.addWidget(self.btnSelect)
        layout.addWidget(self.selectedDirLabel)
        layout.addWidget(self.btnFinish)
        layout.addWidget(self.logLabel)
        self.setLayout(layout)

        # 시스템 트레이 아이콘 설정
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon('C:/Users/dhwan/PycharmProjects/hospital/icon.png'))
        self.trayIcon.setVisible(True)

        # 트레이 메뉴 설정
        trayMenu = QMenu()
        openAction = trayMenu.addAction("Open")
        openAction.triggered.connect(self.show)
        exitAction = trayMenu.addAction("Exit")
        exitAction.triggered.connect(QApplication.instance().quit)
        self.trayIcon.setContextMenu(trayMenu)

        self.trayIcon.show()

    def openDirectoryDialog(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.selectedDirLabel.setText(f"Selected Directory: {directory}")
            if self.monitorThread is not None:
                self.monitorThread.terminate()
            self.monitorThread = DirectoryMonitorThread(directory)
            self.monitorThread.newFileSignal.connect(self.updateLog)
            self.monitorThread.start()

    def finishSetup(self):
        self.hide()

    def updateLog(self, log_message):
        self.logLabel.setText(log_message)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
