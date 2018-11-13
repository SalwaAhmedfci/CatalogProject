from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import *
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
#from flask_bootsrap import Bootstrap

app = Flask(__name__)

CLIENT_ID = json.loads(
open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "CatalogApp"


# Connect to Database and create database session
engine = create_engine('sqlite:///CategoryItems.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()



# User Helper Functions
def createUser(login_session):

    newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Create anti-forgery state token
@app.route('/Catalog/login')
def login():
	# Create anti-forgery state token
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
	login_session['state'] = state

	return render_template('login.html', STATE=state)

@app.route('/Catalog/logout')
def logout():
	if login_session['provider'] == 'facebook':
		fbdisconnect()
		del login_session['facebook_id']

	if login_session['provider'] == 'google':
		gdisconnect()
		del login_session['gplus_id']
		del login_session['access_token']

	del login_session['username']
	del login_session['email']
	del login_session['picture']
	del login_session['user_id']
	del login_session['provider']

	return redirect(url_for('showCategory'))


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
	# Validate anti-forgery state token
	if request.args.get('state') != login_session['state']:
	    response = make_response(json.dumps('Invalid state parameter.'), 401)
	    response.headers['Content-Type'] = 'application/json'
	    return response

	# Gets acces token
	access_token = request.data
	print ("access token received %s " % access_token)

	# Gets info from fb clients secrets
	app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
	app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']

	url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
	h = httplib2.Http()
	result = h.request(url, 'GET')[1]

	# Use token to get user info from API
	userinfo_url = "https://graph.facebook.com/v2.4/me"

    # strip expire tag from access token
	token = result.split("&")[0]

	url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
	h = httplib2.Http()
	result = h.request(url, 'GET')[1]

	data = json.loads(result)
	login_session['provider'] = 'facebook'
	login_session['username'] = data["name"]
	login_session['email'] = data["email"]
	login_session['facebook_id'] = data["id"]

	# Store token in login_session in order to logout
	stored_token = token.split("=")[1]
	login_session['access_token'] = stored_token

	# Get user picture
	url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
	h = httplib2.Http()
	result = h.request(url, 'GET')[1]
	data = json.loads(result)

	login_session['picture'] = data["data"]["url"]

	# See if user exists
	user_id = getUserID(login_session['email'])
	if not user_id:
	    user_id = createUser(login_session)
	login_session['user_id'] = user_id

	return "Login Successful!"

@app.route('/fbdisconnect')
def fbdisconnect():
	facebook_id = login_session['facebook_id']
	access_token = login_session['access_token']

	url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
	h = httplib2.Http()
	result = h.request(url, 'DELETE')[1]

	return "you have been logged out"

@app.route('/gconnect', methods=['POST'])
def gconnect():
	# Validate anti-forgery state token
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
		response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Check that the access token is valid.
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])

	# If there was an error in the access token info, abort.
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is used for the intended user.
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is valid for this app.
	if result['issued_to'] != CLIENT_ID:
		response = make_response(json.dumps("Token's client ID does not match app's."), 401)
		print ("Token's client ID does not match app's.")
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_access_token = login_session.get('access_token')
	stored_gplus_id = login_session.get('gplus_id')

	if stored_access_token is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Store the access token in the session for later use.
	login_session['access_token'] = credentials.access_token
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']
	login_session['provider'] = 'google'

	# See if user exists
	user_id = getUserID(data["email"])
	if not user_id:
	    user_id = createUser(login_session)
	login_session['user_id'] = user_id

	return "Login Successful"

@app.route('/gdisconnect')
def gdisconnect():
	# Only disconnect a connected user.
	access_token = login_session.get('access_token')

	if access_token is None:
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]

	if result['status'] != '200':
	    # For whatever reason, the given token was invalid.
	    response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
	    response.headers['Content-Type'] = 'application/json'
	    return response


###########
#JSON part#
###########
# JSON APIs to all catalog
@app.route('/Catalog/JSON')
def CatalogJSON():
    catalog = session.query(Category).all()
    return jsonify(Category=[r.serialize for r in catalog])


# JSON APIs to view Category Information with items
@app.route('/Catalog/<path:category_name>/JSON')
def CategoryItemsJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(category=category)
    return jsonify(Category=[i.serialize for i in items])






# show all categories
@app.route('/')
@app.route('/Catalog/')
def show_categories():
    category = session.query(Category)
    # printing Items of Category
    items = session.query(Items).all()
    return render_template("Categories.html", category=category,items=items)


# new category # Done
@app.route('/Catalog/new/', methods=['GET', 'POST'])
def new_category():
    # Check if user is logged in
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        new_category = Category(name=request.form['name'])
        session.add(new_category)
        return redirect(url_for('show_categories'))
    else:
        return render_template("newCategory.html")


# show Category Items # Done
@app.route('/Catalog/<path:category_name>/')
def showCategory(category_name):



    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(category=category)
    # Get creator of item
    creator = getUserInfo(category.user_id)
    return render_template("items.html", Category=category, Items=items ,creator =creator)


# edit category items


# show Item details # Done
@app.route('/Catalog/<path:category_name>/<path:item_name>/')
def show_item( category_name ,item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Items).filter_by(name=item_name).one()
    # Get creator of item
    creator = getUserInfo(items.user_id)
    return render_template("item.html", item=items, category=category.name, creator=creator)


# add new items to the category

@app.route('/Catalog/<path:category_name>/new/', methods=['GET', 'POST'])
def new_items(category_name):
    # Check if user is logged in
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    print(category.name)
    if request.method == 'POST':
        new_item = Items(name=request.form['name'],description=request.form['description'], category=category)
        session.add(new_item)
        session.commit()
        return redirect(url_for('showCategory', category_name=category.name))
    else:

     return render_template("newitems.html", category=category)


# edit the details of item # done without create


@app.route('/Catalog/<path:category_name>/<path:item_name>/edit/', methods=['GET', 'POST'])
def edit_item(category_name, item_name):
    # Check if user is logged in
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Items).filter_by(name=item_name).one()
    # Get creator of item
    creator = getUserInfo(item.user_id)

    # Check if logged in user is creator of category item
    if creator.id != login_session['user_id']:

        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        session.add(item)
        session.commit()

        return redirect(url_for('show_item',category_name=category_name, item_name=item.name))
    else:
        return render_template("edititemdetails.html", item=item, category=category)


# delete item

@app.route('/Catalog/<path:category_name>/<path:item_name>/delete/')
def delete_item(category_name, item_name):
    # Check if user is logged in
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Items).filter_by(name=item_name).one()
    # Get creator of item
    creator = getUserInfo(item.user_id)

    # Check if logged in user is creator of category item
    if creator.id != login_session['user_id']:
       return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showCategory', category_name=category.name))

    else:
        return render_template("deleteitem.html", category=category, item=item)


# delete category


@app.route('/Catalog/<path:category_name>/delete/')
def delete_Category(category_name):
    # Check if user is logged in
    if 'username' not in login_session:
        return redirect('/login')
    #item = session.query(Items).filter_by(name=item_name).one()
    category = session.query(Category).filter_by(name=category_name).one()
    if request.method == 'POST':
        session.delete(category)
        session.commit()
        flash('Category Successfully Deleted')
        return redirect(url_for('show_categories'))
    else:
        return render_template("deleteCategory.html", category=category)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(port=5000, host='localhost')



