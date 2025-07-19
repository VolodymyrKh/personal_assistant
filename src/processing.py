from src.models import AddressBook, CustomValueError, Name, Note, NoteRecord, Record, Title
from src.decorators import input_error
from src.store import list_backups
from colorama import Back, Fore, Style, init
import readline, shlex, textwrap
import difflib

init(autoreset=True)

# Command suggestions based on user input
COMMAND_SUGGESTIONS = {
    # Contact-related commands
    'add contact': ['add-contact', 'add'],
    'create contact': ['add-contact', 'add'],
    'new contact': ['add-contact', 'add'],
    'edit contact': ['edit-contact'],
    'change contact': ['edit-contact'],
    'update contact': ['edit-contact'],
    'search contact': ['search-contact'],
    'find contact': ['search-contact'],
    'look for contact': ['search-contact'],
    'delete contact': ['delete'],
    'remove contact': ['delete'],
    'show contacts': ['all'],
    'list contacts': ['all'],
    'display contacts': ['all'],
    'phone number': ['phone', 'add', 'change'],
    'birthday': ['add-birthday', 'show-birthday', 'birthdays'],
    'upcoming birthdays': ['birthdays'],
    
    # Note-related commands
    'add note': ['note-add'],
    'create note': ['note-add'],
    'new note': ['note-add'],
    'edit note': ['note-update'],
    'update note': ['note-update'],
    'change note': ['note-update'],
    'delete note': ['note-delete'],
    'remove note': ['note-delete'],
    'show notes': ['notes-all', 'notes'],
    'list notes': ['notes-all', 'notes'],
    'display notes': ['notes-all', 'notes'],
    'search notes': ['notes'],
    'find notes': ['notes'],
    'tag': ['note-add', 'note-update'],
    'tags': ['note-add', 'note-update'],
    
    # General commands
    'help': ['help'],
    'commands': ['help'],
    'what can you do': ['help'],
    'exit': ['close', 'exit'],
    'quit': ['close', 'exit'],
    'goodbye': ['close', 'exit'],
    'bye': ['close', 'exit']
}

def suggest_command(user_input):
    """Suggest commands based on user input"""
    user_input_lower = user_input.lower().strip()
    
    # Direct command match
    if user_input_lower in COMMAND_SUGGESTIONS:
        return COMMAND_SUGGESTIONS[user_input_lower]
    
    # Partial match
    suggestions = []
    for key, commands in COMMAND_SUGGESTIONS.items():
        if any(word in user_input_lower for word in key.split()):
            suggestions.extend(commands)
    
    # Fuzzy match using difflib
    if not suggestions:
        all_keys = list(COMMAND_SUGGESTIONS.keys())
        matches = difflib.get_close_matches(user_input_lower, all_keys, n=3, cutoff=0.6)
        for match in matches:
            suggestions.extend(COMMAND_SUGGESTIONS[match])
    
    # Remove duplicates and return unique suggestions
    return list(set(suggestions))[:5]  # Limit to 5 suggestions

def analyze_user_intent(user_input):
    """Analyze user input and suggest appropriate commands"""
    if not user_input.strip():
        return None
    
    suggestions = suggest_command(user_input)
    
    if suggestions:
        suggestion_text = f"\n{Fore.YELLOW}Did you mean one of these commands?{Style.RESET_ALL}\n"
        for i, cmd in enumerate(suggestions, 1):
            suggestion_text += f"{Fore.CYAN}{i}.{Style.RESET_ALL} {Fore.GREEN}{cmd}{Style.RESET_ALL}\n"
        suggestion_text += f"\n{Fore.BLUE}Type the command number or the full command to proceed.{Style.RESET_ALL}\n"
        return suggestion_text
    
    return None


