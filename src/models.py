from collections import UserDict, defaultdict
from datetime import datetime, timedelta
import hashlib
import re

# Phone nr validation exception
class PhoneValidationError(Exception):
    pass

class CustomValueError(Exception):
    pass

class EmailValidationError(Exception):
    pass

class BirthdayValidationError(Exception):
    pass

# Base class
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
# Contact name class
class Name(Field):
    def __init__(self, value):
        value = self._validate(value)
        super().__init__(value)
    
    def _validate(self, value):
        if not value or not value.strip():
            raise CustomValueError("Name cannot be empty.")
        if len(value.strip()) < 2:
            raise CustomValueError("Name must be at least 2 characters long.")
        return value.strip()

class Address(Field):
    def __init__(self, value):
        value = self._validate(value)
        super().__init__(value)
    
    def _validate(self, value):
        if not value or not value.strip():
            raise CustomValueError("Address cannot be empty.")
        return value.strip()

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
            date_obj = datetime.strptime(value, "%d.%m.%Y").date()
            # Check if birthday is not in the future
            if date_obj > datetime.today().date():
                raise BirthdayValidationError("Birthday cannot be in the future.")
            # Check if birthday is not too far in the past (reasonable age limit)
            if date_obj < datetime(1900, 1, 1).date():
                raise BirthdayValidationError("Birthday seems unrealistic (before 1900).")
            return date_obj
        except ValueError:
            raise BirthdayValidationError("Invalid date format. Please use DD.MM.YYYY")
        
    def __str__(self):
        return self.value.strftime("%d.%m.%Y")    

# Phone nr class
class Phone(Field):
    def __init__(self, value):
        self._validate(value)
        super().__init__(value)

    def _validate(self, value):
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', value)
        
        # Check for common international formats
        if value.startswith('+'):
            # International format with country code
            if len(digits_only) < 10 or len(digits_only) > 15:
                raise PhoneValidationError("International phone number must be 10-15 digits (including country code).")
        elif value.startswith('00'):
            # International format starting with 00
            if len(digits_only) < 10 or len(digits_only) > 15:
                raise PhoneValidationError("International phone number must be 10-15 digits (including country code).")
        else:
            # Local format - must be exactly 10 digits
            if len(digits_only) != 10:
                raise PhoneValidationError("Local phone number must be exactly 10 digits.")
        
        # Store the cleaned version
        self.value = digits_only
        
# Email class
class Email(Field):
    email_regexp = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    def __init__(self, value):
        self._validate(value)
        super().__init__(value)

    def _validate(self, value):
        if not value or not value.strip():
            raise EmailValidationError("Email cannot be empty.")
        
        value = value.strip().lower()
        
        if not re.match(Email.email_regexp, value):
            raise EmailValidationError(f"Invalid email address format: {value}")
        
        # Additional checks
        if len(value) > 254:  # RFC 5321 limit
            raise EmailValidationError("Email address is too long.")
        
        if value.count('@') != 1:
            raise EmailValidationError("Email must contain exactly one @ symbol.")
        
        return value

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
    def __init__(self, title, note_text="", tags=None):
        self.title = Title(title)
        self.note_text = note_text
        self.tags = set(tags) if tags else set()
        self.id_hash = hashlib.sha1(title.encode()).hexdigest()[:6]

    def add_tag(self, tag):
        """Add a tag to the note"""
        if tag and tag.strip():
            self.tags.add(tag.strip().lower())
    
    def remove_tag(self, tag):
        """Remove a tag from the note"""
        self.tags.discard(tag.strip().lower())
    
    def has_tag(self, tag):
        """Check if note has a specific tag"""
        return tag.strip().lower() in self.tags

    def validate_note_text(self, note_text):
        MAX_TEXT_LENGTH = 150
        if not note_text.strip():
            return "Note text can not be empty"
        if len(note_text) > MAX_TEXT_LENGTH:
            return f"Note text is too long (max. is {MAX_TEXT_LENGTH} characters)"

    def __str__(self):
        tags_str = f" [Tags: {', '.join(sorted(self.tags))}]" if self.tags else ""
        return f"{self.id_hash} {self.title.value} {self.note_text}{tags_str}"


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

    # Find Record by ID hash
    def find_by_id(self, id_hash):
        for record in self.data.values():
            if record.id_hash == id_hash:
                return record
        return None

    # Search notes by tag
    def search_by_tag(self, tag):
        tag = tag.strip().lower()
        result = []
        for record in self.data.values():
            if record.has_tag(tag):
                result.append(record)
        return result

    # Get all unique tags
    def get_all_tags(self):
        all_tags = set()
        for record in self.data.values():
            all_tags.update(record.tags)
        return sorted(all_tags)

    # Get notes sorted by tags
    def get_notes_by_tags(self, tags=None):
        if not tags:
            return list(self.data.values())
        
        result = []
        for record in self.data.values():
            if any(tag.strip().lower() in record.tags for tag in tags):
                result.append(record)
        return result

    # Delete Record by title
    def delete(self, title):
        if title in self.data:
            del self.data[title]
