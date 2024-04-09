# DICOM Files Management and QR Code Generator (Local WAS)

This project provides a comprehensive solution for managing DICOM medical imaging files, enabling secure local storage on a Web Application Server (WAS) and facilitating patient access through QR code scanning. This README outlines the setup, workflow, and guidelines for a local implementation, bypassing the need for cloud storage solutions like AWS S3 due to personal information security concerns.

![architecture](https://github.com/safethelife/hospital-local-sw-test/assets/62466374/f97952a2-a2c0-4756-b1aa-80df08a57248)

## Workflow Overview

1. **CR Scanner Imaging**: Patients undergo medical imaging using a CR scanner.
2. **Local PC Processing**: The CR scanner, connected to a local PC, generates imaging results as DICOM files.
3. **Local WAS Storage**: Generated DICOM files are automatically uploaded to a local Web Application Server, where downloadable links for each file are created.
4. **QR Code Generation**: Each download link is converted into a QR code for easy access.
5. **QR Code Distribution**: At the reception, a local PC prints the QR codes for patients to take with them.
6. **Patient Downloads Data**: Patients can scan the QR code with their mobile devices to download their medical data.

## System Requirements

- CR Scanner connected to a Local PC for DICOM file generation.
- Local Web Application Server (WAS) for secure storage of DICOM files.
- Software to generate QR codes from download links.
- Printer connected to the local PC at the reception for printing QR codes.
- Internet-enabled device for patients to scan QR codes and access their medical data.

## Setup and Configuration

### CR Scanner and Local PC

Ensure the CR scanner is properly connected to a local PC designed to generate DICOM files in a specified directory.

### Local WAS Configuration

Set up a local Web Application Server to receive and store DICOM files. Ensure it's secured and accessible only within the local network or VPN to protect patient information.

### QR Code Generation and Distribution

Implement functionality on the local WAS or use third-party software to generate QR codes from the downloadable links of the DICOM files stored on the server. Ensure the reception's local PC has access to this system for printing QR codes for patients.

## Usage

1. **DICOM File Generation**: Conduct medical imaging with the CR scanner. The local PC automatically generates DICOM files.
2. **File Monitoring and Upload**: A system monitors the specified directory for new DICOM files and uploads them to the local WAS.
3. **Downloadable Link and QR Code Generation**: The local WAS generates a downloadable link for each uploaded file, converts it into a QR code, and makes it available for printing.
4. **QR Code Printing and Distribution**: Print the QR code for patients at the reception desk.
5. **Patient Downloads Data**: Patients scan the QR code with their device to securely download their medical data.

## Security Considerations

- **Data Encryption**: Ensure all data transmissions within the local network are encrypted to protect patient information.
- **Access Control**: Implement strict access control measures on the local WAS to prevent unauthorized access to DICOM files.
- **Audit Trails**: Maintain logs of all accesses to the DICOM files for auditing and compliance purposes.

## Testing

To test the functionality of this repository:

1. Simulate the generation of DICOM files by adding files to the monitored directory.
2. Verify that the files are uploaded to the local WAS and that downloadable links are generated.
3. Check for the new files and their QR codes available for printing at the reception's local PC.
4. Test the QR code with a mobile device to ensure the correct download of the DICOM file.

## Contributions

Contributions to improve the project are welcome. Please submit pull requests or issues through GitHub to propose enhancements or report bugs.
