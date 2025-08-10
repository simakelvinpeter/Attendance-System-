from pyfingerprint.pyfingerprint import PyFingerprint
import os
from dotenv import load_dotenv
load_dotenv()
PORT = os.getenv('COM_PORT', 'COM3')
BAUD = int(os.getenv('BAUD_RATE', '57600'))

def enroll():
    try:
        f = PyFingerprint(PORT, BAUD, 0xFFFFFFFF, 0x00000000)
        if not f.verifyPassword():
            raise ValueError('Sensor password wrong')
    except Exception as e:
        print('Sensor init failed:', e)
        return

    print('Place finger...')
    while not f.readImage():
        pass

    f.convertImage(0x01)
    result = f.searchTemplate()
    position = result[0]
    if position >= 0:
        print(f'Already enrolled at {position}')
        return

    print('Remove finger...')
    while f.readImage():
        pass

    print('Place same finger again...')
    while not f.readImage():
        pass

    f.convertImage(0x02)
    f.createTemplate()
    pos = f.storeTemplate()
    print('Enrolled at position', pos)

if __name__ == '__main__':
    enroll()
