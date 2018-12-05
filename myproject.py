from flask import Flask, render_template, request, redirect, url_for,jsonify,make_response,flash,session as login_session,make_response
import random,string
from sqlalchemy.orm import sessionmaker
import requests
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from storedb_setup import Base, Product, ProductType, User
from oauth2client.client import flow_from_clientsecrets,FlowExchangeError
import httplib2
import requests
from validate_email import validate_email
import bcrypt
 

CLIENT_ID = json.loads(open('client_secrets.json','r').read())['web']['client_id']
engine = create_engine('sqlite:///nasserzon.db?check_same_thread=false')
Base.metadata.bind = engine

DBsession = sessionmaker(bind=engine)
session = DBsession()
app = Flask(__name__)

def GetUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    return user
def GetUserId(user_email):
    try:
        user = session.query(User).filter_by(email=user_email).first()
        return user.id
    except:
        return None
@app.route('/AddUsers',methods=['POST'])        
def AddUser():
    if request.method == 'POST':

        uname = request.form['username']
        password = request.form['pass']
        email = request.form['email']
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())

        if not uname or not password or not email:
            return render_template('register.html', message="All fileds are mandtory!!",uname=uname,email=email)
        if not validate_email(email):
              return render_template('register.html', message="Enter Valid Email!!",uname=uname,email=email)

        if  len(password) < 8:
             return render_template('register.html', message="Password must be Bigger than 7 chracters!!",uname=uname,email=email)

        userId = GetUserId(email)
        
        if userId :
            return render_template('register.html', message="Email Is Registed already!!",uname=uname,email=email)

        userInfo = GetUserInfo(userId)
        if userInfo:
              return render_template('register.html', message="Username Is Registed already!!",uname=uname,email=email)

        myMenueItem = User(username=request.form['username'], email=request.form['email'],
        password=hashed)
        
        session.add(myMenueItem)
        session.commit()
        redirect('/login')
    