def commands_overview():
    # Define the column width for command names
    cmd_width = 20
    out = f"\n{Fore.CYAN + Style.BRIGHT}COMMANDS OVERVIEW{Style.RESET_ALL}\n\n"

    def line(cmd, desc, usage=None):
        result = f"{Fore.YELLOW}{cmd.ljust(cmd_width)}{Style.RESET_ALL} {Fore.GREEN}{desc}{Style.RESET_ALL}\n"
        if usage:
            result += f"{' ' * cmd_width} {Fore.CYAN}Usage: {usage}{Style.RESET_ALL}\n"
        return result

    # Note commands
    out += f"{Fore.MAGENTA + Style.BRIGHT}📝 NOTE COMMANDS:{Style.RESET_ALL}\n"
    out += line("note-add", "Adds a new note with tags", 'note-add --title "title" --text "text"') + "\n"
    out += line("notes-all", "Shows all saved notes with tags")  + "\n"
    out += line("notes", "Shows all notes by search string", 'notes --search "search string"') + "\n"
    out += line("notes-tags", "Shows notes filtered by tags", 'notes-tags tag1,tag2,tag3') + "\n"
    out += line("note-update", "Updates note by specified id", 'note-update <note id>') + "\n"
    out += line("note-delete", "Deletes note by specified id", 'note-delete <note id>') + "\n\n"
    
    # Contact commands
    out += f"{Fore.MAGENTA + Style.BRIGHT}👥 CONTACT COMMANDS:{Style.RESET_ALL}\n"
    out += line("add", "Adds a contact with phone number", 'add Mykola 0660320528')  + "\n"
    out += line("add-contact", "Adds a contact with full details", 'add-contact [use following prompts]')  + "\n"
    out += line("edit-contact", "Edit a contact", 'edit-contact John')  + "\n"
    out += line("search-contact", "Search for contacts by field", 'search-contact')  + "\n"
    out += line("change", "Changes a contact's phone number", 'change John 0660320528 0660320529')  + "\n"
    out += line("phone", "Shows phone(s) of a contact", 'phone John')  + "\n"
    out += line("all", "Shows all contacts")  + "\n"
    out += line("add-birthday", "Adds birthday to a contact", 'add-birthday Andrii 25.07.2001')  + "\n"
    out += line("show-birthday", "Shows birthday of a contact", 'show-birthday John')  + "\n"
    out += line("birthdays", "Shows upcoming birthdays", 'birthdays') + "\n"
    out += line("delete", "Deletes a contact", 'delete John') + "\n\n"
    
    # System commands
    out += f"{Fore.MAGENTA + Style.BRIGHT}⚙️ SYSTEM COMMANDS:{Style.RESET_ALL}\n"
    out += line("exit | close", "Exits the bot")  + "\n"
    out += line("help", "Shows this help table")  + "\n"
    out += line("backups", "Shows available data backups") + "\n\n"
    
    # Features info
    out += f"{Fore.MAGENTA + Style.BRIGHT}✨ FEATURES:{Style.RESET_ALL}\n"
    out += f"{Fore.CYAN}•{Style.RESET_ALL} Intelligent command suggestions\n"
    out += f"{Fore.CYAN}•{Style.RESET_ALL} Tag-based note organization\n"
    out += f"{Fore.CYAN}•{Style.RESET_ALL} Advanced phone/email validation\n"
    out += f"{Fore.CYAN}•{Style.RESET_ALL} Birthday reminders\n"
    out += f"{Fore.CYAN}•{Style.RESET_ALL} Persistent data storage\n"

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
    if len(args) < 2:
        raise CustomValueError("Please provide name and phone number")
    
    # Join all args except the last one as the name
    name = " ".join(args[:-1])
    phone = args[-1]
    
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
    
    if not args:
        raise CustomValueError("Please enter the argument for the command")
    name = " ".join(args)
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
    if len(args) < 3:
        raise CustomValueError("Please provide name, old phone, and new phone")
    
    # Join all args except the last two as the name
    name = " ".join(args[:-2])
    old_phone = args[-2]
    new_phone = args[-1]
    
    record = book.find(name)
    if not record:
        raise CustomValueError(f"Contact {name} not found.")
    if not record.edit_phone(old_phone, new_phone):
        raise CustomValueError(f"{old_phone} not found for the given contact.")
    return "Phone number updated."
    
