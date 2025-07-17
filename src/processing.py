from src.models import AddressBook, CustomValueError, Name, Note, NoteRecord, Record, Title
from src.decorators import input_error
from colorama import Fore, Style, init
import shlex

init(autoreset=True)


def commands_overview():
    # Define the column width for command names
    cmd_width = 20
    out = f"\n{Fore.CYAN + Style.BRIGHT}COMMAND OVERVIEW{Style.RESET_ALL}\n\n"

    def line(cmd, desc, usage=None):
        result = f"{Fore.YELLOW}{cmd.ljust(cmd_width)}{Style.RESET_ALL} {Fore.GREEN}{desc}{Style.RESET_ALL}\n"
        if usage:
            result += f"{' ' * cmd_width} {Fore.CYAN}Usage: {usage}{Style.RESET_ALL}\n"
        return result

    out += line("note-add", "Adds a new note", 'note-add --title "title" --text "text"') + "\n"
    out += line("notes-all", "Shows all saved notes")  + "\n"
    out += line("add", "Adds a contact with phone number", 'add Mykola 0660320528')  + "\n"
    out += line("add-contact", "Adds a contact", 'add-contact [use following prompts]')  + "\n"
    out += line("edit-contact", "Edit a contact", 'edit-contact John')  + "\n"
    out += line("search-contact", "Search for contacts by rcerd field and search value", 'search-contact')  + "\n"
    out += line("change", "Changes a contact's phone number", 'change John 0660320528 0660320529')  + "\n"
    out += line("phone", "Shows phone(s) of a contact", 'phone John')  + "\n"
    out += line("all", "Shows all contacts")  + "\n"
    out += line("add-birthday", "Adds birthday to a contact", 'add-birthday Andrii 25.07.2001')  + "\n"
    out += line("show-birthday", "Shows birthday of a contact", 'show-birthday John')  + "\n"
    out += line("birthdays", "Shows upcoming birthdays in next defined days")  + "\n"
    out += line("exit | close", "Exits the bot")  + "\n"
    out += line("help | ?", "Shows this help table")  + "\n"

    return out


def parse_input(user_input: str):
    try:
        parts = shlex.split(user_input)
    except ValueError as e:
        raise ValueError("Invalid input format. Check your quotes.") from e

    if not parts:
        return "", []

    cmd = parts[0].strip().lower()
    args = parts[1:]
    return cmd, args


def parse_named_args(args: list[str]) -> dict:
    result = {}
    i = 0
    while i < len(args):
        if args[i].startswith("--"):
            key = args[i].lstrip("-")
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                result[key] = args[i + 1]
                i += 2
            else:
                result[key] = ""
                i += 1
        else:
            i += 1
    return result


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
def add_contact_complete(book: AddressBook):
    name_msg = "Please enter name (required): "
    name_input = input(name_msg.rjust(len(name_msg) + 4)).strip()

    if not name_input:
        raise CustomValueError(f"To create new contact 'name' is required.")
    
    record = book.find(name_input)
    if record:
        return f'Contact {name_input} already exists.'
    
    record = Record(name_input)
    book.add_record(record)
    
    phone_msg = "Please enter phone (optional), or press 'Enter' to skip: "
    phone_input = input(phone_msg.rjust(len(phone_msg) + 4)).strip()

    if phone_input:
        record.add_phone(phone_input)

    email_msg = "Please enter email (optional), or press 'Enter' to skip: "
    email_input = input(email_msg.rjust(len(email_msg) + 4)).strip()

    if email_input:
        record.add_email(email_input)

    birthday_msg = "Please enter birthday (optional), or press 'Enter' to skip: "
    birthday_input = input(birthday_msg.rjust(len(birthday_msg) + 4)).strip()

    if birthday_input:
        record.add_birthday(birthday_input)

    address_msg = "Please enter address (optional), or press 'Enter' to skip: "
    address_input = input(address_msg.rjust(len(address_msg) + 4)).strip()

    if address_input:
        record.add_address(address_input)
        
    return "Contact added."

@input_error
def edit_contact_complete(args, book: AddressBook):
    
    name = args[0]
    record = book.find(name)

    if record:
        new_name_msg = "Please specify new name, use 'quotes' if name separated by space, or press 'Enter' to skip: "
        new_name_input = input(new_name_msg.rjust(len(new_name_msg) + 4)).strip()
        if new_name_input:
            book.update_record_name(name, new_name_input)

        new_phone_msg = "Please enter one phone to add <new_phone> or two phones to replace <old_phone> <new_phone>, or press 'Enter' to skip: "
        new_phone_input = input(new_phone_msg.rjust(len(new_phone_msg) + 4)).strip()
        if new_phone_input:
            phones = shlex.split(new_phone_input)
            if len(phones) == 1:
                record.add_phone(phones[0])
            else:
                old_phone, new_phone, *_ = phones
                record.edit_phone(old_phone, new_phone)

        new_email_msg = "Please enter email, or press 'Enter' to skip: "
        new_email_input = input(new_email_msg.rjust(len(new_email_msg) + 4)).strip()
        if new_email_input:
            record.add_email(new_email_input)

        new_birthday_msg = "Please enter birthday, or press 'Enter' to skip: "
        new_birthday_input = input(new_birthday_msg.rjust(len(new_birthday_msg) + 4)).strip()
        if new_birthday_input:
            record.add_birthday(new_birthday_input)

        new_address_msg = "Please enter address, or press 'Enter' to skip: "
        new_address_input = input(new_address_msg.rjust(len(new_address_msg) + 4)).strip()
        if new_address_input:
            record.add_address(new_address_input)        
        return "Contact updated."
    
    raise CustomValueError(f"Contact {name} not found.")

@input_error
def search_contact_by(book: AddressBook):
    search_msg = "Specify one search field 'name/email/phone' and the value to search for: "
    search_input = shlex.split(input(search_msg.rjust(len(search_msg) + 4)).strip())

    search_field, search_value, *_ = search_input
    filtered_records = book.search_contacts(search_field, search_value)

    if not filtered_records:
        return "No matches found."
    return "\n".join(str(record) for record in filtered_records)
    

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
    birthday_msg = "Please specify days in advance to select upcoming birthdays: "
    birthday_input = int(input(birthday_msg.rjust(len(birthday_msg) + 4)).strip())

    upcoming_birthdays = book.get_upcoming_birthdays(birthday_input)
    if not upcoming_birthdays:
        return "No birthdays fall next week."
    result = ["Upcoming birthdays fall next week:"]
    for name, contact in sorted(upcoming_birthdays.items()):
        result.append(f"{name}: {contact.birthday.value}")
    return "\n".join(result)

@input_error
def add_note(args, note_instance: Note):
    title, note_text, *_ = args
    note_record = NoteRecord(title)

    try:
        title = Title(title).value
        note_record.validate_note_text(note_text)
        record = note_instance.find(title)
    except ValueError as e:
        return f"Validation error: {e}"
    
    if note_instance.find(title):
        return f"Note with title {title} already exists."

    record = NoteRecord(title, note_text)
    note_instance.add_record(record)
    
    return f"Note with title {title} added."
    
    
@input_error
def show_all_notes(note: Note):
    if not note.data:
        return "Can not find any note."
    return "\n\n".join(str(record) for record in note.data.values())
           