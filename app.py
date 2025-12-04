from flask import Flask, render_template,g
from common.config import *
from common.api_controller import dashboardDataFetch
from common.login_manager import user_bp,check_login
from common.api_controller import API_BP
from common.MongoConnection import mongoConnection
stockCollection = mongoConnection(MONGODB_CONNECTION_STRING,MONGODB_PRODUCT_DB,MONGODB_PRODUCT_COLLECTION)
roleCollection = mongoConnection(MONGODB_CONNECTION_STRING,MONGODB_AUTH_DB,MONGODB_ROLES_COLLECTION)
userCollection = mongoConnection(MONGODB_CONNECTION_STRING,MONGODB_AUTH_DB,MONGODB_USERS_COLLECTION)

app = Flask(__name__)
app.register_blueprint(user_bp)
app.register_blueprint(API_BP)
app.secret_key = "ProjectKapitaSelekta2025"

@app.route('/')
def index():
    auth_check = check_login()
    if auth_check:
        print("tidak ada session aktif")
        return auth_check
    dashboardDat = dashboardDataFetch()
    return render_template('index.html',name=g.user['name'],role=g.user['roleName'],title="Manage Product",Perm=g.user['rolePerm'],firstTime=g.user['firstLogon'],dbDat=dashboardDat)

@app.route('/management/users')
def usersManagement():
    auth_check = check_login()
    if auth_check:
        print("tidak ada session aktif")
        return auth_check
    return render_template('management_users.html',name=g.user['name'],role=g.user['roleName'],title="Users Management",Perm=g.user['rolePerm'])

@app.route('/shipments/log')
def shipmentLog():
    auth_check = check_login()
    if auth_check:
        print("tidak ada session aktif")
        return auth_check
    return render_template('shipmentAndArrival.html',name=g.user['name'],role=g.user['roleName'],title="Shipments and Arrivals",Perm=g.user['rolePerm'])

@app.route('/retail-supply')
def retailSupply():
    auth_check = check_login()
    if auth_check:
        print("tidak ada session aktif")
        return auth_check
    return render_template('retailAndSupply.html',name=g.user['name'],role=g.user['roleName'],title="Supply and Retail",Perm=g.user['rolePerm'])

@app.route('/management/product')
def dashboard():
    auth_check = check_login()
    if auth_check:
        print("tidak ada session aktif")
        return auth_check
    return render_template('management_product.html',name=g.user['name'],role=g.user['roleName'],title="Dashboard",Perm=g.user['rolePerm'])

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")