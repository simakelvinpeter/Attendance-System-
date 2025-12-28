R307 Fingerprint Attendance 

Overview

The (R307 Fingerprint Attendance System) is a biometric-based attendance management solution.
It uses the R307 Optical Fingerprint Sensor connected via USB-TTL to a Windows PC.
The project features:

Python Backend (Flask + SQLite) for data storage and fingerprint processing
Tkinter Frontend for user interaction
Fingerprint enrollment and identification
Attendance logging and Excel export


Team Members & Responsibilities

| Name                             | Matric No. | Role                                                                        |
Sima Kelvin Peter            | 20234968   | Environment setup (Backend & Frontend dev environment)                      |
Wisdom Chizurumoke Edeji     | 20205317   | Backend development (Flask API, SQLite integration, fingerprint processing) |
Oluwatofunmi Gideon Akinwale | 20214454   | Frontend development (Tkinter GUI, Excel export, API integration)           |

Environment Setup (Windows)
1. Install Python

1. Download Python 3.10+ from [python.org](https://www.python.org/downloads/windows/).
2. During installation, check "Add Python to PATH".


2. Create Virtual Environment
powershell
python -m venv fingerprint-venv
fingerprint-venv\Scripts\activate
python -m pip install --upgrade pip

3. Install Dependencies

powershell
pip install pyserial pyfingerprint pandas openpyxl cryptography flask sqlalchemy
(Tkinter is included in Python on Windows.)

4. Install USB–Serial Driver

Plug in USB-TTL adapter.
Check **Device Manager → Ports (COM & LPT) for your COM port.
If driver missing, install:

  [CH340 Driver](https://sparks.gogo.co.nz/ch340.html)
  [CP210x Driver](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)


5. Wiring (R307 → USB-TTL)

| R307 Pin | USB-TTL Pin |
| -------- | ----------- |
| VCC  | 5V          |
| GND  | GND         |
| TX   | RX          |
| RX   | TX          |



6. Test Fingerprint Sensor

Create a file `enroll.py`:

python
from pyfingerprint.pyfingerprint import PyFingerprint

port = 'COM3'  # Change to your COM port
baud = 57600

try:
    f = PyFingerprint(port, baud, 0xFFFFFFFF, 0x00000000)
    if not f.verifyPassword():
        raise ValueError('Sensor password is wrong!')
except Exception as e:
    print('Failed to initialize sensor:')
    print(e)
    exit(1)

print('Waiting for finger...')
while not f.readImage():
    pass

f.convertImage(0x01)
result = f.searchTemplate()
position = result[0]

if position >= 0:
    print(f'Finger already enrolled at position #{position}')
else:
    print('Remove finger...')
    while f.readImage():
        pass
    print('Place same finger again...')
    while not f.readImage():
        pass
    f.convertImage(0x02)
    f.createTemplate()
    position = f.storeTemplate()
    print(f'Finger enrolled at position #{position}')


Run:

powershell
fingerprint-venv\Scripts\activate
python enroll.py


---

Project Structure
fingerprint_attendance/
│── backend/
│   ├── app.py          # Flask backend
│   ├── database.py     # SQLite logic
│   ├── fingerprint.py  # Sensor functions
│── frontend/
│   ├── gui.py          # Tkinter GUI
│   ├── export.py       # Excel export logic
│── requirements.txt
│── README.md

Task Distribution

Sima Kelvin Peter (20234968)

Created Python environment
Installed dependencies
Installed USB–Serial driver
Verified sensor with `enroll.py`

Wisdom Chizurumoke Edeji (20205317)

Build Flask backend with endpoints:

  `/enroll` → Enroll fingerprint
  `/identify` → Match fingerprint
  `/attendance` → Log attendance to SQLite
   Integrate `pyfingerprint` with backend
   Secure API with token-based authentication

Oluwatofunmi Gideon Akinwale (20214454)
Build Tkinter GUI:

  Trigger enrollment & identification
  Display attendance table
  Export to Excel via `pandas` + `openpyxl`
  Connect frontend to backend API
  Implement error handling & prompts



Running the Project

1. Start backend:

powershell
cd backend
python app.py
```

2. Start frontend:

```powershell
cd frontend
python gui.py
```




