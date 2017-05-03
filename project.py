# project.py
# Udacity FSND ItemCatalog project
# author: Zhanwen Chen

from functools import wraps
from flask import Flask, render_template, g, request, redirect, jsonify, \
    url_for, flash, make_response
from flask import session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item
import random
import string
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError, \
    AccessTokenCredentials
import httplib2
import json
import requests
import sys

NUM_OF_LATEST_ITEMS = 6 # number of latest items to display

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"

# Connect to Database and create database session
engine = create_engine('postgresql://catalog:items@localhost:5432/items')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Helpers
# for Py3, use range instead of xrange
if sys.version_info >= (3, 0):
    def xrange(*args, **kwargs):
        return iter(range(*args, **kwargs))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You are not allowed to access there")
            return redirect('/login')
    return decorated_function


def get_pic():
    return login_session['picture'] if 'picture' in login_session else None


# Routes
@app.route('/login')
def showLogin():
    # Create anti-forgery state token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v3/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode("utf8"))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']

    if result['sub'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['aud'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the user is not already logged in.
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    # do not store credentials. Only access tokens!
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<h1>\n\n %s \n\n</h1>' % login_session
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px; \
        -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])

    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s' % access_token
    if access_token is None:
    	response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    print("url is " + url)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['access_token']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['access_token']
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Category Information
@app.route('/category/<int:category_id>/item/JSON')
def itemcatalogJSON(category_id):
    # category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(
        category_id=category_id).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/category/<int:category_id>/item/<int:item_id>/JSON')
def itemJSON(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)


@app.route('/category/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


# Show all categories
@app.route('/')
def showAllCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    latestItems = session.query(Item).order_by(asc(Item.name)).limit(
        NUM_OF_LATEST_ITEMS)
    return render_template('categories.html', categories=categories,
                            latestItems=latestItems, login_picture=get_pic())


# Show all of one category's items
@app.route('/category/<int:category_id>/')
def showSingleCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(
        category_id=category_id).all()
    return render_template('items.html', items=items, category=category,
                                login_picture=get_pic(),
                                user_email=login_session['email'] \
                                    if 'email' in login_session else None)


# Create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
@login_required
def newCategory():
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showAllCategories'))
    else:
        return render_template('newCategory.html', login_picture=get_pic())


# Edit a category
@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
@login_required
def editCategory(category_id):
    categoryToEdit = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            categoryToEdit.name = request.form['name']
            flash('Successfully Edited Category %s' % categoryToEdit.name)
            return redirect(url_for('showSingleCategory',
                                        category_id=categoryToEdit.id,
                                        login_picture=get_pic()))
    else:
        return render_template('editCategory.html',
                                    category=categoryToEdit,
                                    login_picture=get_pic())


# Delete a category
@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_id):
    categoryToDelete = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted by %s' %
            (categoryToDelete.name, login_session['email']))
        session.commit()
        return redirect(url_for('showAllCategories', category_id=category_id))
    else:
        return render_template('deleteCategory.html',
                                category=categoryToDelete,
                                category_id=category_id,
                                login_picture=get_pic())


# Show a single item
@app.route('/item/<int:item_id>')
def showSingleItem(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('item.html', item=item, login_picture=get_pic(),
                                user_email=login_session['email'] \
                                    if 'email' in login_session else None)


# Create a new item
@app.route('/category/<int:category_id>/item/new/', methods=['GET', 'POST'])
@login_required
def newItem(category_id):
    # category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=category_id,
                       creator=login_session['email'])
        session.add(newItem)
        session.commit()
        flash('New Item %s Successfully Created by %s' %
            (newItem.name, newItem.creator))
        return redirect(url_for('showSingleCategory', category_id=category_id))
    else:
        return render_template('newItem.html', category_id=category_id,
                                login_picture=get_pic())


# Edit a item
@app.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def editItem(item_id):
    editedItem = session.query(Item).filter_by(id=item_id).one()
    if editedItem.creator != login_session['email']:
        flash('You cannot edit items not created by you')
        return redirect(url_for('showSingleCategory',
                                    category_id=editedItem.category_id))
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('showSingleCategory',
                                    category_id=editedItem.category_id))
    else:
        return render_template('editItem.html',
                                    category_id=editedItem.category_id,
                                    item_id=item_id,
                                    item=editedItem,
                                    login_picture=get_pic())


# Delete an item
@app.route('/item/<int:item_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteItem(item_id):
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if itemToDelete.creator != login_session['email']:
        flash('You cannot delete items not created by you')
        return redirect(url_for('showSingleCategory',
                                    category_id=itemToDelete.category_id))
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showSingleCategory',
                                    category_id=itemToDelete.category_id))
    else:
        # on GET
        return render_template('deleteItem.html', item=itemToDelete,
                                login_picture=get_pic())


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    # app.run(host='localhost', port=8000)
    app.run()
