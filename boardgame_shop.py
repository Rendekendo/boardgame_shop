from getpass import getpass
from database import Database
from mysql.connector import connect
import hashlib
from decimal import Decimal  # needed to parse database data
import re
from datetime import datetime, timedelta


def check_credentials(username, password):
    try:
        connect(host="localhost",
                user=username,
                password=password,
                database="boardgame_shop")
        return True

    except Exception:  # wrong password or server not running
        return False


def is_valid_email(email):
    # use regex to check if an email adress is valid
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # return true if its valid
    return re.match(pattern, email) is not None


def is_name(word):
    # check if name contains numbers
    chars = '0123456789'
    for char in word:
        if char in chars:
            return False
    return True


def hash_pwd(string):
    # hash encoded string with sha256
    hash_object = hashlib.sha256(string.encode())

    # return hex_digest i.e. string of characters in hex
    hex_digest = hash_object.hexdigest()
    return hex_digest


def search_games(db, user_id):
    # menu loop
    while True:
        print("""
    == Search ==
    1) by designer (starts with)
    2) by title (whole word)
    3) back to main menu
            """)

        choice = input('Type in your choice: ')  # get input
        valid_input = ['1', '2', '3']
        if choice not in valid_input or choice == '':  # validate input
            print('invalid input try again')

        match choice:
            case '1':
                # get user input for by designer search
                while True:
                    query = input('Designer starts with: ')
                    if query != '':
                        break
                    else:
                        print('input mustn\'t be empty')

                # search with the query
                search(db, user_id, 'designer', query)
            case '2':
                # get user input for by title search
                while True:
                    query = input('Title word: ')
                    if query != '':
                        break
                    else:
                        print('input mustn\'t be empty')

                # search with the query
                search(db, user_id, 'title', query)
            case '3':
                return


def search(db, user_id, search_type, query):
    offset = 0

    while True:
        # get search results and count of results using the db method
        result, count = db.search(query, offset, search_type)

        if result:  # games found
            # format results
            print_result = format_db_return(result)

            # print page information
            x = '== Results(showing'
            print(x, f'{offset + 1} - {offset + 3} of {count}) ==')

            # print games
            for game in print_result:
                print(game)

        else:  # no games found
            print(f'No games found with {search_type}: {query}')
            return

        # print options
        print('\nOptions: enter Game ID to add to cart,'
              ' \'n\' for next, ENTER to return.\n')

        # get user input
        choice = input('> ')
        if choice == 'n':  # show next page
            if count > offset + 3:  # if not on last page
                offset += 3

            else:  # last page
                print('No more results')

        elif choice == '':  # back to main menu
            return

        else:  # user typing in a game id i.e. buying a game

            # get a list of valid ids from result
            valid_input = [result[x][0] for x in range(len(result))]

            if choice not in valid_input:
                print('invalid input try again')

            else:  # choice in valid_input
                while True:
                    # get quantity input from user
                    quantity = input('Quantity: ')

                    # check if quantity is valid
                    try:
                        quantity = int(quantity)
                        if 0 < quantity < 2147483647:
                            break
                        else:
                            print('quantity must be a positive integer')
                    except (ValueError):
                        print('quantity must be an integer')

                # add game to cart
                db.add_to_cart(user_id, choice, quantity)


def format_db_return(lst):
    # formats data from database to a list of strings
    result = []
    for game_id, title, designer, unit_price in lst:
        price = str(unit_price)  # convert decimal object to string

        result.append(f'ID {game_id}: {title} by {designer} ${price}')

    return result


def view_cart(db, user_id):
    # display user's cart
    cart = db.get_cart(user_id)

    if cart == []:  # empty cart
        print('Empty cart')

    else:  # not empty cart
        # format the result
        formated_result, cart_return = format_cart(cart)

        for entry in formated_result:
            print(entry)

        return cart_return  # [game_id, quantity, line_total]


