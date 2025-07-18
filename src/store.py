import pickle
import os
import shutil
from datetime import datetime
from src.models import AddressBook, Note

FILE_NAME = "addressbook.pkl"
FILE_NAME_NOTES = "notes.pkl"
BACKUP_DIR = "backups"

def ensure_backup_dir():
    """Ensure backup directory exists"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def create_backup(filename):
    """Create a backup of the data file"""
    if os.path.exists(filename):
        ensure_backup_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{BACKUP_DIR}/{os.path.basename(filename)}.{timestamp}.backup"
        shutil.copy2(filename, backup_name)
        return backup_name
    return None

def save_data(book: AddressBook, filename=FILE_NAME):
    """Save data with backup creation"""
    try:
        # Create backup before saving
        create_backup(filename)
        
        with open(filename, "wb") as f:
            pickle.dump(book, f)
        return True
    except Exception as e:
        print(f"Error saving data to '{filename}': {e}")
        return False

def load_data(filename, class_name):
    """Load data with improved error handling"""
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
        
    except FileNotFoundError:
        print(f"File '{filename}' not found. Creating a new {class_name.__name__} instance.")
        return class_name()
    
    except (pickle.UnpicklingError, EOFError) as e:
        print(f"Error loading from '{filename}': {e}")
        print("Attempting to restore from backup...")
        
        # Try to restore from backup
        backup_file = find_latest_backup(filename)
        if backup_file:
            try:
                with open(backup_file, "rb") as f:
                    data = pickle.load(f)
                print(f"Successfully restored from backup: {backup_file}")
                return data
            except Exception as backup_error:
                print(f"Failed to restore from backup: {backup_error}")
        
        print(f"Creating a new {class_name.__name__} instance.")
        return class_name()
    
    except Exception as e:
        print(f"Unexpected error loading from '{filename}': {e}")
        return class_name()

def find_latest_backup(filename):
    """Find the latest backup file for the given filename"""
    if not os.path.exists(BACKUP_DIR):
        return None
    
    base_name = os.path.basename(filename)
    backup_files = []
    
    for file in os.listdir(BACKUP_DIR):
        if file.startswith(base_name) and file.endswith('.backup'):
            backup_files.append(os.path.join(BACKUP_DIR, file))
    
    if backup_files:
        # Return the most recent backup
        return max(backup_files, key=os.path.getctime)
    
    return None

def load_address_book():
    return load_data(FILE_NAME, AddressBook)

def load_notes_data():
    return load_data(FILE_NAME_NOTES, Note)

def save_notes_data(notes: Note):
    return save_data(notes, FILE_NAME_NOTES)

def list_backups():
    """List all available backups"""
    if not os.path.exists(BACKUP_DIR):
        return "No backups found."
    
    backups = []
    for file in os.listdir(BACKUP_DIR):
        if file.endswith('.backup'):
            file_path = os.path.join(BACKUP_DIR, file)
            creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            backups.append((file, creation_time))
    
    if not backups:
        return "No backups found."
    
    backups.sort(key=lambda x: x[1], reverse=True)
    result = "Available backups:\n"
    for filename, creation_time in backups:
        result += f"  {filename} - {creation_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    return result
