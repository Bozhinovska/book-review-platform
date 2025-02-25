import sqlite3
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='templates')

app.secret_key = 'password'

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db_connection():
    conn = sqlite3.connect('book_reviews.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM Books').fetchall()
    conn.close()
    return render_template('index.html', books=books)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM Users WHERE email = ?', (email,)).fetchone()
        if user:
            flash('Емаил адресата веќе постои. Обидете се со друга.')
            return redirect(url_for('register'))

        name = request.form['name']
        surname = request.form['surname']
        password = request.form['password']

        date_registered = datetime.now().strftime('%Y-%m-%d')
        profile_picture = request.form.get('profile_picture', 'default_profile.jpeg')

        conn.execute(
            'INSERT INTO Users(name, surname, email, password, date_registered, profile_picture) VALUES(?, ?, ?, ?, ?, ?)',
            (name, surname, email, password, date_registered, profile_picture)
        )
        conn.commit()
        conn.close()

        flash('Успешна регистрација! Сега најавете се.')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM Users WHERE email = ? AND password = ?', (email, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['user_id']
            session['name'] = user['name']
            session['profile_picture'] = user['profile_picture'] or 'default_profile.jpeg'
            flash('Успешна најава!')
            return redirect(url_for('home'))
        else:
            flash('Грешен емаил или лозинка, обидете се повторно.')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Успешно се одјавивте.')
    return redirect(url_for('home'))


@app.route('/my_profile')
def my_profile():

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM Users WHERE user_id = ?', (session['user_id'],)).fetchone()

    rated_books = conn.execute('''
        SELECT Books.book_id, Books.title, Books.book_cover_image, Reviews.rating
        FROM Reviews
        JOIN Books ON Reviews.book_id = Books.book_id
        WHERE Reviews.user_id = ?
    ''', (session['user_id'],)).fetchall()

    favourite_books = conn.execute('''
            SELECT Books.book_id, Books.title, Books.book_cover_image
            FROM FavouriteBook
            JOIN Books ON FavouriteBook.book_id = Books.book_id
            WHERE FavouriteBook.user_id = ?
        ''', (session['user_id'],)).fetchall()

    conn.close()
    return render_template('profile.html', user=user, rated_books=rated_books, favourite_books=favourite_books)


@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    conn = get_db_connection()

    if request.method == 'GET':
        user = conn.execute('SELECT * FROM Users WHERE user_id = ?', (session['user_id'],)).fetchone()
        conn.close()
        return render_template('edit_profile.html', user=user)

    if request.method == 'POST':
        user = conn.execute('SELECT * FROM Users WHERE user_id = ?', (session['user_id'],)).fetchone()

        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        password = request.form['password']

        current_profile_picture = request.form['current_profile_picture']

        file = request.files['profile_picture']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            profile_picture = filename
        else:
            profile_picture = current_profile_picture
        if password:
            conn.execute('''
                        UPDATE Users
                        SET name = ?, surname = ?, email = ?, password = ?, profile_picture = ?
                        WHERE user_id = ?
                    ''', (name, surname, email, password, profile_picture, session['user_id']))
        else:
            conn.execute('''
                        UPDATE Users
                        SET name = ?, surname = ?, email = ?, profile_picture = ?
                        WHERE user_id = ?
                    ''', (name, surname, email, profile_picture, session['user_id']))

        conn.commit()
        conn.close()
        session['profile_picture'] = profile_picture

        flash('Профилот е успешно ажуриран.')
        return redirect(url_for('my_profile'))


@app.route('/genre/<genre_name>')
def books_by_genre(genre_name):
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM Books WHERE genre = ?', (genre_name,)).fetchall()
    conn.close()
    return render_template('genre.html', books=books, genre=genre_name)


@app.route('/book/<int:book_id>', methods=['GET', 'POST'])
def book_details(book_id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM Books WHERE book_id = ?', (book_id,)).fetchone()

    reviews = conn.execute('''
        SELECT Reviews.review_id, Reviews.content, Reviews.rating, Reviews.reviews_date, Reviews.user_id, Users.name, Users.surname
        FROM Reviews
        JOIN Users ON Reviews.user_id = Users.user_id
        WHERE Reviews.book_id = ?
    ''', (book_id,)).fetchall()

    if request.method == 'POST':
        review_id = request.form.get('review_id')
        content = request.form.get('content')
        rating = request.form.get('rating')

        if review_id:
            conn.execute('''
                UPDATE Reviews SET content = ?, rating = ? WHERE review_id = ? AND user_id = ?
            ''', (content, rating, review_id, session['user_id']))
            conn.commit()
            flash('Рецензијата е успешно уредена!')
            conn.close()
            return redirect(url_for('book_details', book_id=book_id))

    conn.close()
    return render_template('book_details.html', book=book, reviews=reviews)


@app.route('/book/<int:book_id>/review', methods=['POST'])
def add_review(book_id):
    if 'user_id' not in session:
        flash('Мора да сте најавени за да додадете рецензија.')
        return redirect(url_for('login'))

    content = request.form.get('content')
    rating = request.form.get('rating')

    if not content or not rating:
        flash('Сите полиња мора да бидат пополнети.')
        return redirect(url_for('book_details', book_id=book_id))

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO Reviews (content, rating, reviews_date, user_id, book_id) VALUES (?, ?, DATE(), ?, ?)',
        (content, rating, session['user_id'], book_id))
    conn.commit()
    conn.close()

    flash('Рецензијата е успешно додадена!')
    return redirect(url_for('book_details', book_id=book_id))


@app.route('/delete_review/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    if 'user_id' not in session:
        flash('Мора да сте најавени за да ја избришете рецензијата.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    review = conn.execute('SELECT * FROM Reviews WHERE review_id = ? AND user_id = ?',
                          (review_id, session['user_id'])).fetchone()

    if not review:
        flash('Немате дозвола за бришење на оваа рецензија.')
        return redirect(url_for('home'))

    conn.execute('DELETE FROM Reviews WHERE review_id = ?', (review_id,))
    conn.commit()
    conn.close()

    flash('Рецензијата е успешно избришана!')
    return redirect(url_for('book_details', book_id=review['book_id']))


@app.route('/book/<int:book_id>/add_favorite', methods=['POST'])
def add_favorite(book_id):
    if 'user_id' not in session:
        flash('Мора да сте најавени за да додадете книга во омилени.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('INSERT OR IGNORE INTO FavouriteBook (user_id, book_id) VALUES (?, ?)',
                 (session['user_id'], book_id))
    conn.commit()
    conn.close()

    flash('Книгата е додадена во вашата листа на омилени.')
    return redirect(url_for('book_details', book_id=book_id))


@app.route('/remove_favorite/<int:book_id>', methods=['POST'])
def remove_favorite(book_id):
    if 'user_id' not in session:
        flash('Мора да сте најавени за да ја отстраните книгата од омилени.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM FavouriteBook WHERE user_id = ? AND book_id = ?', (session['user_id'], book_id))
    conn.commit()
    conn.close()

    flash('Книгата е успешно отстранета од омилените.')
    return redirect(url_for('my_profile'))


if __name__ == '__main__':
    app.run(debug=True)
