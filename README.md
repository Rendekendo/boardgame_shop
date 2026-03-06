# Online Boardgame Shop

Command-line desktop application for browsing, searching, and purchasing boardgames.  
Built with **Python** and **MySQL**, the app allows users to register, log in, browse by genre, search by designer or title, manage a shopping cart, and complete orders with automatic invoice generation.

## Features

- User registration and secure login with hashed passwords
- Browse games by genre
- Search games by title or designer
- Shopping cart management
- Checkout system with invoice printing
- Pagination support for search results and genre browsing
- Data stored in a MySQL database

## Technologies

- Python 3
- MySQL
- `mysql-connector-python` library
- Standard Python libraries: `getpass`, `hashlib`, `datetime`, `re`, `decimal`

### Genre Browsing

```
== GENRES ==
1) Strategy
2) Family
3) Cooperative
...
```

- Users can select a genre to view available games
- Games are displayed with ID, title, and price
- Supports pagination and adding games to cart

### Search by Designer or Title

```
== Results (showing 1 - 3 of 12) ==
ID BG101: Catan by Klaus Teuber $35.00
ID BG102: Pandemic by Matt Leacock $30.00
...
Options: enter Game ID to add to cart, 'n' for next, ENTER to return.
```

- Search supports both whole word title and "starts with" designer queries
- Paginated results with total count displayed

### Shopping Cart

```
Game ID   Title                                              $         Qty      Total
-----------------------------------------------------------------------------------
BG101     Catan                                             $35.0       2      $70.00
BG102     Pandemic                                          $30.0       1      $30.00
-----------------------------------------------------------------------------------
Total = $100.00
```

- Displays all items in cart with quantities and line totals
- Shows total cart value
- Users can proceed to checkout from this screen

### Checkout / Invoice

```
=========================================
Invoice for Order Nr. 15
=========================================
Name: John Doe
Address: 123 Boardgame St
City: Gametown, 12345
Estimated delivery date: 2026-03-13
-----------------------------------------
...
Total = $100.00
=========================================
== ORDER COMPLETE ==
```

- Generates an order and prints a detailed invoice
- Clears the shopping cart after checkout
- Includes estimated delivery date

## How It Works

1. Users register or log in with a valid email and password.
2. After logging in, users can:
   - Browse games by genre
   - Search by designer or title
   - View and manage their shopping cart
3. Users add games to the cart and proceed to checkout.
4. The system creates an order in the database and prints an invoice.
5. Cart data is cleared after successful checkout.

## Database

- **Users table** – stores user information and hashed passwords
- **Games table** – stores boardgame metadata (ID, title, designer, genre, price)
- **Cart table** – temporary shopping cart storage per user
- **Orders / Order_items tables** – store completed order data

## Security

- Passwords are hashed using SHA-256 before storage
- Email validation is performed on registration
- Input is sanitized for SQL queries using parameterized statements
