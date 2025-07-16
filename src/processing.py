from src.models import AddressBook, CustomValueError, Note, NoteRecord, Record, Title
from src.decorators import input_error
from colorama import Back, Fore, Style, init
import readline, shlex, textwrap

init(autoreset=True)


def commands_overview():
    # Define the column width for command names
    cmd_width = 20
    out = f"\n{Fore.CYAN + Style.BRIGHT}COMMANDS OVERVIEW{Style.RESET_ALL}\n\n"

    def line(cmd, desc, usage=None):
        result = f"{Fore.YELLOW}{cmd.ljust(cmd_width)}{Style.RESET_ALL} {Fore.GREEN}{desc}{Style.RESET_ALL}\n"
        if usage:
            result += f"{' ' * cmd_width} {Fore.CYAN}Usage: {usage}{Style.RESET_ALL}\n"
        return result

    out += line("note-add", "Adds a new note", 'note-add --title "note title" --text "note text"') + "\n"
    out += line("notes-all", "Shows all saved notes") + "\n"
    out += line("notes", "Shows all notes by search string", 'notes --search "search string"') + "\n" 
    out += line("note-update", "Updates note by specified id", 'note-update <note id>') + "\n"
    out += line("note-delete", "Deletes note by specified id", 'note-delete <note id>') + "\n"
    out += line("add", "Adds a contact with phone number", 'add Mykola 0660320528') + "\n"
    out += line("change", "Changes a contact's phone number", 'change John 0660320528 0660320529') + "\n"
    out += line("phone", "Shows phone(s) of a contact", 'phone John') + "\n"
    out += line("all", "Shows all contacts") + "\n"
    out += line("add-birthday", "Adds birthday to a contact", 'add-birthday Andrii 25.07.2001') + "\n"
    out += line("show-birthday", "Shows birthday of a contact", 'show-birthday John') + "\n"
    out += line("birthdays", "Shows upcoming birthdays in next defined days") + "\n"
    out += line("exit | close", "Exits the bot") + "\n"
    out += line("help", "Shows this help table") + "\n"

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

def input_with_prefill(prompt, prefill=''):
    def hook():
        readline.insert_text(prefill)
        readline.redisplay()
    readline.set_pre_input_hook(hook)
    try:
        return input(prompt)
    finally:
        readline.set_pre_input_hook()

@input_error
def add_note(args, note_instance: Note):
    title, note_text, *_ = args

    if not title or not note_text:
        raise CustomValueError('Please enter the command with note-add --title "title value" --text "note text"')

    try:
        title = Title(title).value
        note_record = NoteRecord(title)
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
def show_all_notes(note: Note, search_term: str = None):
    if not note.data:
        return "Can not find any note."
    
    COLUMN_ID_WIDTH = 20
    COLUMN_TITLE_WIDTH = 50
    COLUMN_TEXT_WIDTH = 70
    
    header = (
        f"{Fore.WHITE + Back.GREEN + Style.BRIGHT}" 
        f"{'ID':<{COLUMN_ID_WIDTH}} | {'Title':<{COLUMN_TITLE_WIDTH}} | {'Text':<{COLUMN_TEXT_WIDTH}}"
        f"{Style.RESET_ALL}"
    )

    rows = []
    search_term = search_term.lower() if search_term else None

    for idx, record in enumerate(note.data.values()):
        bg_color = Back.LIGHTYELLOW_EX  + Style.BRIGHT if idx % 2 == 0 else Back.CYAN
        color = Fore.MAGENTA  + Style.BRIGHT if idx % 2 == 0 else Fore.BLACK
        wrapped_text = textwrap.wrap(record.note_text, width=COLUMN_TEXT_WIDTH) or [""]
        text_lines_lower = [line.lower() for line in wrapped_text]

        for line_index, line in enumerate(wrapped_text):
            if line_index == 0:
                row = (
                    f"{bg_color}{color}"
                    f"{record.id_hash:<{COLUMN_ID_WIDTH}} | "
                    f"{record.title.value:<{COLUMN_TITLE_WIDTH}} | "
                    f"{line:<{COLUMN_TEXT_WIDTH}}"
                    f"{Style.RESET_ALL}"
                )
            else:
                row = (
                    f"{bg_color}{color}"
                    f"{'':<{COLUMN_ID_WIDTH}} | "
                    f"{'':<{COLUMN_TITLE_WIDTH}} | "
                    f"{line:<{COLUMN_TEXT_WIDTH}}"
                    f"{Style.RESET_ALL}"
                )
            if not search_term or search_term in record.title.value.lower() or any(search_term in line for line in text_lines_lower):
                rows.append(row)

    return f"\n{header}\n" + "\n" . join(rows) + "\n"


@input_error
def update_note(args, note_instance: Note):
    if not args:
        raise CustomValueError("You must provide a note ID, e.g., note-update <note_id>")
    
    if len(args) > 1:
        raise CustomValueError("Too much arguments. Please run with: note-update <note id>")

    id_hash = args[0]
    
    target_record = None
    if id_hash:
        for record in note_instance.data.values():
            if record.id_hash == id_hash:
                target_record = record
                break

    if not target_record:
        return f"Note not found with id {id_hash}"
    
    new_title = input_with_prefill(f"{Fore.BLUE}Edit the title: {Fore.RESET}", record.title.value.strip())
    if new_title:
        try:
            validate_title = Title(new_title).value
            target_record.title = Title(validate_title)
            print("Title updated")
        except ValueError as e:
            print(f"Title not updated: {e}")

    new_text = input_with_prefill(f"{Fore.BLUE}Edit the text: {Fore.RESET}", record.note_text.strip())

    if new_text:
        error = target_record.validate_note_text(new_text)
    if error:
        print(f"Text not updated: {error}")
    else:
        target_record.note_text = new_text
        print("Text updated.")

    return f"Note {id_hash} updated successfully."

@input_error
def delete_note(args, note_instance: Note):
    if not args:
        raise CustomValueError("You must provide a note ID, e.g., note-delete <note_id>")
    
    if len(args) > 1:
        raise CustomValueError("Too much arguments. Please run with: note-delete <note id>")

    id_hash = args[0]
    
    if id_hash:
        for title, record in list(note_instance.data.items()):
            if record.id_hash == id_hash:
                del note_instance.data[title]
                return f"Note with ID {id_hash} deleted."

    return f"No note found with ID {id_hash}."
