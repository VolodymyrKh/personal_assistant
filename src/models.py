from collections import UserDict, defaultdict
from datetime import datetime, timedelta
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

# Note title class
class Title(Field):
    def __init__(self, value):
        value = self._validate(value)
        super().__init__(value)

    def _validate(self, value):
        if not value.strip():
            raise ValueError("Title cannot be empty.")
        if len(value) > 20:
            raise ValueError("Title is too long (max 20 characters).")
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


# One contact record: name, phone nr list.
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, date_str):
        self.birthday = Birthday(date_str)

    # Add Phone instance into phones list
    def add_phone(self, phone):
        if self.find_phone(phone):
            raise CustomValueError(f"Phone number {phone} already exists for the contact.")
        phone_to_add = Phone(phone)   # Validate + add
        self.phones.append(phone_to_add)

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
        return f"Contact name: {self.name.value}, {'phones' if len(self.phones) > 1 else 'phone'}: {phones_str}"
    
class NoteRecord:
    def __init__(self, title, note_text=""):
        self.title = Title(title)
        self.note_text = note_text

    def validate_note_text(self, note_text):
        if not note_text.strip():
            return "Note text can not be empty"
        if len(note_text) > 100:
            return "Note text is too long (max. is 100 characters)"

    def __str__(self):
        return f"Note title: {self.title.value}, note: {self.note_text}"


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

    # Get next week birthday records
    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        '''
        Згідно з ТЗ вибираємо всіх користувачів, День народження яких припадає на наст. тиждень (з наступного понеділка до наступної неділі)
        Якщо потрібна вибірка на наст. 7 днів, то потрібно внести зміни в операндах (рядок 122) 
        '''

        # Next Monday 
        days_till_monday = (7 - today.weekday()) % 7 or 7
        next_monday = today + timedelta(days=days_till_monday)
        next_sunday = next_monday + timedelta(days=6)

        upcoming_birthdays = defaultdict(list)

        for contact in self.data.values():
            if contact.birthday:
                birthday_this_year = contact.birthday.value.replace(year=today.year)

                #  Check if contact birthday falls within next week (Monday–Sunday)
                if next_monday <= birthday_this_year <= next_sunday:
                    weekday = birthday_this_year.strftime("%A")
                    upcoming_birthdays[weekday].append(contact.name.value)

        return dict(upcoming_birthdays)
    
# Notes entity class    
class Note(UserDict):
    # Add record by note title
    def add_record(self, record):
        self.data[record.title.value] = record

    # Find Record by title
    def find(self, title):
        return self.data.get(title)
