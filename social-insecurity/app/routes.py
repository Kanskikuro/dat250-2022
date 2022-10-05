from flask import render_template, flash, redirect, url_for, request
from app import app, query_db
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import re
from flask_login import login_user, login_required, logout_user
from app.__init__ import Users, qb
def password_check(password):
    """
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """
    password_ok = not (len(password) < 8 or re.search(r"\d", password) is None or re.search(r"[A-Z]", password) is None or re.search(r"[a-z]", password) is None or  re.search(r"\W", password) is None)

    if password_ok:
        return True
    else:
        return False

#import hashlib

# this file contains all the different routes, and the logic for communicating with the database

# home page/login/registration
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = IndexForm()

    if form.login.is_submitted() and form.login.submit.data:
        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.login.username.data), one=True)
        if user == None:
            flash('Sorry, wrong password!')
        elif user['password'] == form.login.password.data:
            login_user(Users.query.filter_by(username=form.login.username.data).first())
            return redirect(url_for('stream', username=form.login.username.data))
        else:
            flash('Sorry, wrong password!')

    elif form.register.is_submitted() and form.register.submit.data:
        if form.register.username.data and form.register.first_name.data and form.register.last_name.data and form.register.password.data and form.register.confirm_password.data:
            #salt="5gz"
            #Password= form.register.password.data+salt
            #hashed=hashlib.md5(Password.encode())
            if password_check(form.register.password.data):
                if form.register.password.data == form.register.confirm_password.data:
                    query_db(
                        'INSERT INTO Users (username, first_name, last_name, password) VALUES("{}", "{}", "{}", "{}");'.format(
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
def allowed_file(filename):
   return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
            #returns True if the extention is allowed, False if not

@app.route('/stream/<username>', methods=['GET', 'POST'])
@login_required
def stream(username):
    form = PostForm()
    user = query_db(
        'SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    if form.is_submitted():
        if form.image.data:
            if allowed_file(form.image.data.filename):
                form.image.data.save(os.path.join(
                app.config['UPLOAD_PATH'], secure_filename(form.image.data.filename)))
                query_db('INSERT INTO Posts (u_id, content, image, creation_time) VALUES({}, "{}", "{}", \'{}\');'.format(
                    user['id'], form.content.data, form.image.data.filename, datetime.now()))
                return redirect(url_for('stream', username=username))
            else:
                flash('Invalid file type. Valid ones are png, jpg, jpeg, gif')
        else:
            query_db('INSERT INTO Posts (u_id, content, image, creation_time) VALUES({}, "{}", "{}", \'{}\');'.format(
                user['id'], form.content.data, "", datetime.now()))
            return redirect(url_for('stream', username=username))

    posts = query_db(
        'SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc FROM Posts AS p JOIN Users AS u ON u.id=p.u_id WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id={0}) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id={0}) OR p.u_id={0} ORDER BY p.creation_time DESC;'.format(user['id']))
    return render_template('stream.html', title='Stream', username=username, form=form, posts=posts)

# comment page for a given post and user.
@app.route('/comments/<username>/<int:p_id>', methods=['GET', 'POST'])
@login_required
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
@login_required
def friends(username):
    form = FriendsForm()
    user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    if form.is_submitted():
        friend = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.username.data), one=True)
        if friend is None:
            flash('User does not exist')
        else:
            query_db('INSERT INTO Friends (u_id, f_id) VALUES({}, {});'.format(user['id'], friend['id']))
    
    all_friends = query_db('SELECT * FROM Friends AS f JOIN Users as u ON f.f_id=u.id WHERE f.u_id={} AND f.f_id!={} ;'.format(user['id'], user['id']))
    return render_template('friends.html', title='Friends', username=username, friends=all_friends, form=form)

# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    form = ProfileForm()
    if form.is_submitted():
        query_db('UPDATE Users SET education="{}", employment="{}", music="{}", movie="{}", nationality="{}", birthday=\'{}\' WHERE username="{}" ;'.format(
            form.education.data, form.employment.data, form.music.data, form.movie.data, form.nationality.data, form.birthday.data, username
        ))
        return redirect(url_for('profile', username=username))
    
    user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    return render_template('profile.html', title='profile', username=username, user=user, form=form)