@input_error    
def show_phone(args: list, book: AddressBook):    
    if not args:
        raise CustomValueError("Please enter the argument for the command")
    name = " ".join(args)
    record = book.find(name)
    if record:
        return f"{name}'s phones: {', '.join(p.value for p in record.phones)}"
    raise CustomValueError(f"Contact {name} not found.")
    
def show_all(book: AddressBook):
    if not book.data:
        return f"{Fore.YELLOW}Address book is empty.{Style.RESET_ALL}"
    
    # Define column widths for better formatting
    COLUMN_NAME_WIDTH = 25
    COLUMN_PHONE_WIDTH = 30
    COLUMN_EMAIL_WIDTH = 35
    COLUMN_BIRTHDAY_WIDTH = 15
    COLUMN_ADDRESS_WIDTH = 40
    
    # Create colorful header
    header = (
        f"{Fore.WHITE + Back.BLUE + Style.BRIGHT}"
        f"{'Name':<{COLUMN_NAME_WIDTH}} | {'Phone(s)':<{COLUMN_PHONE_WIDTH}} | {'Email':<{COLUMN_EMAIL_WIDTH}} | {'Birthday':<{COLUMN_BIRTHDAY_WIDTH}} | {'Address':<{COLUMN_ADDRESS_WIDTH}}"
        f"{Style.RESET_ALL}"
    )
    
    rows = []
    for idx, record in enumerate(book.data.values()):
        # Alternate background colors for better readability
        bg_color = Back.LIGHTGREEN_EX if idx % 2 == 0 else Back.LIGHTBLUE_EX
        text_color = Fore.BLACK + Style.BRIGHT if idx % 2 == 0 else Fore.WHITE + Style.BRIGHT
        
        # Format phone numbers
        phones_str = "; ".join(p.value for p in record.phones) if record.phones else "No phone"
        
        # Format email
        email_str = record.email.value if record.email else "No email"
        
        # Format birthday
        birthday_str = str(record.birthday.value) if record.birthday else "No birthday"
        
        # Format address
        address_str = record.address.value if record.address else "No address"
        
        # Create the row with colorful formatting
        row = (
            f"{bg_color}{text_color}"
            f"{record.name.value:<{COLUMN_NAME_WIDTH}} | "
            f"{phones_str:<{COLUMN_PHONE_WIDTH}} | "
            f"{email_str:<{COLUMN_EMAIL_WIDTH}} | "
            f"{birthday_str:<{COLUMN_BIRTHDAY_WIDTH}} | "
            f"{address_str:<{COLUMN_ADDRESS_WIDTH}}"
            f"{Style.RESET_ALL}"
        )
        rows.append(row)
    
    # Add a summary line
    total_contacts = len(book.data)
    summary = f"\n{Fore.CYAN + Style.BRIGHT}Total contacts: {total_contacts}{Style.RESET_ALL}"
    
    return f"\n{header}\n" + "\n".join(rows) + summary

@input_error
def add_birthday(args, book: AddressBook):
    if len(args) < 2:
        raise CustomValueError("Please provide name and birthday date")
    
    # Join all args except the last one as the name
    name = " ".join(args[:-1])
    date_str = args[-1]
    
    record = book.find(name)
    if not record:
        record = Record(name)
        book.add_record(record)
    record.add_birthday(date_str)
    return f"Birthday added for {name}."

