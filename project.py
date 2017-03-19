## author: Zhanwen Chen
## TODO:
## 5. Login area with logout

## Tests

## showAllCategories works
## editCategory works
## deleteCateogry works
## Add item works
## Edit item works
## Delete item works

NUM_OF_LATEST_ITEMS = 6

from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item
from flask import session as login_session
import random
import string

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenCredentials
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

import sys

if sys.version_info >= (3, 0):
    def xrange(*args, **kwargs):
        return iter(range(*args, **kwargs))

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        # print
        # print('gconnect: 1. Validation complete. response = %s' % (response))
        # print
        return response

    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        # credentials.json()
        # json.dump(credentials)
        # print(credentials)

    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    # print('acess token is %s' % (access_token))
    url = ('https://www.googleapis.com/oauth2/v3/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']

    # print json.dumps(result, sort_keys=True,
                #   indent=4, separators=(',', ': '))
    if result['sub'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['aud'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        # print "Token's client ID does not match app's.s"
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the user is not already logged in.
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    ## do not store credentials. Only access tokens!
    # login_session['credentials'] = credentials
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
    output += '<h1>\n\n\n!!!!!!!!!!!!!!!!!!!!!!\n %s \n!!!!!!!!!!!!!!!!!!!!!!!\n\n\n</h1>' % login_session
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])

    return output

@app.route('/gdisconnect')
def gdisconnect():
    # print json.dumps(login_session, sort_keys=True, indent=4, separators=(',',':'))
    # print login_session['credentials'].access_token
    # print(login_session)
    access_token = login_session['access_token']
    # access_token = login_session['credentials'].access_token
    print 'In gdisconnect access token is %s' % access_token
    # print 'User name is: '
    # print login_session['username']
    if access_token is None:
 # 	print 'Access Token is None'
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    print("url is " + url)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        # del login_session
    	# del login_session['access_token']
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
        # print json.dumps(login_session, sort_keys=True, indent=4, separators=(',',':'))
    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response

# JSON APIs to view Category Information
@app.route('/category/<int:category_id>/item/JSON')
def itemcatalogJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(
        category_id=category_id).all()
    return jsonify(Items=[i.serialize for i in items])

@app.route('/category/<int:category_id>/item/<int:item_id>/JSON')
def itemJSON(category_id, item_id):
    Item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=Item.serialize)


@app.route('/category/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])

# Show all categories
@app.route('/')
# @app.route('/categories/')
def showAllCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    latestItems = session.query(Item).order_by(asc(Item.name)).limit(NUM_OF_LATEST_ITEMS)
    return render_template('categories.html', \
                            categories=categories, \
                            latestItems=latestItems, \
                            login_picture=login_session['picture'] if 'picture' in login_session else None)

# Show all of one category's items
@app.route('/category/<int:category_id>/')
# @app.route('/category/<int:category_id>/items/')
def showSingleCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(
        category_id=category_id).all()
    return render_template('items.html', \
        items=items, \
        category=category, \
        login_picture=login_session['picture'] if 'picture' in login_session else None)

# Create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showAllCategories'))
    else:
        return render_template('newCategory.html', \
            login_picture=login_session['picture'] if 'picture' in login_session else None)

# Edit a category
@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    categoryToEdit = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            categoryToEdit.name = request.form['name']
            flash('Successfully Edited Category %s' % categoryToEdit.name)
            return redirect(url_for('showSingleCategory', \
                category_id=categoryToEdit.id, \
                login_picture=login_session['picture'] if 'picture' in login_session else None))
    else:
        return render_template('editCategory.html',
            category=categoryToEdit, \
            login_picture=login_session['picture'] if 'picture' in login_session else None)

# Delete a category
@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    categoryToDelete = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name)
        session.commit()
        return redirect(url_for('showAllCategories', category_id=category_id))
    else:
        return render_template('deleteCategory.html', \
            category=categoryToDelete, \
            category_id=category_id, \
            login_picture=login_session['picture'] if 'picture' in login_session else None)

# Show a single item
@app.route('/item/<int:item_id>')
def showSingleItem(item_id):
    # category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('item.html',
        item=item, \
        login_picture=login_session['picture'] if 'picture' in login_session else None)

# Create a new item
@app.route('/category/<int:category_id>/item/new/', methods=['GET', 'POST'])
def newItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        newItem = Item(name=request.form['name'], \
                       description=request.form['description'], \
                       category_id=category_id)
        session.add(newItem)
        session.commit()
        flash('New Item %s Successfully Created' % (newItem.name))
        return redirect(url_for('showSingleCategory', category_id=category_id))
    else:
        return render_template('newItem.html', \
            category_id=category_id, \
            login_picture=login_session['picture'] if 'picture' in login_session else None)

# Edit a item
# @app.route('/category/<int:category_id>/item/<int:item_id>/edit', methods=['GET', 'POST'])
@app.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Item).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('showSingleCategory', category_id=category_id))
    else:
        return render_template('editItem.html', \
            category_id=category_id, \
            item_id=item_id, \
            item=editedItem, \
            login_picture=login_session['picture'] if 'picture' in login_session else None)

# Delete an item
# @app.route('/category/<int:category_id>/item/<int:item_id>/delete', methods=['GET', 'POST'])
@app.route('/item/<int:item_id>/delete', methods=['GET', 'POST'])
# def deleteItem(category_id, item_id):
def deleteItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')
    # category = session.query(Category).filter_by(id=category_id).one()
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Successfully Deleted')
        # return redirect(url_for('showSingleCategory', category_id=category.id))
        return redirect(url_for('showSingleCategory', category_id=itemToDelete.category_id))
    else:
        # on GET
        # return render_template('deleteItem.html', item=itemToDelete, category_id=category_id)
        return render_template('deleteItem.html', \
            item=itemToDelete, \
            login_picture=login_session['picture'] if 'picture' in login_session else None)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='localhost', port=8000)
