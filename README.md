# Online Book Store

This is a project for CS 157A. Our goal is to create an online bookstore that allows for customers to easily find books they want and order them. Giving the option to place the order for pickup near their location or delivery right to them.

## Purpose

We aim to provide book lovers with a way to order the books they want in a simple and efficient way with ease of pickup and delivery. Our main objective is to build a database to store books, members, and order information. Customers will be able to authenticate themselves and track their current and past orders. Staff will be able to view and manage inventory and see all orders.

# Database Schema

## Entities

- Books: Stores the book catalog, prices, and available stock.
    - (PK: book_id, title, FK: author id, publisher, summary, stock, is_active, price)
- Members: Stores registered customers and staff accounts.
    - (PK: member id, name, UNIQUE: email, password_hash, role)
- Orders: Stores customer purchases and fulfillment information.
    -  (PK: order_id, FK: member id, delivery_address, total cost, status)
- OrderLine: Records the books, quantities, and purchase prices associated with each order.
    - (FK: order_id, FK: book_id, price)
    - PK: (order_id, book_id)
- Reviews: Stores members’ ratings and written reviews of books.
    - (PK: review_id, FK: book_id, FK: member id, rating/score, review_text)
- Authors: Stores information about book authors.
    - (PK: author_id, name)

# Technology

## Backend
- Python 3.14.10
- Flask (web framework and application logic)
- MySQL Connector/Python (database connector API)
- Apache HTTP Server (serves the Flask app in deployment)

## Database
- MySQL (MySQL Workbench is used for design and administration)

## Architecture
The application follows a three-tier architecture: the website interface, the Python/Flask application logic, and the MySQL database. The application communicates with the database through MySQL Connector/Python and executes SELECT, INSERT, UPDATE, and DELETE statements through it.

## Development Environment
- VS Code (editor)
- MySQL Workbench
- Git/GitHub
- Operating systems: Windows, macOS, and Linux

## Setup
```
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running Locally (Development)

```
flask --app wsgi run --debug
```

### Project layout
- `wsgi.py`: entry point used by Flask and by Apache or Gunicorn
- `config.py`: application settings
