import pickle
from collections import UserDict
from datetime import datetime, timedelta

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if len(value) == 10 and value.isdigit():
            self.__value = value
        else:
            raise ValueError('Invalid phone number')

class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError:
            raise ValueError("Incorrect format, Required format: DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if str(p) == old_phone:
                p.value = new_phone

    def find_phone(self, phone):
        for p in self.phones:
            if str(p) == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(p) for p in self.phones)}"

class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record  # Додавання запису в адресну книгу.

    def find(self, name):
        return self.data.get(name)  # Пошук запису за ім'ям.

    def delete(self, name):
        if name in self.data:
            del self.data[name]  # Видалення запису з адресної книги.

    @staticmethod
    def find_next_weekday(d, weekday):
        """
        Функція для знаходження наступного заданого дня тижня після заданої дати.
        d: datetime.date - початкова дата.
        weekday: int - день тижня від 0 (понеділок) до 6 (неділя).
        """
        days_ahead = weekday - d.weekday()  # Різниця між поточним днем тижня та бажаним днем тижня.
        if days_ahead <= 0:  # Якщо день народження вже минув у цьому тижні.
            days_ahead += 7
        return d + timedelta(days_ahead)  # Повернення дати наступного заданого дня тижня.

    def get_upcoming_birthdays(self, days=7) -> str:
        today = datetime.today().date()  # Поточна дата.
        upcoming_birthdays = []

        for user in self.data.values():
            if user.birthday is None:
                continue
            birthday_this_year = user.birthday.date.replace(year=today.year)  # Дата народження в поточному році.

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(
                    year=today.year + 1)  # Дата народження в наступному році.

            if 0 <= (birthday_this_year - today).days <= days:
                if birthday_this_year.weekday() >= 5:  # субота або неділя
                    birthday_this_year = self.find_next_weekday(
                        birthday_this_year, 0
                    )  # Понеділок

                congratulation_date_str = birthday_this_year.strftime("%Y.%m.%d")
                weekday_str = birthday_this_year.strftime("%A")
                upcoming_birthdays.append(
                    f"{user.name.value}'s birthday is on {weekday_str}."
                )

        if not upcoming_birthdays:
            return "There are no upcoming birthdays."

        return '\n'.join(upcoming_birthdays)

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "KeyError"
        except ValueError:
            return "ValueError"
        except IndexError:
            return "IndexError"

    return wrapper

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

def change_contact(args, book: AddressBook):
    if len(args) != 3:
        raise ValueError("Invalid number of arguments. Format: change <name> <old_phone> <new_phone>")
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        if record.find_phone(old_phone):
            record.edit_phone(old_phone, new_phone)
            return "Phone number updated."
        else:
            return "Old phone number not found for the contact."
    else:
        return "Contact not found."

@input_error
def show_phone(args, book: AddressBook):
    if len(args) != 1:
        raise ValueError
    name = args[0]
    record = book.find(name)
    if record:
        return str(record)
    else:
        return "Contact not found."

@input_error
def show_all(book: AddressBook):
    if not book:
        return "No contacts found."
    else:
        return "\n".join([str(record) for record in book.values()])

#@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    message = "Birthday added."
    if record:
        record.add_birthday(birthday)
    else:
        message = "Contact not found."
    return message

@input_error
def show_birthday(args, book: AddressBook):
    if len(args) != 1:
        raise ValueError
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday: {record.birthday.date.strftime('%d.%m.%Y')}"
    else:
        return "No birthday found for the contact."


def birthdays(book):
    return book.get_upcoming_birthdays()


def parse_input(user_input):
    parts = user_input.split(maxsplit=3)
    command = parts[0].lower()
    args = parts[1:]
    return command, args

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)  # Збереження даних перед виходом з програми
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()