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
                while True:
                    quantity = input('Quantity: ')
                    try:
                        quantity = int(quantity)
                        if 0 < choice < 2147483647:
                            break
                        else:
                            print('quantity must be a positive integer')
                    except (Exception):
                        print('quantity must be an integer')
                db.add_to_cart(user_id, choice, quantity)


def format_db_return(lst):
    result = []
    for game_id, title, designer, unit_price in lst:
        price = str(unit_price)

        result.append(f'ID {game_id}: {title} by {designer} ${price}')

    return result


def view_cart(db, user_id):
    cart = db.get_cart(user_id)
    formated_result = format_cart(cart)

    for entry in formated_result:
        print(entry)


def format_cart(lst):
    game_id = 'Game ID'
    title = 'Title'
    unit_price = '$'
    quantity = 'Qty'
    total = 'Total'
    cart_total = 0

    result = []
    result.append(f'\n{game_id:<10}{title:<50}{unit_price:>10}'
                  f'{quantity:>3}{total:>10}')
    result.append('-----------------------------------------'
                  '------------------------------------------')
    for game_id, title, unit_price, quantity in lst:
        unit_price = float(unit_price)
        total = unit_price * quantity
        cart_total += total
        total = f'{total:.2f}'

        if len(title) >= 48:
            title = title[:48] + '..'
        result.append(f'{game_id:<10}{title:<50}{'$' + str(unit_price):<10}'
                      f'{quantity:>3}{'$' + str(total):>10}')

    result.append('-----------------------------------------'
                  '------------------------------------------\n')

    result.append(f'Total = ${cart_total:.2f}')
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
            password = hash_pwd(getpass('Enter Password (hidden): '))
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
        print('Welcome user', email, user_id)

        choice = input('Type in your choice: ')
        valid_input = ['1', '2', '3', '4', '5']
        if choice not in valid_input or choice == '':
            print('invalid input try again')

        match choice:
            case '1':
                init_browse_by_genre(db, user_id, email)
            case '2':
                search_games(db, user_id)
            case '3':
                view_cart(db, user_id)
            case '4':
                pass
            case '5':
                break


def init_browse_by_genre(db, user_id, email):
    # get genres
    genres = db.get_genres()
    # convert tuple to list so it can be sorted
    genres_list = [genre for genre in genres]
    genres_list.sort()

    lst_of_str_genres = []
    strng = '== GENRES == '
    n = 0
    for i in genres_list:
        n += 1
        genre = str(i).strip('()')
        genre = str(genre).strip(',')
        genre = str(genre).strip("'")
        lst_of_str_genres.append(genre)
        strng += f'\n{n}) {genre}'
    print(strng)
    choice = ''
    valid_nr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    while choice not in valid_nr:
        choice = input('Pick a number (or ENTER to return):')
        match choice:
            case '1':
                genre = lst_of_str_genres[0]
            case '2':
                genre = lst_of_str_genres[1]
            case '3':
                genre = lst_of_str_genres[2]
            case '4':
                genre = lst_of_str_genres[3]
            case '5':
                genre = lst_of_str_genres[4]
            case '6':
                genre = lst_of_str_genres[5]
            case '7':
                genre = lst_of_str_genres[6]
            case '8':
                genre = lst_of_str_genres[7]
            case '9':
                genre = lst_of_str_genres[8]
            case '10':
                genre = lst_of_str_genres[9]
            case _:
                print('Invalid input. Please enter a number between 1 and 10.')
                choice = input('Pick a number (or ENTER to return):')

    browse_by_genre(db, user_id, email, genre)


def browse_by_genre(db, user_id, email, genre, sec_game_nr=0, page=0):
    print('------------------------------------'
          '------------------------------------')
    # -- get data for pages --
    sum_of_games = db.get_page_count(genre)
    page += 1
    if page < sum_of_games[0]:
        page_str1 = f'== {genre}: showing page {page}'
        page_str2 = f'-{page+1} of {sum_of_games[0]} =='
        page_str = page_str1 + page_str2
        print(page_str)
    elif page <= sum_of_games[0]:
        print(f'== {genre}: showing page {page} of {sum_of_games[0]} ==')
    else:
        print('All available games have been displayed. '
              'Returning to chosing the genre.')
        init_browse_by_genre(db, user_id, email)
    page += 1

    # -- get actual game data --
    # sec(ond)_game_nr: which number to use with OFFSET in query
    rows = db.get_game_data_browse(genre, sec_game_nr)
    for tuples in rows:
        str_of_elements = ''
        for element in tuples:
            element = str(element)
            str_of_elements += element + ' '
        print(str_of_elements)
    # first two elements have been printed, now user choses what happens

    answer = input("Enter GameID to add to cart, 'n' "
                   "to see next games or ENTER to return. ")

    # user chose to add game to cart
    if answer[:2] == 'BG':
        # check if ID is valid
        status = db.valid_game_id(answer)
        # -- input gameID is valid --
        if status != ():
            quantity = input('Quantity: ')
            # verifying quantity is valid
            while quantity == '0':
                print('You have to chose at least one game to add '
                      'it to the cart. Please try again.')
                quantity = input('Quantity: ')
            for i in range(len(quantity)):
                valid_nrs = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
                while quantity[i] not in valid_nrs:
                    print('Invalid Input. Please try again.')
                    quantity = input('Quantity: ')
            # add to cart
            db.add_to_cart(user_id, answer, quantity)
            print('Successfully added to cart.')
            print('Returning to member menu.')
            browse_by_genre(db, user_id, email, genre, sec_game_nr, page)
        else:
            print('This gameID does not exist. Please try again.')
            browse_by_genre(db, user_id, email, genre, sec_game_nr, page)

    elif answer == 'n':
        sec_game_nr += 2
        browse_by_genre(db, user_id, email, genre, sec_game_nr, page)

    elif answer == '':
        member_menu(db, email)

    else:
        print('Invalid Input. Try again.')
        browse_by_genre(db, user_id, email, genre)


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
                db.connection.close()
                break


main()
