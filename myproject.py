from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify, make_response, flash, session, make_response
import random
import string
from sqlalchemy.orm import sessionmaker
import requests
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from storedb_setup import Base, Product, ProductType, User
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import requests
from validate_email import validate_email
import bcrypt
from datetime import timedelta, datetime
import smtplib
from email.mime.text import MIMEText


class ViewProduct(object):

    def __init__(self, name, description, price, catagorey):
        self.name = name
        self.description = description
        self.price = price
        self.catagorey = catagorey


CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']
engine = create_engine('sqlite:///nasserzon.db?check_same_thread=false')
Base.metadata.bind = engine

DBsession = sessionmaker(bind=engine)
dbsession = DBsession()
app = Flask(__name__)


def GetUserInfo(user_id):
    user = dbsession.query(User).filter_by(id=user_id).first()
    return user


def GetUserIdbyEmail(user_email):
    try:
        user = dbsession.query(User).filter_by(email=user_email).first()
        return user
    except BaseException:
        return None


def GetUserIdbyusername(username):
    try:
        user = dbsession.query(User).filter_by(username=username).first()
        return user
    except BaseException:
        return None


@app.route('/AddUsers', methods=['POST'])
def AddUser():
    if request.method == 'POST':

        uname = request.form['username']
        password = request.form['pass']
        email = request.form['email']
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        if not uname or not password or not email:
            return render_template(
                'register.html',
                message="All fileds are mandtory!!",
                uname=uname,
                email=email)

        if not validate_email(email):
            return render_template(
                'register.html',
                message="Enter Valid Email!!",
                uname=uname,
                email=email)

        if len(password) < 8:
            return render_template(
                'register.html',
                message="Password must be Bigger than 7 chracters!!",
                uname=uname,
                email=email)

        userId = GetUserIdbyEmail(email)
        userId2 = GetUserIdbyusername(uname)

        if userId:
            return render_template(
                'register.html',
                message="Email Is Registed already!!",
                uname=uname,
                email=email)
        if userId2:
            return render_template(
                'register.html',
                message="Username Is Registed already!!",
                uname=uname,
                email=email)

        myMenueItem = User(
            username=request.form['username'],
            email=request.form['email'],
            password=hashed)

        dbsession.add(myMenueItem)
        dbsession.commit()
        return redirect('/login')


def CreateUser(session):
    newUser = User(name=session['username'], email=session['email'])
    dbsession.add(newUser)
    dbsession.commit()
    user = dbsession.query(User).filter_by(email=session['email']).one()
    return user.id


@app.route('/register')
def register():
    return render_template('register.html', message="", uname="", email="")


@app.route('/restpassword/', methods=['POST'])
@app.route('/restpassword/<string:refortoke>')
def restpassword(refortoke=None):
    if refortoke:
        user = dbsession.query(User).filter_by(forgouttoken=refortoke).first()
        if not user:
            return 'Acsess Deineds'
        session['username'] = user.username
    if request.method == 'POST':

        password = request.form['password']
        repassword = request.form['repassword']
        if not password or not repassword:
            return render_template(
                'resetpassword.html',
                message="All fileds Mandatory!!")
        if password != repassword:
            return render_template(
                'resetpassword.html',
                message="Password and repassword are mismatch!!")
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        user = GetUserIdbyusername(session['username'])
        user.password = hashed
        user.forgouttoken = ""
        dbsession.commit()
        return redirect('/login')

    else:
        return render_template('resetpassword.html', message="")


