# -*- coding: utf-8 -*-
import os
import json
import random
import string
import requests
import httplib2

from flask import Flask
from flask import session as login_session
from flask import make_response
from flask import (flash, render_template, url_for, jsonify,
                   request, redirect, send_from_directory)

from functools import wraps
from werkzeug import secure_filename

from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from models import Base, User, Category, Item

# secret key to encrypt session cookie
SECRET_KEY = ''.join(random.choice(string.ascii_uppercase +
                     string.digits) for x in xrange(32))

# define default values for file management
UPLOAD_FOLDER = '/vagrant/catalog/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = SECRET_KEY

# connect to database and create db session
engine = create_engine('sqlite:///heroes.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# GENERAL FUNCTIONS AND ROUTES -->
def categoryMenu():
    '''Get categories from DB for menu navigation'''
    menuNav = session.query(Category).all()
    return menuNav


def allowed_file(filename):
    '''Check if a file extension is valid'''
    return ('.' in filename and filename.rsplit('.', 1)[1]
            in ALLOWED_EXTENSIONS)


def delete_image(filename):
    '''Delete a image from server'''
    try:
        os.remove(os.path.join(UPLOAD_FOLDER, filename))
    except OSError:
        print "Sorry, we couldn't delete the image %s" % filename


@app.route('/picture/<filename>')
def show_image(filename):
    '''Get images uploaded'''
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# THE JSON API ENDPOINTS -->
@app.route('/heroes/JSON')
def catlistsJSON():
    '''Return all items with categories as JSON file'''
    categories = categoryMenu()
    return jsonify(categories=[r.serialize for r in categories])


@app.route('/herocreator/<int:user_id>/JSON/')
def listJSON(user_id):
    '''Return a user list as JSON file'''
    try:
        user = session.query(User).filter_by(id=user_id).one()
    except NoResultFound:
        flash("Sorry, this hero creator isn't among us.")
        return redirect(url_for('mainPage'))

    return jsonify(User=user.serialize)


@app.route('/hero/<int:item_id>/JSON/')
def itemJSON(item_id):
    '''Return a single item as JSON file'''
    try:
        item = session.query(Item).filter_by(id=item_id).one()
    except NoResultFound:
        flash("Sorry, this hero isn't among us.")
        return redirect(url_for('mainPage'))

    return jsonify(Item=item.serialize)


# AUTH LOGIN -->
@app.route('/login/')
def loginPage():
    '''Create a state token to prevent request forgery.

    Args:
        state (char(32)): A token made by uppercase letters and digits.
        login_session['state']: Login session to store the token for
        validation.

    Returns:
        The login page with state token validation.
    '''
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in range(32))
    login_session['state'] = state

    menuNav = categoryMenu()

    return render_template('login.html', STATE=state, menuNav=menuNav)
    # For testing, comment the line above and uncomment next line.
    # return "The current session state is %s" % login_session['state']
    # Refresh the /login page a couple times. The token must change every time.


def createUser(login_session):
    '''Create new user taking login session as input.

    Returns:
        The id for new user in database.
    '''
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])

    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserID(email):
    '''Check if user is signing in or up, with email as input.

    Returns:
        The user id if already signed up.
        None if it's the first connection - signing up.
    '''
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except NoResultFound:
        return None


def getUserInfo(user_id):
    '''Get user information taking user id as input.

    Returns:
        A user object.
    '''
    try:
        user = session.query(User).filter_by(id=user_id).one()
        return user
    except NoResultFound:
        return None


def login_required(f):
    '''Decorator function to check if user is logged in.'''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You must be logged in!")
            return redirect('/login')
    return decorated_function