def CreateUser(login_session):
    newUser = User(name=login_session['username'],email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id
@app.route('/register')
def register():
    return render_template('register.html', message="",uname="",email="")

@app.route('/logout')
def logout():
    gdisconnect()
    return "You have loged out"

@app.route('/',methods=['GET','POST'])
@app.route('/<string:catagorey>',methods=['GET','POST'])
def GetProducts(catagorey='All'):
     
        smartphones = []
        if catagorey and catagorey != 'All':
            ptype = session.query(ProductType).filter(ProductType.name.like(catagorey)).first()
            if ptype:
                smartphones = session.query(Product).filter_by(typeId=ptype.id).all()

        else:
            smartphones = session.query(Product).all() 
        
            
        return render_template('nasserzonmenu.html', smartphones=smartphones,count=len(smartphones))


@app.route('/login',methods=['GET','POST'])
def Login():

        state = ''.join(random.choice(string.ascii_uppercase+string.digits)for x in xrange(32))
        login_session['state'] = state
        session = DBsession()
        if request.method == 'POST':
            password = request.form['pass']
            
            email = request.form['email']
           
            if  not password or not email:
                return render_template('login.html', message="All fileds are mandtory!!",uname="",email=email)
            
            if not validate_email(email):
                  return render_template('login.html', message="Enter Valid Email!!",uname="",email=email)

            userId = GetUserId(email)
        
            if not userId :
                return render_template('login.html', message="No user found !!",uname="",email=email)

            userInfo = GetUserInfo(userId)
            
            if not userInfo:
                  return render_template('login.html', message="No user found !!",uname="",email=email)
                  
            if not userInfo.password or not bcrypt.checkpw(password.encode("utf-8"), userInfo.password):
                 return render_template('login.html', message="Wrong Password !!",uname="",email=email)

            login_session['uname'] = userInfo.username
            login_session['email'] = userInfo.username

            smartphones = session.query(Product).all() 
            return render_template('nasserzonmenu.html', smartphones=smartphones,count=len(smartphones))
       
        return render_template('login.html',STATE=state,message="",uname="",email="")

@app.route('/gconnect',methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('invalid state parameter'),401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data    

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json',scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = make_response(json.dumps('Falid to Upgrade Authrization Code'),401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)    
    h = httplib2.Http()
    result = json.loads(h.request(url,'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')),500)
        response.headers['Content-Type'] = 'application/json'
        return response
    google_id = credentials.id_token['sub']    
    if result['user_id'] != google_id:
        response = make_response(json.dumps("User Id doesn't match Token's User" ),401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client Id doesn't match App ID"),401)
        print ("Token's client Id doesn't match App ID")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_google_id = login_session.get('gplus_id')
    if stored_access_token is not None and google_id == stored_google_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = stored_google_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    currentuser = GetUserId(data['email'])
    if not currentuser:
        currentuser = CreateUser(login_session)
    login_session['user_id'] = currentuser  

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output   
    
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print ('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print( 'In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print ('result is ')
    print (result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

    

@app.route('/Search')
def Search():
   
    keyword = request.args.get('keyword')
    
    smartphones = session.query(Product).filter(Product.name.like("%"+keyword+"%")).all()
    for smartphone in smartphones:
                x = "https://via.placeholder.com/200/"
                smartphone.desc = x    

    return render_template('nasserzonmenu.html', smartphones=smartphones,count=len(smartphones))

@app.route('/Add',methods=['get','post'])
def Add():
    if 'username' not in login_session :
        redirect('/login')

  
    if request.method == 'POST':
        
        myMenueItem = Product(name=request.form['name'], price=request.form['price'],
        desc=request.form['desc'], typeId=request.form['ptype'])
        
        session.add(myMenueItem)
        session.commit()
        
        
        return redirect(url_for('GetProducts'))

    ptypes = session.query(ProductType).all()

    return render_template('additem.html',ptypes=ptypes)

@app.route('/Edit/<int:id>',methods=['GET','POST'])
def Edit(id):

    if 'username' not in login_session :
        redirect('/login')
        
   
    myMenueItem = session.query(Product).filter_by(id=id).first()
    
    if request.method == 'POST':

        myMenueItem.name=request.form['name']
        myMenueItem.price=request.form['price']
        myMenueItem.desc=request.form['desc']
        myMenueItem.typeId=request.form['ptype']

        session.commit()
        
        
        return redirect(url_for('GetProducts'))

    ptypes = session.query(ProductType).all()
    

    return render_template('edititme.html',ptypes=ptypes,product=myMenueItem)

@app.route('/Show/<int:id>')
def Show(id):
    
    myMenueItem = session.query(Product).filter_by(id=id).first()
    ptypes = session.query(ProductType).all()
    

    return render_template('showitem.html',ptypes=ptypes,item=myMenueItem)

@app.route('/Delete/<int:id>',methods=['POST'])
def Delete(id):
    if 'username' not in login_session :
        redirect('/login')
  
    myMenueItem = session.query(Product).filter_by(id=id).first()
    if request.method == 'POST':
        
        session.delete(myMenueItem)
        session.commit()
        
        
        return redirect(url_for('GetProducts'))

@app.route('/hello')
def HelloWordl():
    
    x = json.dumps(getPhoto().json()['hits'][0]['webformatURL'])
    
    n = '''
            <html>
                <body>
                <img src=%s>
                </body>
            </html>
            '''
    response = "".join(n % x)
    
    return response
    return x.hits[0]
    restaurant = session.query(ProductType).first()
    items = session.query(ProductType).filter_by(restaurant_id=restaurant.id)
    if restaurant is None or not items:
        return "No resturant found"

    return render_template('menu.html', restaurant=restaurant, items=items)


@app.route('/menu/<int:res_id>/')
def GetMenu(res_id):
    restaurant = session.query(ProductType).filter_by(id=res_id).first()
    items = session.query(ProductType).filter_by(restaurant_id=restaurant.id)

    if restaurant is None or not items:
        return "No restaurant found"

    return render_template('menu.html', restaurant=restaurant, items=items)



def deleteMenuItem(restaurant_id, menu_id):
    return "page to delete a menu item. Task 3 complete!"

def getPhoto(name):
    res = requests.get('https://pixabay.com/api/?key=10821391-42c0faabd31442d2f044a4eb5&q='+name+'&image_type=photo')
    if res.ok:
        return res
        

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