@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        user = GetUserIdbyEmail(email)

        if user:
            forguttoken = bcrypt.hashpw(
                (datetime.now().strftime('%s') +
                 user.email +
                 user.username).encode("utf-8"),
                bcrypt.gensalt()).replace(
                "/",
                "")
            user.forgouttoken = forguttoken
            dbsession.commit()
            html = """
                <html>
                <head>
                </head>
                <body>
                    <h4> Hello %s</h4>
                    <p>If you need to reset your password you can reset it by
                    click the link
                    <a href="http://localhost:8000/restpassword/%s">
                    Reset Password</a>
                    If you dont request a reset link,
                    please ignore this email. </p>
                </body>
                </html>
                """

            msgview = html % (user.username, forguttoken)
            emailmsg = MIMEText(msgview, 'html')

            sender = 'nasserfj58@gmail.com'
            reciver = user.email
            emailmsg['Subject'] = 'Rest Password for %s' % (user.username)
            emailmsg['From'] = sender
            emailmsg['To'] = reciver
            # https://myaccount.google.com/lesssecureapps
            # enter to allow Access for less secure app
            # to send email with gmail stmp
            emailaccount = 'youremail@gmail.com'
            emailpassword = 'yourpassword'
            s = smtplib.SMTP_SSL('smtp.googlemail.com', 465)
            s.login(emailaccount, emailpassword)
            s.sendmail(sender, [reciver], emailmsg.as_string())
            s.quit()
            return render_template(
                "forgot.html",
                isSucsses=True,
                message="""Reset link Send sescusefully,
                Please check your email inbox"""
                )
        else:
            return render_template(
                "forgot.html",
                isSucsses=False,
                message="Wrong Email!!")

    return render_template("forgot.html", isSucsses=False, message="")


@app.route('/logout')
def logout():

    gdisconnect()
    session.clear()
    return redirect('/')


@app.route('/', methods=['GET', 'POST'])
@app.route('/<string:catagorey>', methods=['GET', 'POST'])
def GetProducts(catagorey='All'):

    smartphones = []
    if catagorey and catagorey != 'All':
        ptype = dbsession.query(ProductType).filter(
            ProductType.name.like(catagorey)).first()
        if ptype:
            smartphones = dbsession.query(
                Product).filter_by(typeId=ptype.id).all()

    else:
        smartphones = dbsession.query(Product).all()

    return render_template(
        'nasserzonmenu.html',
        smartphones=smartphones,
        count=len(smartphones))