# create the client ID for G+
CLIENT_ID = json.loads(
    open('client_secrets_gplus.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    '''Implement server-side function for Google+.'''
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets_gplus.json',
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    gplus_id = credentials.id_token['sub']

    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # check if user is logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # store the access token
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # get user information
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    # store login infos in session
    login_session['provider'] = 'google'
    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    # check if user already exists
    user_id = getUserID(login_session['email'])
    print "User exist!"
    if not user_id:
        print "Creating new user!"
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    print "User logged in."

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'

    output += '<img src="'
    output += login_session['picture']
    output += '"style = "width: 300px; height: 300px; border-radius: 150px; '
    output += '-webkit-border-radius: 150px; -moz-border-radius: 150px;">'

    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    '''Implement server-side function for Facebook login.'''
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open(
        'client_secrets_fb.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open(
        'client_secrets_fb.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
           '&fb_exchange_token=%s') % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print "url sent for API access:%s" % url
    print "API JSON result: %s" % result
    # store login infos in session
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    # store token in login session
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token
    # get user picture
    url = ('https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height='
           '200&width=200') % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # ckeck if user already exist
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output


def gdisconnect():
    '''Disconnect a user from Google.'''
    access_token = login_session.get('access_token')

    if access_token is None:
        print 'There is no access token.'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # execute HTTP GET request to revoke current token
        url = ('https://accounts.google.com/o/oauth2/revoke?'
               'token=%s') % access_token
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]
        print 'result is:'

        if result['status'] != '200':
            response = make_response(json.dumps(
                'Failed to revoke for given user.'), 400)
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            response = make_response(json.dumps(
                'User logged out!'), 200)
            response.headers['Content-Type'] = 'application/json'
            return response


def fbdisconnect():
    '''Disconnect a user from Facebook.'''
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = ('https://graph.facebook.com/%s/permissions?'
           'access_token=%s') % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]

    if result == '200':
        response = make_response(json.dumps(
            'Failed to revoke. Try again.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'User logged out!'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/disconnect')
def logout():
    '''Logout system for user.'''
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']

        elif login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']

        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']

        flash("You have successfully been logged out.")
    else:
        flash("You were not logged in")

    return redirect(url_for('loginPage'))


# PRIMARY ROUTES -->
@app.route('/')
def mainPage():
    '''The Homepage'''
    menuNav = categoryMenu()

    items = session.query(Item).order_by(desc(Item.id))
    return render_template('index.html', menuNav=menuNav, items=items)


@app.route('/herocreator/<int:user_id>/')
def showList(user_id):
    '''A User's list page '''
    menuNav = categoryMenu()

    try:
        user = session.query(User).filter_by(id=user_id).one()
    except NoResultFound:
        flash("Sorry, this hero creator isn't among us!")
        return redirect(url_for('mainPage'))

    items = (session.query(Item).filter_by(user_id=user_id).order_by(
             desc(Item.category_id)).all())
    author = getUserInfo(user.id)

    if 'username' not in login_session or author.id != (
                         login_session['user_id']):
        return render_template('list.html',
                               menuNav=menuNav,
                               user=user,
                               items=items)
    else:
        return render_template('list.html',
                               menuNav=menuNav,
                               user=user,
                               items=items,
                               author=author)


@app.route('/herocreator/mylist/')
@login_required  # check if user is logged in
def myList():
    '''Navbar link to redirect to user list'''
    user_id = getUserID(login_session['email'])
    return redirect(url_for('showList', user_id=user_id))


@app.route('/herocreator/<int:user_id>/delete/', methods=['GET', 'POST'])
@login_required  # check if user is logged in
def deleteList(user_id):
    '''Handler with deleting a list'''
    menuNav = categoryMenu()

    try:
        user = session.query(User).filter_by(id=user_id).one()
    except NoResultFound:
        flash("Sorry, this hero creator isn't among us!")
        return redirect(url_for('mainPage'))

    author = getUserInfo(user.id)

    if author.id != login_session['user_id']:
        flash("Hey, you can't delete a Hero Creator!")
        return redirect(url_for('mainPage'))
    else:
        items = session.query(Item).filter_by(user_id=user_id).all()

        if request.method == 'POST':
            for item in items:
                session.delete(item)
                print "List deleted!"

            session.delete(user)
            session.commit()
            flash("Oh! You're no longer a Hero Creator! :-(")
            return redirect(url_for('logout'))
        else:
            return render_template('list_delete.html',
                                   menuNav=menuNav,
                                   user=user)


@app.route('/category/<int:category_id>/heroes/')
def showCategory(category_id):
    '''Show items to a specific category.'''
    menuNav = categoryMenu()

    try:
        category = session.query(Category).filter_by(id=category_id).one()
    except NoResultFound:
        flash("Sorry, this category doesn't exist.")
        return redirect(url_for('mainPage'))

    items = (session.query(Item).filter_by(category_id=category_id).order_by(
             desc(Item.id)).all())
    return render_template('category.html',
                           menuNav=menuNav,
                           category=category,
                           items=items)


@app.route('/hero/<int:item_id>/')
def showItem(item_id):
    '''Show a single item page'''
    menuNav = categoryMenu()

    try:
        item = session.query(Item).filter_by(id=item_id).one()
    except NoResultFound:
        flash("Sorry, this hero isn't among us!")
        return redirect(url_for('mainPage'))

    author = getUserInfo(item.user_id)

    if 'username' not in login_session or author.id != (
                         login_session['user_id']):
        return render_template('item.html',
                               menuNav=menuNav,
                               item=item)
    else:
        return render_template('item.html',
                               menuNav=menuNav,
                               item=item,
                               author=author)


@app.route('/herocreator/<int:user_id>/newhero/', methods=['GET', 'POST'])
@login_required  # check if user is logged in
def addItem(user_id):
    '''Handler to add a new Item'''
    try:
        user = session.query(User).filter_by(id=user_id).one()
    except NoResultFound:
        flash("Sorry, this hero creator isn't among us!")
        return redirect(url_for('mainPage'))

    author = getUserInfo(user.id)

    if author.id != login_session['user_id']:
        flash("Hey, you can't add a hero to another Hero Creator list!")
        return redirect(url_for('mainPage'))
    else:
        if request.method == 'POST':
            if not request.form['name']:
                flash("Your hero needs a name")
                return redirect(url_for('addItem', user_id=user_id))

            if not request.form['description']:
                flash("C'mon! One line about your Hero!")
                return redirect(url_for('addItem', user_id=user_id))

            category = (session.query(Category).filter_by(
                        name=request.form['category']).one())
            newItem = Item(category=category,
                           name=request.form['name'],
                           description=request.form['description'],
                           user_id=user.id)

            picture_filename = request.files['picture_file']

            if picture_filename and allowed_file(picture_filename.filename):
                filename = secure_filename(picture_filename.filename)
                if os.path.isdir(app.config['UPLOAD_FOLDER']) is False:
                    os.mkdir(app.config['UPLOAD_FOLDER'])
                picture_filename.save(os.path.join(
                                      app.config['UPLOAD_FOLDER'], filename))
                newItem.picture_filename = filename
            elif request.form['picture_url']:
                newItem.picture_url = request.form['picture_url']
            else:
                flash("Wow! Your hero deserves a picture! Upload it"
                      " or give us a link, please!")
                return redirect(url_for('addItem', user_id=user_id))

            session.add(newItem)
            session.commit()

            flash("Super Perfect! Your hero is up!")
            item_id = newItem.id
            return redirect(url_for('showItem', item_id=item_id))
        else:
            categories = categoryMenu()
            return render_template('item_new.html',
                                   categories=categories,
                                   user=user)


@app.route('/hero/<int:item_id>/edit/', methods=['GET', 'POST'])
@login_required  # check if user is logged in
def editItem(item_id):
    '''Handler to edit an item.'''
    try:
        item = session.query(Item).filter_by(id=item_id).one()
    except NoResultFound:
        flash("Sorry, this hero isn't among us!")
        return redirect(url_for('mainPage'))

    author = getUserInfo(item.user_id)

    if author.id != login_session['user_id']:
        flash("Hey, you can't edit a hero that doesn't belong to you!")
        return redirect(url_for('mainPage'))
    else:
        if request.method == 'POST':
            if not request.form['name']:
                flash("Your hero needs a name")
                return redirect(url_for('editItem', item_id=item_id))
            else:
                if request.form['name'] != item.name:
                    item.name = request.form['name']

            if not request.form['description']:
                flash("C'mon! One line about your hero!")
                return redirect(url_for('editItem', item_id=item_id))
            else:
                if request.form['description'] != item.description:
                    item.description = request.form['description']

            editedCategory = (session.query(Category).filter_by(
                        name=request.form['category']).one())
            if editedCategory != item.category:
                item.category = editedCategory

            picture_filename = request.files['picture_file']

            if picture_filename and allowed_file(picture_filename.filename):
                if item.picture_filename:
                    delete_image(item.picture_filename)
                filename = secure_filename(picture_filename.filename)
                if os.path.isdir(app.config['UPLOAD_FOLDER']) is False:
                    os.mkdir(app.config['UPLOAD_FOLDER'])
                picture_filename.save(os.path.join(
                                      app.config['UPLOAD_FOLDER'], filename))
                item.picture_filename = filename
                item.picture_url = None
            elif not picture_filename and request.form['picture_url']:
                item.picture_url = request.form['picture_url']
                if item.picture_filename:
                    delete_image(item.picture_filename)
                    item.picture_filename = None

            session.add(item)
            session.commit()

            flash("Your hero has changed!")
            item_id = item.id
            return redirect(url_for('showItem', item_id=item_id))

        else:
            categories = categoryMenu()
            return render_template('item_edit.html',
                                   categories=categories,
                                   item=item)


@app.route('/hero/<int:item_id>/delete/', methods=['GET', 'POST'])
@login_required  # check if user is logged in
def deleteItem(item_id):
    '''Handler to delete an item.'''
    try:
        item = session.query(Item).filter_by(id=item_id).one()
    except NoResultFound:
        flash("Sorry, this hero isn't among us!")
        return redirect(url_for('mainPage'))

    author = getUserInfo(item.user_id)

    if author.id != login_session['user_id']:
        flash("Hey, you can't delete a hero that doesn't belong to you!")
        return redirect(url_for('mainPage'))
    else:
        if request.method == 'POST':
            if item.picture_filename:
                delete_image(item.picture_filename)
            session.delete(item)
            session.commit()

            user = session.query(User).filter_by(id=item.user_id).one()
            user_id = user.id
            flash("Your hero's gone! :-(")
            return redirect(url_for('showList', user_id=user_id))
        else:
            menuNav = categoryMenu()
            return render_template('item_delete.html',
                                   menuNav=menuNav,
                                   item=item)


@app.errorhandler(404)
def notFound(exc):
    '''Handler with 404 error.'''
    menuNav = categoryMenu()
    items = session.query(Item).order_by(desc(Item.id))
    return render_template('404.html',
                           menuNav=menuNav,
                           items=items
                           ), 404

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
