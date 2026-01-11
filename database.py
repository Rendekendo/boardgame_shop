from mysql.connector import connect


class Database:

    def __init__(self, username, password):
        self.connection = connect(host="localhost",
                                  user=username,
                                  password=password,
                                  database="boardgame_shop")
        self.cursor = self.connection.cursor()

    def register(self,
                 first_name,
                 last_name,
                 street,
                 city,
                 postal_code,
                 phone_no,
                 email,
                 pwd_hash):
        sql = ("INSERT INTO users (first_name, last_name, street, city, "
               "postal_code, phone_no, email, pwd_hash) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")

        val = (first_name,
               last_name,
               street,
               city,
               postal_code,
               phone_no,
               email,
               pwd_hash)

        # insert user data into user table
        self.cursor.execute(sql, val)
        self.connection.commit()
        print('User registration succesful')

    def login(self, input_email, input_pwd):
        # verify if credentials are in database

        # get email and password where input_email
        sql = 'SELECT email, pwd_hash FROM users WHERE email = %s'
        val = [input_email]
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()

        if result == []:  # no email found, invalid credentials
            return False
        else:
            email, pwd = result[0]  # unpack credentials

        if (input_email, input_pwd) == (email, pwd):  # compare with input
            return True  # correct
        else:
            return False  # invalid

    def check_unique_email(self, input_email):
        # check if email is already in database

        sql = 'SELECT email FROM users WHERE email = %s'
        self.cursor.execute(sql, [input_email])
        data = self.cursor.fetchall()

        if data == []:  # email not in database yet
            return True
        else:  # email found
            return False

    def get_id(self, email):
        # return user_id from email

        sql = 'SELECT user_id FROM users WHERE email = %s'
        self.cursor.execute(sql, [email])
        data = self.cursor.fetchall()

        return data[0][0]

    def in_cart(self, user_id, game_id):
        # return quantity of a specific game in a specific user's cart

        sql = 'SELECT quantity FROM cart WHERE user_id = %s AND game_id = %s'
        self.cursor.execute(sql, (user_id, game_id))
        quantity = self.cursor.fetchall()

        if quantity == []:  # no data i.e. 0 items
            return 0
        else:
            return quantity[0][0]  # return quantity in string

    def add_to_cart(self, user_id, game_id, quantity):
        # insert values into cart table

        # if item already in cart
        quantity_in_cart = self.in_cart(user_id, game_id)
        final_value = int(quantity) + int(quantity_in_cart)

        if final_value > 2147483647:
            print('What are you doing?')
        else:

            if quantity_in_cart != 0:  # if already in cart update value
                sql = (
                    'UPDATE cart '
                    'SET quantity = %s '
                    'WHERE user_id = %s AND game_id = %s'
                )
                val = (final_value, user_id, game_id)

            else:  # not in cart yet
                sql = (
                    'INSERT INTO cart (user_id, game_id, quantity)'
                    ' VALUES (%s, %s, %s)'
                    )
                val = (user_id, game_id, quantity)

            # send sql command
            self.cursor.execute(sql, val)
            self.connection.commit()
            print(f'{quantity} games added to cart')

    def get_cart(self, user_id):
        # returns cart data of a specific user

        sql = (
            'SELECT games.game_id, title, unit_price, quantity '
            'FROM cart '
            'JOIN games ON games.game_id = cart.game_id '
            'WHERE user_id = %s '
        )
        self.cursor.execute(sql, [user_id])

        result = self.cursor.fetchall()
        return result

    def add_to_orders(self, user_id, time):
        # get insertion data based on the user id
        sql_get = ('SELECT u.first_name, u.last_name, '
                   'u.street, u.city, u.postal_code '
                   'FROM boardgame_shop.users AS u '
                   'WHERE u.user_id = %s')
        val_get = [user_id]
        self.cursor.execute(sql_get, val_get)
        answer = self.cursor.fetchmany(5)

        print(answer)

        # convert data into a list of strings
        lst_of_user_data_export = list()
        for tuple in answer:
            for data in tuple:
                data = str(data)
                lst_of_user_data_export.append(data)

        lst_of_user_data_sql = list()
        i = 0
        for tuple in answer:
            for data in tuple:
                if i == 0:
                    lst_of_user_data_sql.append(user_id)
                elif i == 1:
                    lst_of_user_data_sql.append(time)
                else:
                    lst_of_user_data_sql.append(data)
                i += 1

        print(lst_of_user_data_sql)

        # add data to orders table
        sql_add = ('INSERT INTO orders (user_id, created, ship_street, '
                   'ship_city, ship_postal_code) VALUES (%s, %s, %s, %s, %s)')
        val_add = lst_of_user_data_sql
        self.cursor.execute(sql_add, val_add)
        self.connection.commit()

        # return user data to display it
        return lst_of_user_data_export

    def add_to_order_items(self, user_id, cart_data):
        # get order no
        sql_order_no = ('SELECT o.order_no '
                        'FROM boardgame_shop.orders WHERE user_id = %s '
                        'ORDER BY o.created DESC '
                        'LIMIT 1')
        val_order_no = [user_id]
        self.cursor.execute(sql_order_no, val_order_no)
        order_no = self.cursor.fetchmany(1)

        # add to order_items
        lst_of_oder_data = []
        for i in range(0, len(cart_data, 3)):
            sql_add = ('INSERT INTO order_items (order_no, game_id, '
                       'quantity, line_total) '
                       'VALUES (%s, %s, %s, %s)')
            val_add = [order_no, cart_data[i], cart_data[i + 1], cart_data[i + 2]]
            lst_of_oder_data.append(val_add)
            self.cursor.execute(sql_add, val_add)
            self.connection.commit()

        return order_no, lst_of_oder_data

    def view_order_items(self, order_no):
        sql = ('SELECT games.game_id, title, unit_price, quantity, line_total'
               'FROM order_items '
               'JOIN games ON games.game_id = order_items.game_id '
               'WHERE order_no = %s ')
        val = [order_no]
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()

        return result

    def checkout_delete(self, user_id):
        # clear cart data after checkout

        sql = (
            'DELETE '
            'FROM cart '
            'WHERE user_id = %s '
        )
        self.cursor.execute(sql, [user_id])
        self.connection.commit()

    def search(self, query, offset, search_type):
        # search for game by title or designer

        if search_type == 'title':  # user chose title search
            sql = (
                'SELECT game_id, title, designer, unit_price, '
                'COUNT(*) OVER () AS total_count '
                'FROM games '
                'WHERE title LIKE %s '
                'LIMIT 3 OFFSET %s'
            )
            # whole word query
            val = ('%' + query + '%', offset)

        else:  # designer search
            sql = (
                'SELECT game_id, title, designer, unit_price, '
                'COUNT(*) OVER () AS total_count '
                'FROM games '
                'WHERE designer LIKE %s '
                'LIMIT 3 OFFSET %s'
            )
            # query starts with
            val = (query + '%', offset)

        # send sql command
        self.cursor.execute(sql, val)
        rows = self.cursor.fetchall()

        # no results
        if not rows:
            return False, None

        # get total count of games found
        count = rows[0][4]

        # return found games in list
        result = []
        for row in rows:
            result.append((row[0], row[1], row[2], row[3]))

        return result, count

    def get_genres(self):
        sql_get_genres = 'SELECT g.genre  FROM boardgame_shop.games AS g ' \
                     'GROUP BY g.genre;'
        self.cursor.execute(sql_get_genres)
        genres = self.cursor.fetchmany(20)

        return genres

    def get_page_count(self, genre):
        game_sql = 'SELECT COUNT(*) FROM boardgame_shop.games WHERE genre = %s'
        game_val = [genre]
        self.cursor.execute(game_sql, game_val)
        sum_of_games = self.cursor.fetchone()

        return sum_of_games

    def get_game_data_browse(self, genre, sec_game_nr):
        sql = """
        SELECT g.game_id, g.title, g.unit_price
        FROM boardgame_shop.games AS g
        WHERE g.genre = %s
        LIMIT 2 OFFSET %s;
        """
        val = [genre, sec_game_nr]
        self.cursor.execute(sql, val)
        rows = self.cursor.fetchmany(2)

        return rows

    def valid_game_id(self, answer):
        test_sql = str("SELECT g.* FROM boardgame_shop.games "
                       "AS g WHERE g.game_id = %s;")
        test_id = [answer]
        status = self.cursor.execute(test_sql, test_id)
        self.cursor.fetchmany(10)  # empty the cursor

        return status
