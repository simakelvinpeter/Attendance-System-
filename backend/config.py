# Reads .env
import os
from dotenv import load_dotenv

load_dotenv()

COM_PORT = os.getenv('COM_PORT', 'COM3')
DB_PATH = os.getenv('DB_PATH', 'attendance.db')