@input_error
def show_birthday(args, book: AddressBook):
    if not args:
        raise CustomValueError("Please enter the argument for the command")
    name = " ".join(args)
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
def delete_contact(args, book: AddressBook):
    if not args:
        raise CustomValueError("Please enter the argument for the command")
    name = " ".join(args)
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
    
    # Ask for tags
    tags_input = input(f"{Fore.BLUE}Enter tags (comma-separated, optional): {Fore.RESET}").strip()
    if tags_input:
        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        for tag in tags:
            record.add_tag(tag)
    
    note_instance.add_record(record)
    
    tags_str = f" with tags: {', '.join(sorted(record.tags))}" if record.tags else ""
    return f"Note with title {title} added{tags_str}."
    
    
@input_error
def show_all_notes(note: Note, search_term: str = None):
    if not note.data:
        return "Can not find any note."
    
    COLUMN_ID_WIDTH = 20
    COLUMN_TITLE_WIDTH = 40
    COLUMN_TEXT_WIDTH = 50
    COLUMN_TAGS_WIDTH = 30
    
    header = (
        f"{Fore.WHITE + Back.GREEN + Style.BRIGHT}" 
        f"{'ID':<{COLUMN_ID_WIDTH}} | {'Title':<{COLUMN_TITLE_WIDTH}} | {'Text':<{COLUMN_TEXT_WIDTH}} | {'Tags':<{COLUMN_TAGS_WIDTH}}"
        f"{Style.RESET_ALL}"
    )

    rows = []
    search_term = search_term.lower() if search_term else None

    for idx, record in enumerate(note.data.values()):
        bg_color = Back.LIGHTYELLOW_EX  + Style.BRIGHT if idx % 2 == 0 else Back.CYAN
        color = Fore.MAGENTA  + Style.BRIGHT if idx % 2 == 0 else Fore.BLACK
        wrapped_text = textwrap.wrap(record.note_text, width=COLUMN_TEXT_WIDTH) or [""]
        text_lines_lower = [line.lower() for line in wrapped_text]
        tags_str = ", ".join(sorted(record.tags)) if record.tags else ""

        for line_index, line in enumerate(wrapped_text):
            if line_index == 0:
                row = (
                    f"{bg_color}{color}"
                    f"{record.id_hash:<{COLUMN_ID_WIDTH}} | "
                    f"{record.title.value:<{COLUMN_TITLE_WIDTH}} | "
                    f"{line:<{COLUMN_TEXT_WIDTH}} | "
                    f"{tags_str:<{COLUMN_TAGS_WIDTH}}"
                    f"{Style.RESET_ALL}"
                )
            else:
                row = (
                    f"{bg_color}{color}"
                    f"{'':<{COLUMN_ID_WIDTH}} | "
                    f"{'':<{COLUMN_TITLE_WIDTH}} | "
                    f"{line:<{COLUMN_TEXT_WIDTH}} | "
                    f"{'':<{COLUMN_TAGS_WIDTH}}"
                    f"{Style.RESET_ALL}"
                )
            if not search_term or search_term in record.title.value.lower() or any(search_term in line for line in text_lines_lower) or search_term in tags_str.lower():
                rows.append(row)

    return f"\n{header}\n" + "\n" . join(rows) + "\n"

