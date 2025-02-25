import sqlite3

def initialize_database():
    conn = sqlite3.connect('book_reviews.db')
    conn.close()

if __name__ == '__main__':
    initialize_database()
    print('Database initialized.')