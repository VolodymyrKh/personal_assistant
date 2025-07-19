# Personal Assistant Bot

A comprehensive personal assistant system for managing contacts and notes with intelligent features.

## Features

### 📝 Contact Management

- **Add contacts** with names, addresses, phone numbers, emails, and birthdays
- **Search contacts** by various fields (name, email, phone, address, birthday)
- **Edit and delete** contacts with confirmation
- **Birthday reminders** - find contacts with upcoming birthdays
- **Advanced validation** for phone numbers (supports international formats) and email addresses

### 📋 Note Management

- **Create notes** with titles and text content
- **Tag system** - organize notes with custom tags
- **Search notes** by text content or tags
- **Edit and delete** notes
- **Tag-based filtering** and organization

### 🤖 Intelligent Features

- **Natural language understanding** - the bot can understand commands like "add a contact" or "show my notes"
- **Command suggestions** - when you type something unclear, the bot suggests relevant commands
- **Smart validation** with helpful error messages

### 💾 Data Management

- **Persistent storage** - all data is saved to disk
- **Automatic backups** - data is backed up before each save
- **Backup management** - view and manage your data backups
- **Robust error handling** - automatic recovery from corrupted files

## Installation

```bash
git clone https://github.com/VolodymyrKh/personal_assistant.git
cd personal_assistant
python -m venv .venv
```

### On Ubuntu or Windows WSL:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### On Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Usage

### Basic Commands

- `help` - Show all available commands
- `add-contact` - Add a new contact (interactive)
- `edit-contact <name>` - Edit an existing contact
- `search-contact` - Search for contacts
- `all` - Show all contacts
- `birthdays` - Show upcoming birthdays

### Note Commands

- `note-add --title "Title" --text "Content"` - Add a new note with tags
- `notes-all` - Show all notes
- `notes --search "search term"` - Search notes by content
- `notes-tags tag1,tag2` - Show notes filtered by tags
- `note-update <id>` - Edit a note
- `note-delete <id>` - Delete a note

### System Commands

- `backups` - Show available data backups
- `exit` or `close` - Exit the application

### Natural Language Examples

Try these natural language commands:

- "add a contact"
- "show my notes"
- "search for contacts"
- "edit a note"
- "show birthdays"

## Data Storage

- Contacts are stored in `addressbook.pkl`
- Notes are stored in `notes.pkl`
- Backups are automatically created in the `backups/` directory
- All data persists between sessions

## Requirements

- Python 3.7+
- colorama==0.4.6

## Contributing

Feel free to submit issues and enhancement requests!