def format_cart(lst):
    game_id = 'Game ID'
    title = 'Title'
    unit_price = '$'
    quantity = 'Qty'
    total = 'Total'
    cart_total = 0

    # formats data into a list of strings
    result = []
    cart_return = []
    result.append(f'\n{game_id:<10}{title:<50}{unit_price:>10}'
                  f'{quantity:>3}{total:>10}')
    result.append('-----------------------------------------'
                  '------------------------------------------')

    # game information
    for game_id, title, unit_price, quantity in lst:
        unit_price = float(unit_price)
        total = unit_price * quantity
        cart_total += total
        total = f'{total:.2f}'

        # truncate string if title too long
        """if len(title) >= 48:
            title = title[:48] + '..'
        result.append(f'{game_id:<10}{title:<50}{'$' + str(unit_price):<10}'
                      f'{quantity:>3}{'$' + str(total):>10}')
        cart_return.append([game_id, quantity, total])"""  #  .......................................................

    result.append('-----------------------------------------'
                  '------------------------------------------\n')

    # append total cart value
    result.append(f'Total = ${cart_total:.2f}')
    return result, cart_return


def login(db):
    # let's user login provided with correct credentials
    valid_credentials = False

    while not valid_credentials:
        # get email
        while True:
            email = input('Enter Email: ')
            if is_valid_email(email):
                email = email.lower()
                break
            else:
                print('Invalid Input')

        # get password
        while True:
            password = hash_pwd(getpass('Enter Password (hidden): '))
            if password != '':
                break
            else:
                print('Invalid Input')

        # user db method to check if credentials are correct
        if db.login(email, password):
            valid_credentials = True

        # invalid credentials
        else:
            print('Invalid Credentials, try again')

    # send user to member menu
    member_menu(db, email)


def register(db):
    # get first name
    while True:
        first_name = input('Enter first name: ')
        if is_name(first_name) and first_name != '' and len(first_name) <= 50:
            break
        else:
            print('name must consist of only letters try again \n')

    # get last name
    while True:
        last_name = input('Enter last name: ')
        if is_name(last_name) and last_name != '' and len(first_name) <= 50:
            break
        else:
            print('name must consist of only letters try again \n')

    # get street
    while True:
        street = input('Enter street: ')
        if street != '' and len(first_name) <= 80:
            break
        else:
            print('street is required')

    # get city
    while True:
        city = input('Enter city: ')
        if city != '' and len(first_name) <= 40:
            break
        else:
            print('city is required')

    # get postal_code
    while True:
        postal_code = input('Enter postal code: ')
        if postal_code != '' and len(first_name) <= 10:
            break
        else:
            print('postal code is required')

    # get phone (optional)
    phone = input('Enter phone (optional): ')
    # if phone not entered: set phone to None
    if phone == '':
        phone = None

    # get email
    while True:
        email = input('Enter email: ')
        if is_valid_email(email) and db.check_unique_email(email):
            if len(first_name) <= 80:
                email = email.lower()
                break
        else:
            print('Invalid email, try again \n')

    # get password
    while True:
        password = getpass('Enter password (hidden): ')
        if password != '' and len(password) >= 8:
            # hash the password
            password = hash_pwd(password)
            break
        else:
            print('password is required\n')

    # send data to db
    db.register(first_name,
                last_name,
                street,
                city,
                postal_code,
                phone,
                email,
                password)

    # send user to member menu
    member_menu(db, email)


def member_menu(db, email):
    # get user id with email
    user_id = db.get_id(email)

    # menu loop
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

        # menu options
        match choice:
            case '1':
                init_browse_by_genre(db, user_id, email)
            case '2':
                search_games(db, user_id)
            case '3':
                view_cart(db, user_id)
            case '4':
                checkout(db, user_id)
            case '5':
                break


