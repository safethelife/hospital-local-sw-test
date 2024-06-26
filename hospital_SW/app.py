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
import requests
import os

def extract_patient_info(dicom_file_path):
    ds = pydicom.dcmread(dicom_file_path)
    patient_name = str(ds.PatientName) if 'PatientName' in ds else 'Unknown'
    patient_id = str(ds.PatientID) if 'PatientID' in ds else 'Unknown'
    patient_birth_date = str(ds.PatientBirthDate) if 'PatientBirthDate' in ds else 'Unknown'
    patient_sex = str(ds.PatientSex) if 'PatientSex' in ds else 'Unknown'
    return patient_name, patient_id, patient_birth_date, patient_sex

def upload_file_to_flask(file_path):
    url = 'http://127.0.0.1:5000/upload'
    files = {'file': (os.path.basename(file_path), open(file_path, 'rb'))}
    patient_info = extract_patient_info(file_path)
    data = {
        'patient_name': patient_info[0],
        'patient_id': patient_info[1],
        'patient_birth_date': patient_info[2],
        'patient_sex': patient_info[3]
    }
    response = requests.post(url, files=files, data=data)
    print(f"File {os.path.basename(file_path)} uploaded with response: {response.text}")

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal
        self.buffer = Queue()
        self.buffer_timeout = 2
        self.last_event_time = time.time()
        threading.Thread(target=self.process_buffer, daemon=True).start()

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.dcm'):
            self.buffer.put(event.src_path)
            self.last_event_time = time.time()

    def process_buffer(self):
        while True:
            try:
                time.sleep(self.buffer_timeout)
                current_time = time.time()
                if current_time - self.last_event_time >= self.buffer_timeout and not self.buffer.empty():
                    while not self.buffer.empty():
                        file_path = self.buffer.get()
                        patient_info = extract_patient_info(file_path)
                        message = f"New DICOM file: {os.path.basename(file_path)}, Patient Name: {patient_info[0]}, Patient ID: {patient_info[1]}, Birth Date: {patient_info[2]}, Sex: {patient_info[3]}"
                        self.signal.emit(message)
                        upload_file_to_flask(file_path)
                    self.last_event_time = time.time()
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

    def initUI(self):
        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('DICOM File Monitoring and Upload')

        self.btnSelect = QPushButton("Select Directory", self)
        self.btnSelect.clicked.connect(self.openDirectoryDialog)

        self.selectedDirLabel = QLabel("Selected Directory: None", self)
        self.logLabel = QLabel("Logs:", self)

        layout = QVBoxLayout()
        layout.addWidget(self.btnSelect)
        layout.addWidget(self.selectedDirLabel)
        layout.addWidget(self.logLabel)
        self.setLayout(layout)

        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon('icon.png'))
        trayMenu = QMenu()
        openAction = trayMenu.addAction("Open")
        openAction.triggered.connect(self.show)
        exitAction = trayMenu.addAction("Exit")
        exitAction.triggered.connect(sys.exit)
        self.trayIcon.setContextMenu(trayMenu)
        self.trayIcon.show()

    def openDirectoryDialog(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.selectedDirLabel.setText(f"Selected Directory: {directory}")
            self.monitorThread = DirectoryMonitorThread(directory)
            self.monitorThread.newFileSignal.connect(self.updateLog)
            self.monitorThread.start()

    def updateLog(self, log_message):
        self.logLabel.setText(log_message)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
