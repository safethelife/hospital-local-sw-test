import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pydicom
import os



def extract_patient_info(dicom_file_path):
    ds = pydicom.dcmread(dicom_file_path)
    patient_name = ds.PatientName if 'PatientName' in ds else 'Unknown'
    patient_id = ds.PatientID if 'PatientID' in ds else 'Unknown'
    patient_birth_date = ds.PatientBirthDate if 'PatientBirthDate' in ds else 'Unknown'
    patient_sex = ds.PatientSex if 'PatientSex' in ds else 'Unknown'
    return patient_name, patient_id, patient_birth_date, patient_sex


class FileEventHandler(FileSystemEventHandler):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.dcm'):
            patient_info = extract_patient_info(event.src_path)
            log_message = f"New DICOM file: {os.path.basename(event.src_path)}, Patient Name: {patient_info[0]}, Patient ID: {patient_info[1]}, Birth Date: {patient_info[2]}, Sex: {patient_info[3]}"
            self.signal.emit(log_message)



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
