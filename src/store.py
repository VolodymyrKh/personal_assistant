import pickle
from src.models import AddressBook, Note

FILE_NAME = "addressbook.pkl"
FILE_NAME_NOTES = "notes.pkl"

def save_data(book: AddressBook, filename=FILE_NAME):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename, class_name):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
        
    except FileNotFoundError:
        print(f"File '{filename}' not found. Creating a new {class_name.__name__} instance.")
        return class_name()
    
    except Exception as e:
        print(f"Error loading from '{filename}': {e}")
        return class_name()
    
def load_address_book():
    return load_data(FILE_NAME, AddressBook)

def load_notes_data():
    return load_data(FILE_NAME_NOTES, Note)

def save_notes_data(notes: Note):
    save_data(notes, FILE_NAME_NOTES)