def init_browse_by_genre(db, user_id, email):
    # get genres
    genres = db.get_genres()
    # convert tuple to list so it can be sorted
    genres_list = [genre for genre in genres]
    genres_list.sort()

    # printing the genre choices
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

    # prompting the user to chose which genre they want to view
    choice = ''
    game_nr = len(lst_of_str_genres)
    choice = input(f'Pick a number 1-{game_nr} (or ENTER to return):')
    # if user presses ENTER return to user menu
    if choice == '':
        member_menu(db, email)
    else:
        # check the input for validity
        valid_input = '0123456789'
        while choice not in valid_input or not 0 < int(choice) <= game_nr:
            choice = input(f'Pick a number 1-{game_nr} (or ENTER to return):')
            if choice == '':
                member_menu(db, email)
        choice = int(choice)
        # assign the genre based on the users input
        genre = lst_of_str_genres[choice-1]

    browse_by_genre(db, user_id, email, genre)


def browse_by_genre(db, user_id, email, genre, sec_game_nr=0, page=0):
    print('------------------------------------'
          '------------------------------------')
    # -- get data for pages --
    sum_of_games = db.get_page_count(genre)
    page += 1
    # print 2 games
    if page < sum_of_games[0]:
        page_str1 = f'== {genre}: showing page {page}'
        page_str2 = f'-{page+1} of {sum_of_games[0]} =='
        page_str = page_str1 + page_str2
        print(page_str)
    # print 1 game if on last page
    elif page <= sum_of_games[0]:
        print(f'== {genre}: showing page {page} of {sum_of_games[0]} ==')
    # returning to the genre choice page if all games have been displayed
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
            valid_nrs = '0123456789'
            while quantity not in valid_nrs:
                print('Invalid Input. Please try again.')
                quantity = input('Quantity: ')
            # add to cart
            db.add_to_cart(user_id, answer, quantity)
            print('Successfully added to cart.')
            browse_by_genre(db, user_id, email, genre, sec_game_nr, page)
        else:
            print('This gameID does not exist. Please try again.')
            browse_by_genre(db, user_id, email, genre, sec_game_nr, page)

    elif answer == 'n':  # go to next page
        sec_game_nr += 2
        browse_by_genre(db, user_id, email, genre, sec_game_nr, page)

    elif answer == '':  # return to member menu
        member_menu(db, email)

    else:
        print('Invalid Input. Try again.')
        browse_by_genre(db, user_id, email, genre)


def checkout(db, user_id):
    # create timestamp for database
    time = datetime.now()
    # inserts order data and returns user data
    user_data = db.add_to_orders(user_id, time)
    cart_data = view_cart(db, user_id)
    # inserts cart_data into order_items and returns order no
    order_no, order_data = db.add_to_order_items(user_id, cart_data)

    # -- Invoice printing --
    print('========================================='
          '==========================================')
    print(f'Invoice for Order Nr. {order_no}')
    print('========================================='
          '==========================================')
    print()
    print(f'Name: {user_data[0]} {user_data[1]}')
    print(f'Address: {user_data[2]}')
    print(f'City: {user_data[4]}, {user_data[3]}')

    # get delivery date
    order_date = datetime.fromtimestamp(time)
    day_delta = timedelta(days=7)
    delivery_date = order_date + day_delta
    delivery_date.date()

    print(f'Estimated delivery date: {delivery_date}')
    print('-----------------------------------------'
          '------------------------------------------')

    # print ordered games
    ordered_games = db.view_order_items(order_no)
    formated_games, lst = format_cart(ordered_games)

    for line in formated_games:
        print(line)


def main():
    valid_connection = False
    username = None
    password = None

    # get login credentials from user and validate credentials
    while not valid_connection:
        username = input('Enter your Database username: ')
        password = getpass('Enter your Database password: ')
        if check_credentials(username, password):
            valid_connection = True
        else:
            print('Connection to the SQL server failed.'
                  ' Please make sure your credentials '
                  'are correct or mySQL server is running')

    # create database object with correct credentials
    db = Database(username, password)

    # menu loop
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

        # menu options
        match choice:
            case '1':
                login(db)
            case '2':
                register(db)
            case 'q':
                # disconnect from db before exiting programme
                db.connection.close()
                break


if __name__ == "__main__":
    main()