@app.route('/login', methods=['GET', 'POST'])
def Login():

    state = ''.join(random.choice(string.ascii_uppercase +
                                  string.digits)for x in range(32))
    session['state'] = state
    if request.method == 'POST':
        password = request.form['pass']

        email = request.form['email']

        if not password or not email:
            return render_template(
                'login.html',
                message="All fileds are mandtory!!",
                uname="",
                email=email)

        if not validate_email(email):
            return render_template(
                'login.html',
                message="Enter Valid Email!!",
                uname="",
                email=email)

        user = GetUserIdbyEmail(email)

        if not user:
            return render_template(
                'login.html',
                message="No user found !!",
                uname="",
                email=email)

        if not user.password or not bcrypt.checkpw(
                password.encode("utf-8"), user.password):
            return render_template(
                'login.html',
                message="Wrong Password !!",
                uname="",
                email=email)

        session['username'] = user.username
        session['email'] = user.email
        session['userid'] = user.id
        session.permanent = True

        return redirect('/')

    return render_template(
        'login.html',
        STATE=state,
        message="",
        uname="",
        email="")


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = make_response(json.dumps(
            'Falid to Upgrade Authrization Code'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    param = 'access_token=%s' % access_token
    url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?%s' % param
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    google_id = credentials.id_token['sub']
    if result['user_id'] != google_id:
        response = make_response(json.dumps(
            "User Id doesn't match Token's User"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's client Id doesn't match App ID"), 401)
        print("Token's client Id doesn't match App ID")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = session.get('access_token')
    stored_google_id = session.get('gplus_id')
    if stored_access_token is not None and google_id == stored_google_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the dbsession for later use.
    session['access_token'] = credentials.access_token
    session['gplus_id'] = stored_google_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    session['username'] = data['name']
    session['picture'] = data['picture']
    session['email'] = data['email']

    currentuser = GetUserIdbyEmail(data['email'])
    if not currentuser:
        currentuser = CreateUser(session)

    session['userid'] = currentuser.id

    session.permanent = True

    output = ''
    output += '<h1>Welcome, '
    output += session['username']
    output += '!</h1>'
    flash("you are now logged in as %s" % session['username'])
    print("done!")
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'
    h = httplib2.Http()
    result = h.request(url % session['access_token'], 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del session['access_token']
        del session['gplus_id']
        del session['username']
        del session['email']
        del session['picture']
        del session['userid']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/Search')
def Search():

    keyword = request.args.get('keyword')

    smartphones = dbsession.query(Product).filter(
        Product.name.like("%" + keyword + "%")).all()

    return render_template(
        'nasserzonmenu.html',
        smartphones=smartphones,
        count=len(smartphones))


@app.route('/Add', methods=['get', 'post'])
def Add():
    if 'username' not in session:
        redirect('/login')

    if request.method == 'POST':

        myMenueItem = Product(
            name=request.form['name'],
            price=request.form['price'],
            desc=request.form['desc'],
            typeId=request.form['ptype'],
            userId=session['userid'])

        dbsession.add(myMenueItem)
        dbsession.commit()

        return redirect(url_for('GetProducts'))

    ptypes = dbsession.query(ProductType).all()

    return render_template('additem.html', ptypes=ptypes)


@app.route('/Edit/<int:id>', methods=['GET', 'POST'])
def Edit(id):

    if 'username' not in session or 'userid' not in session:
        return redirect('/login')

    userid = session['userid']
    myMenueItem = dbsession.query(Product).filter_by(id=id).first()

    if myMenueItem.userId != userid:
        return "You dont have acsses !!s"

    if request.method == 'POST':

        myMenueItem.name = request.form['name']
        myMenueItem.price = request.form['price']
        myMenueItem.desc = request.form['desc']
        myMenueItem.typeId = request.form['ptype']

        dbsession.commit()

        return redirect(url_for('GetProducts'))

    ptypes = dbsession.query(ProductType).all()

    return render_template('edititme.html', ptypes=ptypes, product=myMenueItem)


@app.route('/Show/<int:id>')
def Show(id):

    myMenueItem = dbsession.query(Product).filter_by(id=id).first()
    ptypes = dbsession.query(ProductType).all()

    return render_template('showitem.html', ptypes=ptypes, item=myMenueItem)


@app.route('/Delete/<int:id>', methods=['POST'])
def Delete(id):
    if 'username' not in session or 'userid' not in session:
        return redirect('/login')

    userid = session['userid']

    myMenueItem = dbsession.query(Product).filter_by(id=id).first()

    if myMenueItem.userId != userid:
        return redirect('/login')

    if request.method == 'POST':

        dbsession.delete(myMenueItem)
        dbsession.commit()

        return redirect(url_for('GetProducts'))


@app.route('/api/get/products/')
@app.route('/api/get/products/<string:catagorey>/')
def GetAllProducts(catagorey='All'):
    jsonProducts = []
    products = []
    if catagorey and catagorey != 'All':
        ptype = dbsession.query(ProductType).filter(
            ProductType.name.like(catagorey)).first()
        if ptype:
            products = dbsession.query(
                Product).filter_by(typeId=ptype.id).all()
    else:
        products = dbsession.query(Product).all()
    for product in products:
        ptype = dbsession.query(ProductType).filter_by(
            id=product.typeId).first()
        if ptype:
            prodType = ptype.name
        else:
            prodType = ""

        obj = ViewProduct(product.name, product.desc,
                          str(product.price), prodType)
        jsonProducts.append(json.dumps(obj.__dict__))

    return jsonify(jsonProducts)


@app.route('/api/get/product/')
@app.route('/api/get/product/<string:name>/')
def GetProduct(name=None):

    if name:
        product = dbsession.query(Product).filter(
            Product.name.like(name)).first()
        if product:
            ptype = ptype = dbsession.query(
                ProductType).filter_by(id=product.typeId).first()
            if ptype:
                prodType = ptype.name
            else:
                prodType = ""

            obj = ViewProduct(product.name, product.desc,
                              str(product.price), prodType)

            return json.dumps(obj.__dict__)

    return jsonify(name="", description="", price="", type="")


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)
    app.run(host='0.0.0.0', port=8000)
