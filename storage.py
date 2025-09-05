import json
import os
import threading
from typing import Any, Dict
from config import DATA_FILE, ADMIN_IDS

_lock = threading.RLock()

def init_data() -> None:
    with _lock:
        print(f"DEBUG: Checking if {DATA_FILE} exists")
        data_dir = os.path.dirname(DATA_FILE) or "."
        if not os.access(data_dir, os.W_OK | os.R_OK):
            print(f"ERROR: No read/write permissions for directory {data_dir}")
            raise PermissionError(f"No read/write permissions for directory {data_dir}")
        if not os.path.exists(DATA_FILE):
            print(f"DEBUG: Creating new data file: {DATA_FILE}")
            try:
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump({'events': [], 'questions': [], 'admins': ADMIN_IDS}, f, ensure_ascii=False, indent=2)
                print(f"DEBUG: Created {DATA_FILE} successfully")
            except Exception as e:
                print(f"ERROR: Failed to create {DATA_FILE}: {e}")
                raise
        else:
            print(f"DEBUG: Reading existing data file: {DATA_FILE}")
            try:
                data = read_data()
                print(f"DEBUG: Read data successfully: {data}")
                data['admins'] = list(set(data.get('admins', []) + ADMIN_IDS))
                write_data(data)
                print(f"DEBUG: Updated admins in {DATA_FILE}")
            except (json.JSONDecodeError, OSError) as e:
                print(f"ERROR: Failed to read or parse {DATA_FILE}: {e}. Recreating file...")
                try:
                    with open(DATA_FILE, "w", encoding="utf-8") as f:
                        json.dump({'events': [], 'questions': [], 'admins': ADMIN_IDS}, f, ensure_ascii=False, indent=2)
                    print(f"DEBUG: Recreated {DATA_FILE} successfully")
                except Exception as e:
                    print(f"ERROR: Failed to recreate {DATA_FILE}: {e}")
                    raise

def read_data() -> Dict[str, Any]:
    with _lock:
        if not os.path.exists(DATA_FILE):
            print(f"DEBUG: File {DATA_FILE} does not exist, initializing...")
            init_data()
        try:
            print(f"DEBUG: Opening file for read")
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                print(f"DEBUG: File opened, loading JSON")
                data = json.load(f)
                print(f"DEBUG: Successfully read data from {DATA_FILE}: {data}")
                return data
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in {DATA_FILE}: {e}. File will be recreated.")
            raise  # Поднимаем исключение, чтобы init_data обработал пересоздание
        except Exception as e:
            print(f"ERROR: Failed to read {DATA_FILE}: {e}")
            raise

import tempfile
import shutil

def write_data(data: Dict[str, Any]) -> None:
    with _lock:
        try:
            print(f"DEBUG: Writing data: {data}")
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as temp_file:
                json.dump(data, temp_file, ensure_ascii=False, indent=2)
                temp_file.flush()
                temp_file_name = temp_file.name
            shutil.move(temp_file_name, DATA_FILE)
            print(f"DEBUG: Wrote data to {DATA_FILE}")
        except Exception as e:
            print(f"ERROR: Failed to write to {DATA_FILE}: {e}")
            raise