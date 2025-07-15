import pickle
from src.models import AddressBook

FILE_NAME = "addressbook.pkl"

def save_data(book: AddressBook, filename=FILE_NAME):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename=FILE_NAME) -> AddressBook:
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
        
    except FileNotFoundError:
        return AddressBook()