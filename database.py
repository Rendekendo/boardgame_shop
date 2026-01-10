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

        self.cursor.execute(sql, val)
        self.connection.commit()
        print(self.cursor.rowcount, 'record inserted')

    def login(self, input_email, input_pwd):
        sql = 'SELECT email, pwd_hash FROM users WHERE email = %s'
        val = [input_email]
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        if result == []:
            return False
        else:
            email, pwd = result[0]

        if (input_email, input_pwd) == (email, pwd):
            return True
        else:
            return False

    def check_unique_email(self, input_email):
        sql = 'SELECT email FROM users WHERE email = %s'
        self.cursor.execute(sql, [input_email])
        data = self.cursor.fetchall()

        if data == []:  # email not in database yet
            return True
        else:
            return False

    def get_id(self, email):
        sql = 'SELECT user_id FROM users WHERE email = %s'
        self.cursor.execute(sql, [email])
        data = self.cursor.fetchall()

        return data[0][0]

    def in_cart(self, user_id, game_id):
        sql = 'SELECT quantity FROM cart WHERE user_id = %s AND game_id = %s'
        self.cursor.execute(sql, (user_id, game_id))
        quantity = self.cursor.fetchall()

        if quantity == []:
            return 0
        else:
            return quantity[0][0]

    def add_to_cart(self, user_id, game_id, quantity):
        quantity_in_cart = self.in_cart(user_id, game_id)
        final_value = int(quantity) + int(quantity_in_cart)
        if final_value > 2147483647:
            print('What are you doing?')
        else:

            if quantity_in_cart != 0:
                sql = (
                    'UPDATE cart '
                    'SET quantity = %s '
                    'WHERE user_id = %s AND game_id = %s'
                )
                val = (final_value, user_id, game_id)
            else:
                sql = (
                    'INSERT INTO cart (user_id, game_id, quantity)'
                    ' VALUES (%s, %s, %s)'
                    )
                val = (user_id, game_id, quantity)

            self.cursor.execute(sql, val)
            self.connection.commit()
            print(f'{quantity} games added to cart')

    def get_cart(self, user_id):
        sql = (
            'SELECT games.game_id, title, unit_price, quantity '
            'FROM cart '
            'JOIN games ON games.game_id = cart.game_id '
            'WHERE user_id = %s '
        )
        self.cursor.execute(sql, [user_id])

        result = self.cursor.fetchall()
        return result

    def add_to_orders(self, user_id):
        # get insertion data based on the user id
        sql_get = ('SELECT u.first_name, u.last_name, '
               'u.street, u.city, u.postal_code '
               'FROM board_games.users AS u '
               'WHERE u.user_id = %s')
        val_get = [user_id]
        self.cursor.execute(sql_get, val_get)
        answer = self.cursor.fetchmany(5)

        # convert data intno a list of strings
        lst_of_user_data = list()
        for i in answer:
            i = str(i)
            lst_of_user_data.append(i)

        # add data to orders table
        sql_add = ('INSERT INTO orders (user_id, ship_street, ship_city, ' \
                   'ship_postal_code) VALUES (%s, %s, %s, %s)')
        val_add = lst_of_user_data
        self.cursor.execute(sql_add, val_add)
        self.connection.commit()

        # return user data to display it
        return lst_of_user_data

    def add_to_order_items(self, user_id, order_no, line_totals):
        # get game_ids and quantities with user id from cart
        # get order_no
        # add to order_items
        pass

    def checkout_delete(self, user_id):
        sql = (
            'DELETE '
            'FROM cart '
            'WHERE user_id = %s '
        )
        self.cursor.execute(sql, [user_id])
        self.connection.commit()

    def search(self, query, offset, search_type):
        if search_type == 'title':
            sql = (
                'SELECT game_id, title, designer, unit_price, '
                'COUNT(*) OVER () AS total_count '
                'FROM games '
                'WHERE title LIKE %s '
                'LIMIT 3 OFFSET %s'
            )
            val = ('%' + query + '%', offset)
        else:
            sql = (
                'SELECT game_id, title, designer, unit_price, '
                'COUNT(*) OVER () AS total_count '
                'FROM games '
                'WHERE designer LIKE %s '
                'LIMIT 3 OFFSET %s'
            )
            val = (query + '%', offset)

        self.cursor.execute(sql, val)
        rows = self.cursor.fetchall()

        if not rows:
            return False, None

        count = rows[0][4]

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

    def checkout_user_data(self, user_id):
        

