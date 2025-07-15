from src.models import AddressBook
from src.store import load_data, save_data
from src.processing import (
    add_birthday, birthdays, change_contact, parse_input,
    add_contact, show_all, show_birthday, show_phone
)

def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        match command:
            case "close" | "exit":
                save_data(book)
                print("Good bye!")
                break
            case "hello":
                print("How can I help you?")
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
            case _:
                print("Invalid command.")

if __name__ == "__main__":
    main()
