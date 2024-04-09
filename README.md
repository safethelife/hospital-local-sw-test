# DICOM Files Management and QR Code Generator

This project provides a solution for managing DICOM medical imaging files generated from CR scanners in healthcare facilities. It automates the process of uploading these files to a web server (local WAS), generating downloadable links, converting these links into QR codes, and enabling patients to download their medical data by scanning the QR code. This README outlines the setup, workflow, and testing of this system.

![architecture](https://github.com/safethelife/hospital-local-sw-test/assets/62466374/f97952a2-a2c0-4756-b1aa-80df08a57248)

## Workflow Overview

1. **CR Scanner Imaging**: A patient undergoes medical imaging with a CR scanner.
2. **Local PC Processing**: The CR scanner is connected to a local PC that generates the imaging results as DICOM files.
3. **Web Server Storage**: The generated DICOM files are automatically uploaded to a web server (local WAS), where a downloadable link for each file is created.
4. **QR Code Generation**: Each download link is converted into a QR code.
5. **QR Code Distribution**: The QR codes are printed at the reception desk's local PC and handed to patients.
6. **Patient Downloads Data**: Patients can scan the QR code to download their medical data.

## System Requirements

- CR Scanner connected to a Local PC.
- Local PC with internet access for uploading DICOM files.
- WAS setting for storing DICOM files.
- Web server capable of generating downloadable links and converting them into QR codes.
- Printer for QR codes at the reception desk.
- QR code scanning capability on the patient's device (e.g., smartphone).

## Setup and Configuration

### CR Scanner and Local PC

- Ensure the CR scanner is properly connected and configured to save DICOM files to a specific directory on the local PC.


### Web Server Setup

- Deploy a web server capable of handling file uploads to local WAS and generating downloadable links.
- Implement a QR code generation feature to convert download links into QR codes.

### Front Desk PC Configuration

- Setup a web page or application to display uploaded DICOM files and their corresponding QR codes.
- Ensure a printer is connected for printing QR codes.

## Usage

1. **DICOM File Generation**: Conduct medical imaging with the CR scanner. The local PC will automatically generate and save DICOM files.
2. **File Monitoring and Upload**: The system monitors the designated directory for new DICOM files and uploads them to the local WAS.
3. **Downloadable Link and QR Code Generation**: For each uploaded file, the web server generates a downloadable link, converts it into a QR code, and displays it on the front desk PC.
4. **QR Code Printing**: Print the QR code for the patient at the reception desk.
5. **Patient Downloads Data**: The patient scans the QR code with their device to download their medical data.

## Testing

To test this repository's functionality:

1. Simulate DICOM file generation by adding files to the monitored directory.
2. Verify that the files are uploaded to loacl WAS and that downloadable links are generated.
3. Check the web page or application at the front desk PC for the new files and their QR codes.
4. Test the QR code with a mobile device to ensure it correctly downloads the DICOM file.

## Contributions

Contributions to this project are welcome. Please submit pull requests or issues through GitHub to propose enhancements or report bugs.
