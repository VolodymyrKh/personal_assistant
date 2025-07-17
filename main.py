from src.models import AddressBook
from src.store import load_address_book, load_notes_data, save_data, save_notes_data
from src.processing import (
    add_birthday, add_contact_complete, birthdays, change_contact, edit_contact_complete, parse_input, parse_named_args,
    add_contact, search_contact_by, show_all, show_birthday, show_phone,
    add_note, show_all_notes, delete_note, update_note, commands_overview
)

def main():
    book = load_address_book()
    notes = load_notes_data()

    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        match command:
            case "close" | "exit":
                save_data(book)
                save_notes_data(notes)
                print("Good bye!")
                break
            case "hello":
                print("How can I help you?")
            case "help":
                print(commands_overview())
            case "add-contact":
                print(add_contact_complete(book))
            case "edit-contact":
                print(edit_contact_complete(args, book))
            case "search-contact":
                print(search_contact_by(book))    
            case "add":
                print(add_contact(args, book))
            case "change":
                print(change_contact(args, book))
            case "phone":
                print(show_phone(args, book))
            case "all":
                print(show_all(book))
            case "add-birthday":
                print(add_birthday(args, book))
            case "show-birthday":
                print(show_birthday(args, book))
            case "birthdays":
                print(birthdays(book))   
            case "note-add":
                parts = parse_named_args(args)
                title = parts.get('title')
                text = parts.get('text')
                print(add_note([title, text], notes))
            case "notes-all":
                print(show_all_notes(notes))
            case "notes":
                parts = parse_named_args(args)
                search_str = parts.get('search')
                print(show_all_notes(notes, search_str))
            case 'note-update':
                print(update_note(args, notes))
            case 'note-delete':
                print(delete_note(args, notes))
            case _:
                print("Invalid command.")

if __name__ == "__main__":
    main()
