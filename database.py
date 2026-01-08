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

    def add_to_cart(self, user_id, game_id, quantity):
        sql = 'INSERT INTO cart (user_id, game_id, quantity)' \
              ' VALUES (%s, %s, %s)'
        val = (user_id, game_id, quantity)
        self.cursor.execute(sql, val)

        self.connection.commit()
        print(f'f{quantity} games added to cart')

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
