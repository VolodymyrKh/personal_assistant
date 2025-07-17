from collections import UserDict, defaultdict
from datetime import datetime, timedelta
import hashlib
import re

# Phone nr validation exception
class PhoneValidationError(Exception):
    pass

class CustomValueError(Exception):
    pass

# Base class
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
# Contact name class
class Name(Field):
		pass

class Address(Field):
	pass

# Note title class
class Title(Field):
    def __init__(self, value):
        value = self._validate(value)
        super().__init__(value)

    def _validate(self, value):
        MAX_TITLE_LENGTH = 40
        if not value.strip():
            raise ValueError("Title cannot be empty.")
        if len(value) > MAX_TITLE_LENGTH:
            raise ValueError(f"Title is too long (max {MAX_TITLE_LENGTH} characters).")
        return value

# Contact birthday class
class Birthday(Field):
    def __init__(self, value):
        date_value = self._validate(value)
        super().__init__(date_value)

    def _validate(self, value):
        try:
            return datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise CustomValueError("Invalid date format. Please use DD.MM.YYYY")
        
    def __str__(self):
        return self.value.strftime("%d.%m.%Y")    

# Phone nr class
class Phone(Field):
    def __init__(self, value):
        self._validate(value)
        super().__init__(value)

    def _validate(self, value):
        if not re.fullmatch(r"\d{10}", value):
            raise PhoneValidationError          # Exception to handle in following implementation
        
# Email class
class Email(Field):
    email_regexp = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    def __init__(self, value):
        self._validate(value)
        super().__init__(value)

    def _validate(self, value):
        if not re.match(Email.email_regexp, value):
            raise CustomValueError(f"Invalid email address: {value}")

# One contact record: name, phone nr list.
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        self.email = None
        self.address = None

    def edit_name(self, new_name):
        self.name = Name(new_name)    

    def add_birthday(self, date_str):
        self.birthday = Birthday(date_str)

    # Add Phone instance into phones list
    def add_phone(self, phone):
        if self.find_phone(phone):
            raise CustomValueError(f"Phone number {phone} already exists for the contact.")
        phone_to_add = Phone(phone)   # Validate + add
        self.phones.append(phone_to_add)

    def add_email(self, email):
        self.email = Email(email)
    
    def add_address(self, address):
        self.address = Address(address)

    # Remove phone by value
    def remove_phone(self, phone):
        self.phones = [phone_nr for phone_nr in self.phones if phone_nr.value != phone]

    # Update phone nr with a new value
    def edit_phone(self, old_value, new_value):
        for i, p in enumerate(self.phones):
            if p.value == old_value:
                self.phones[i] = Phone(new_value)
                return True
        return False  # Can use in future True/False value to confirm if phone nr was updated or not found.

    # Search for a phone nr
    def find_phone(self, phone):
        for phone_nr in self.phones:
            if phone_nr.value == phone:
                return phone_nr
        return None

    def __str__(self):
        phones_str = "; ".join(p.value for p in self.phones)
        return f"Name: {self.name.value} | {'phones' if len(self.phones) > 1 else 'phone'}: {phones_str} | email: {self.email.value if self.email else ''} | birthday: {self.birthday.value if self.birthday else ''} | address: {self.address.value if self.address else ''}"
    
class NoteRecord:
    def __init__(self, title, note_text=""):
        self.title = Title(title)
        self.note_text = note_text
        self.id_hash = hashlib.sha1(title.encode()).hexdigest()[:6]


    def validate_note_text(self, note_text):
        MAX_TEXT_LENGTH = 150
        if not note_text.strip():
            return "Note text can not be empty"
        if len(note_text) > MAX_TEXT_LENGTH:
            return f"Note text is too long (max. is {MAX_TEXT_LENGTH} characters)"

    def __str__(self):
        return f"{self.id_hash} {self.title.value} {self.note_text}"


# AddressBook (Map for Records)
class AddressBook(UserDict):
    
    # Add record by contact name
    def add_record(self, record):
        self.data[record.name.value] = record

    # Find Record by name
    def find(self, name):
        return self.data.get(name)

    # Delete Record by name
    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def update_record_name(self, old_name, new_name):
        record = self.find(old_name)
        if record:
            record.edit_name(new_name)
            self.data[new_name] = record
            del self.data[old_name]        

    # Get next week birthday records
    def get_upcoming_birthdays(self, days=7):
        start_range = datetime.today().date()
        end_range = start_range + timedelta(days=days)
        upcoming_birthdays = defaultdict()

        for contact in self.data.values():
            if contact.birthday:
                birthday_this_year = contact.birthday.value.replace(year=start_range.year)

                #  Check if contact birthday falls within selected range
                if start_range <= birthday_this_year <= end_range:
                    upcoming_birthdays[contact.name.value] = contact
        return dict(upcoming_birthdays)
    
    def search_contacts(self, field_name: str, query: str):
        result = []

        valid_fields = ['name', 'phones', 'email', 'birthday', 'address']
        if field_name not in valid_fields:
            raise CustomValueError(f"Field '{field_name}' is not valid. Choose one of: {', '.join(valid_fields)}.")

        for record in self.data.values():
                
            field = getattr(record, field_name, None)
            if not field:
                continue

            if isinstance(field, list):
                for item in field:
                    if query.lower() in str(item.value).lower():
                        result.append(record)
                        break

            elif hasattr(field, 'value'):
                if query.lower() in str(field.value).lower():
                    result.append(record)
        return result
    
# Notes entity class    
class Note(UserDict):
    # Add record by note title
    def add_record(self, record):
        self.data[record.title.value] = record

    # Find Record by title
    def find(self, title):
        return self.data.get(title)
