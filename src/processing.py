from src.models import AddressBook, CustomValueError, Record
from src.decorators import input_error

def parse_input(user_input: str):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if not record:
        raise CustomValueError(f"Contact {name} not found.")
    if not record.edit_phone(old_phone, new_phone):
        raise CustomValueError(f"{old_phone} not found for the given contact.")
    return "Phone number updated."
    
@input_error    
def show_phone(args: list, book: AddressBook):    
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}'s phones: {', '.join(p.value for p in record.phones)}"
    raise CustomValueError(f"Contact {name} not found.")
    
def show_all(book: AddressBook):
    if not book.data:
        return "Address book is empty."
    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book: AddressBook):
    name, date_str, *_ = args
    record = book.find(name)
    if not record:
        record = Record(name)
        book.add_record(record)
    record.add_birthday(date_str)
    return f"Birthday added for {name}."

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is {record.birthday}"
    elif record:
        return f"{name} has no birthday info."
    raise CustomValueError(f"Contact {name} not found.")

@input_error
def birthdays(book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No birthdays fall next week."
    result = ["Upcoming birthdays fall next week:"]
    for day, names in sorted(upcoming_birthdays.items()):
        result.append(f"{day}: {', '.join(names)}")
    return "\n".join(result)
           