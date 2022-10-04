import re
from flask import render_template, flash, redirect, url_for, request
from app import app, query_db
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm
from datetime import datetime
import os
from werkzeug.utils import secure_filename
def password_check(password):
    """
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """
    # calculating the length
    length_error = len(password) < 8
    # searching for digits
    digit_error = re.search(r"\d", password) is None
    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None
    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None
    # searching for symbols
    symbol_error = re.search(r"\W", password) is None
    # overall result
    password_ok = not (length_error or digit_error or uppercase_error or lowercase_error or symbol_error)

    if password_ok:
        return True
    else:
        return False

# this file contains all the different routes, and the logic for communicating with the database

# home page/login/registration
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = IndexForm()


    if form.login.is_submitted() and form.login.submit:

        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.login.username.data), one=True)
        if user == None:
            flash('Sorry, wrong username/password!')
        elif user['password'] == form.login.password.data:
            return redirect(url_for('stream', username=form.login.username.data))
        else:
            flash('Sorry, wrong username/password!')

    elif form.register.is_submitted() and form.register.submit.data:
        if form.register.username.data and form.register.first_name.data and form.register.last_name.data and form.register.password.data and form.register.confirm_password.data:
            if password_check(form.register.password.data):
                if form.register.password.data == form.register.confirm_password.data:
                    query_db(
                        'INSERT INTO Users (username, first_name, last_name, password, attempts) VALUES("{}", "{}", "{}", "{}", 5);'.format(
                            form.register.username.data, form.register.first_name.data,
                            form.register.last_name.data, form.register.password.data))
                    flash("Successful register")
                    return redirect(url_for('index'))
                else:
                    flash("Password is different")
                    return redirect(url_for('index'))
            else:
                flash("Password must contain requirements")
                return redirect(url_for('index'))
        else:
            flash("Fill out register")
            return redirect(url_for('index'))
    return render_template('index.html', title='Welcome', form=form)


# content stream page
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/stream/<username>', methods=['GET', 'POST'])
def stream(username):
    form = PostForm()
    user = query_db(
        'SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    if form.is_submitted():
        if form.image.data:
            if allowed_file(form.image.data.filename):
                form.image.data.save(os.path.join(
                    app.config['UPLOAD_PATH'], secure_filename(form.image.data.filename)))
                query_db(
                    'INSERT INTO Posts (u_id, content, image, creation_time) VALUES({}, "{}", "{}", \'{}\');'.format(
                        user['id'], form.content.data, form.image.data.filename, datetime.now()))
                return redirect(url_for('stream', username=username))
            else:
                flash('Invalid file type. Valid ones are png, jpg, jpeg, gif')
        else:
            query_db('INSERT INTO Posts (u_id, content, image, creation_time) VALUES({}, "{}", "{}", \'{}\');'.format(
                user['id'], form.content.data, "", datetime.now()))
            return redirect(url_for('stream', username=username))

    posts = query_db(
        'SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc FROM Posts AS p JOIN Users AS u ON u.id=p.u_id WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id={0}) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id={0}) OR p.u_id={0} ORDER BY p.creation_time DESC;'.format(
            user['id']))
    return render_template('stream.html', title='Stream', username=username, form=form, posts=posts)

# comment page for a given post and user.
@app.route('/comments/<username>/<int:p_id>', methods=['GET', 'POST'])
def comments(username, p_id):
    form = CommentsForm()
    if form.is_submitted():
        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)

        query_db('INSERT INTO Comments (p_id, u_id, comment, creation_time) VALUES({}, {}, "{}", \'{}\');'.format(p_id,
                                                                                                                  user[
                                                                                                                      'id'],
                                                                                                                  form.comment.data,
                                                                                                                  datetime.now()))

    post = query_db('SELECT * FROM Posts WHERE id={};'.format(p_id), one=True)
    all_comments = query_db(
        'SELECT DISTINCT * FROM Comments AS c JOIN Users AS u ON c.u_id=u.id WHERE c.p_id={} ORDER BY c.creation_time DESC;'.format(
            p_id))
    return render_template('comments.html', title='Comments', username=username, form=form, post=post,
                           comments=all_comments)



# page for seeing and adding friends
@app.route('/friends/<username>', methods=['GET', 'POST'])
def friends(username):
    form = FriendsForm()
    user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    if form.is_submitted():
        friend = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.username.data), one=True)
        if friend is None:
            flash('User does not exist')
        else:
            query_db('INSERT INTO Friends (u_id, f_id) VALUES({}, {});'.format(user['id'], friend['id']))


    all_friends = query_db(
        'SELECT * FROM Friends AS f JOIN Users as u ON f.f_id=u.id WHERE f.u_id={} AND f.f_id!={} ;'.format(user['id'],
                                                                                                            user['id']))
    return render_template('friends.html', title='Friends', username=username, friends=all_friends, form=form)


# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    form = ProfileForm()
    if form.is_submitted():
        query_db(
            'UPDATE Users SET education="{}", employment="{}", music="{}", movie="{}", nationality="{}", birthday=\'{}\' WHERE username="{}" ;'.format(
                form.education.data, form.employment.data, form.music.data, form.movie.data, form.nationality.data,
                form.birthday.data, username
            ))
        return redirect(url_for('profile', username=username))


    user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    return render_template('profile.html', title='profile', username=username, user=user, form=form)
