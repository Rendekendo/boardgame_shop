from getpass import getpass
from database import Database
from mysql.connector import connect
import hashlib
from decimal import Decimal
import re


def check_credentials(username, password):
    try:
        connect(host="localhost",
                user=username,
                password=password,
                database="boardgame_shop")
        return True

    except (Exception):
        return False


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_name(word):
    chars = "qwertyuiopasdfghjklzxcvbnmåöäéQWERTYUIOPASDFGHJKLZXCVBNMÅÖÄÉ\'-"
    for char in word:
        if char not in chars:
            return False
    return True


def hash_pwd(string):
    hash_object = hashlib.sha256(string.encode())
    hex_digest = hash_object.hexdigest()
    return hex_digest


def search_games(db, user_id):
    while True:
        print("""
    == Search ==
    1) by designer (starts with)
    2) by title (whole word)
    3) back to main menu
            """)

        choice = input('Type in your choice: ')
        valid_input = ['1', '2', '3']
        if choice not in valid_input or choice == '':
            print('invalid input try again')

        match choice:
            case '1':
                while True:
                    query = input('Designer starts with: ')
                    if query != '':
                        break
                    else:
                        print('input mustn\'t be empty')
                search(db, user_id, 'designer', query)
            case '2':
                while True:
                    query = input('Title word: ')
                    if query != '':
                        break
                    else:
                        print('input mustn\'t be empty')
                search(db, user_id, 'title', query)
            case '3':
                return


def search(db, user_id, search_type, query):
    offset = 0
    while True:
        result, count = db.search(query, offset, search_type)
        if result:
            print_result = format_db_return(result)
            x = '== Results(showing'
            print(x, f'{offset + 1} - {offset + 3} of {count}) ==')
            for game in print_result:
                print(game)
        else:
            print(f'No games found with {search_type}: {query}')
            return

        print('\nOptions: enter Game ID to add to cart,'
              ' \'n\' for next, ENTER to return.\n')

        choice = input('> ')
        if choice == 'n':
            if count > offset + 3:
                offset += 3
            else:
                print('No more results')
        elif choice == '':
            return
        else:
            valid_input = [result[x][0] for x in range(len(result))]
            if choice not in valid_input:
                print('invalid input try again')
            else:
                quantity = input('Quantity: ')
                db.add_to_cart(user_id, choice, quantity)


def format_db_return(lst):
    result = []
    for game_id, title, designer, unit_price in lst:
        price = str(unit_price)

        result.append(f'ID {game_id}: {title} by {designer} ${price}')

    return result


def login(db):
    valid_credentials = False

    while not valid_credentials:
        while True:
            email = input('Enter Email: ')
            if is_valid_email(email):
                email = email.lower()
                break
            else:
                print('Invalid Input')

        while True:
            password = hash_pwd(getpass('Enter Password: '))
            if password != '':
                break
            else:
                print('Invalid Input')

        if db.login(email, password):
            valid_credentials = True
        else:
            print('Invalid Credentials, try again')

    member_menu(db, email)


def register(db):
    while True:
        first_name = input('Enter first name: ')
        if is_name(first_name) and first_name != '' and len(first_name) <= 50:
            break
        else:
            print('name must consist of only letters try again \n')

    while True:
        last_name = input('Enter last name: ')
        if is_name(last_name) and last_name != '' and len(first_name) <= 50:
            break
        else:
            print('name must consist of only letters try again \n')

    while True:
        street = input('Enter street: ')
        if street != '' and len(first_name) <= 80:
            break
        else:
            print('street is required')

    while True:
        city = input('Enter city: ')
        if city != '' and len(first_name) <= 40:
            break
        else:
            print('city is required')

    while True:
        postal_code = input('Enter postal code: ')
        if postal_code != '' and len(first_name) <= 10:
            break
        else:
            print('postal code is required')

    phone = input('Enter phone (optional): ')
    if phone == '':
        phone = None

    while True:
        email = input('Enter email: ')
        if is_valid_email(email) and db.check_unique_email(email):
            if len(first_name) <= 80:
                email = email.lower()
                break
        else:
            print('Invalid email, try again \n')

    while True:
        password = getpass('Enter password (hidden): ')
        if password != '' and len(password) >= 8:
            password = hash_pwd(password)
            break
        else:
            print('password is required\n')

    db.register(first_name,
                last_name,
                street,
                city,
                postal_code,
                phone,
                email,
                password)

    member_menu(db, email)


def member_menu(db, email):
    user_id = db.get_id(email)

    while True:
        print("""
    ********************************************
    *** Welcome to the Online Boardgame Shop ***
    ********************************************
    1) Browse by genre
    2) Search by designer/title
    3) View cart
    4) Checkout
    5) Log out
            """)
        print('welcome user', email, user_id)

        choice = input('Type in your choice: ')
        valid_input = ['1', '2', '3', '4', '5']
        if choice not in valid_input or choice == '':
            print('invalid input try again')

        match choice:
            case '1':
                pass
            case '2':
                search_games(db, user_id)
            case '3':
                pass
            case '4':
                pass
            case '5':
                break


def main():
    valid_connection = False
    username = None
    password = None

    while not valid_connection:
        username = input('Enter your Database username: ')
        password = getpass('Enter your Database password: ')
        if check_credentials(username, password):
            valid_connection = True
        else:
            print('Connection to the SQL server failed.'
                  ' Please make sure your credentials '
                  'are correct or mySQL server is running')

    db = Database(username, password)
    while True:
        print("""
    ********************************************
    *** Welcome to the Online Boardgame Shop ***
    ********************************************
    1) User Login
    2) New Member Registration
    q) Exit
            """)

        choice = input('Type in your choice: ')
        valid_input = ['1', '2', 'q']
        if choice not in valid_input or choice == '':
            print('invalid input try again')

        match choice:
            case '1':
                login(db)
            case '2':
                register(db)
            case 'q':
                break


main()