@input_error
def show_notes_by_tags(notes: Note, tags_input: str = None):
    """Show notes filtered by tags"""
    if not notes.data:
        return "No notes found."
    
    if not tags_input:
        # Show all available tags
        all_tags = notes.get_all_tags()
        if not all_tags:
            return "No tags found in any notes."
        
        tags_str = ", ".join(all_tags)
        return f"Available tags: {tags_str}\n\nUse 'notes-tags <tag1,tag2,...>' to filter notes by tags."
    
    # Parse tags
    tags = [tag.strip().lower() for tag in tags_input.split(',') if tag.strip()]
    if not tags:
        return "No valid tags provided."
    
    # Get notes by tags
    filtered_notes = notes.get_notes_by_tags(tags)
    if not filtered_notes:
        return f"No notes found with tags: {', '.join(tags)}"
    
    # Display filtered notes
    COLUMN_ID_WIDTH = 20
    COLUMN_TITLE_WIDTH = 40
    COLUMN_TEXT_WIDTH = 50
    COLUMN_TAGS_WIDTH = 30
    
    header = (
        f"{Fore.WHITE + Back.GREEN + Style.BRIGHT}" 
        f"{'ID':<{COLUMN_ID_WIDTH}} | {'Title':<{COLUMN_TITLE_WIDTH}} | {'Text':<{COLUMN_TEXT_WIDTH}} | {'Tags':<{COLUMN_TAGS_WIDTH}}"
        f"{Style.RESET_ALL}"
    )

    rows = []
    for idx, record in enumerate(filtered_notes):
        bg_color = Back.LIGHTYELLOW_EX + Style.BRIGHT if idx % 2 == 0 else Back.CYAN
        color = Fore.MAGENTA + Style.BRIGHT if idx % 2 == 0 else Fore.BLACK
        wrapped_text = textwrap.wrap(record.note_text, width=COLUMN_TEXT_WIDTH) or [""]
        tags_str = ", ".join(sorted(record.tags)) if record.tags else ""

        for line_index, line in enumerate(wrapped_text):
            if line_index == 0:
                row = (
                    f"{bg_color}{color}"
                    f"{record.id_hash:<{COLUMN_ID_WIDTH}} | "
                    f"{record.title.value:<{COLUMN_TITLE_WIDTH}} | "
                    f"{line:<{COLUMN_TEXT_WIDTH}} | "
                    f"{tags_str:<{COLUMN_TAGS_WIDTH}}"
                    f"{Style.RESET_ALL}"
                )
            else:
                row = (
                    f"{bg_color}{color}"
                    f"{'':<{COLUMN_ID_WIDTH}} | "
                    f"{'':<{COLUMN_TITLE_WIDTH}} | "
                    f"{line:<{COLUMN_TEXT_WIDTH}} | "
                    f"{'':<{COLUMN_TAGS_WIDTH}}"
                    f"{Style.RESET_ALL}"
                )
            rows.append(row)

    return f"\n{header}\n" + "\n".join(rows) + "\n"


@input_error
def update_note(args, note_instance: Note):
    if not args:
        raise CustomValueError("You must provide a note ID, e.g., note-update <note_id>")
    
    if len(args) > 1:
        raise CustomValueError("Too much arguments. Please run with: note-update <note id>")

    id_hash = args[0]
    
    target_record = note_instance.find_by_id(id_hash)

    if not target_record:
        return f"Note not found with id {id_hash}"
    
    new_title = input_with_prefill(f"{Fore.BLUE}Edit the title: {Fore.RESET}", target_record.title.value.strip())
    if new_title:
        try:
            validate_title = Title(new_title).value
            target_record.title = Title(validate_title)
            print("Title updated")
        except ValueError as e:
            print(f"Title not updated: {e}")

    new_text = input_with_prefill(f"{Fore.BLUE}Edit the text: {Fore.RESET}", target_record.note_text.strip())

    if new_text:
        error = target_record.validate_note_text(new_text)
        if error:
            print(f"Text not updated: {error}")
        else:
            target_record.note_text = new_text
            print("Text updated.")

    # Handle tags
    current_tags = ", ".join(sorted(target_record.tags)) if target_record.tags else ""
    new_tags_input = input_with_prefill(f"{Fore.BLUE}Edit tags (comma-separated): {Fore.RESET}", current_tags)
    
    if new_tags_input is not None:  # User pressed Enter without typing
        # Clear existing tags and add new ones
        target_record.tags.clear()
        if new_tags_input.strip():
            new_tags = [tag.strip() for tag in new_tags_input.split(',') if tag.strip()]
            for tag in new_tags:
                target_record.add_tag(tag)
        print("Tags updated.")

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

@input_error
def show_backups():
    """Show available backups"""
    return list_backups()
