from src.models import AddressBook, CustomValueError, Note, NoteRecord, Record, Title
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
    out += line("change", "Changes a contact's phone number", 'change John 0660320528 0660320529')  + "\n"
    out += line("delete", "Deletes a contact", 'delete John')  + "\n"
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


@input_error
def delete_contact(args, book: AddressBook):
    if not args:
        raise IndexError
    name = args[0]
    if not book.find(name):
        raise CustomValueError(f"Contact {name} not found.")
    
    # Запит підтвердження
    while True:
        confirmation = input(f"Are you sure you want to delete contact '{name}'? (y/n): ").strip().lower()
        if confirmation == 'y':
            book.delete(name)
            return f"Contact {name} deleted successfully."
        elif confirmation == 'n':
            return f"Deletion cancelled. Contact {name} was not deleted."
        else:
            print("Please enter 'y' for yes or 'n' for no.")