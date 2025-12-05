"""
Login and User Authentication Manager

This module handles user authentication, session management, and user-related operations.
It provides functionality for user login, registration, session validation, and password management.

Key Features:
- User authentication with Argon2 password hashing
- Session management with token-based authentication
- User registration and account management
- Role-based access control
- Password reset functionality

Routes:
    /users/api/register - Register a new user
    /users/login - User login endpoint
    /users/logout - User logout endpoint
    /users/roles - Get available user roles
    /users/ - Get all users (admin only)
    /users/update - Update user information
    /users/delete - Delete a user (admin only)
    /users/reset-password - Reset user password

Dependencies:
    - Flask for web framework
    - argon2-cffi for password hashing
    - MongoDB for data storage
    - Custom modules: config, session_manager, MongoConnection, user_creator
"""

import argon2
from .config import *
from .session_manager import SessionManager
from flask import Blueprint,render_template,flash,request,make_response,redirect,url_for,jsonify,g
from .MongoConnection import *
from argon2 import PasswordHasher
from datetime import datetime
from .user_creator import accountCreator
session_manager = SessionManager()
verifier = PasswordHasher()
user_bp = Blueprint('user',__name__,url_prefix='/users/')
createAccount = accountCreator()


def authenticate_user(uid,password):
    user_data = userCollection.collection.find_one({'_id':uid})
    if user_data is None:
        return None
    g.user = user_data
    try:
        if verifier.verify(g.user['password'],password):
            firstTime = False
            if g.user['lastLogin'] == None:
                firstTime = uid
            lastLogon = userCollection.collection.update_one({'_id':g.user['_id']},{'$set':{'lastLogin':datetime.now()}})
            if lastLogon is None:
                return None
            return {'username':g.user['namaDepan'],'role':g.user['role'],'firstTime':firstTime,'status':g.user['status'],'id':g.user['_id']}
        return None
    except argon2.exceptions.VerifyMismatchError:
        return None


def check_login():
    token = request.cookies.get('token')
    if not token:
        print('tidak ada token')
        return redirect(url_for('user.login'))
    session_data = session_manager.verify_token(token)
    if not session_data:
        print("token tidak valid")
        response = make_response(redirect(url_for('user.login')))
        response.set_cookie('token','',expires=0)
        return response
    g.user = session_data
    g.user['rolePerm'] = roleCollection.collection.find_one({'_id':g.user['role']})['permission']
    return None


@user_bp.route('/api/register', methods=['POST'])
def regis_user():
    if request.method == "POST":
        Auth = check_login()
        if Auth:
            return Auth
        permData = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['account management']
        if permData:
            data = request.get_json()
            account = accountCreator()
            create = account.crateAccount(data['namaDepan'],data['namaBelakang'],data['email'],data['noTelp'],data['password'],data['roles'],True)
            if create:
                return create
    return jsonify({'error':'forbidden'}),403

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    Auth = check_login()
    if Auth is None:
        return make_response(redirect(url_for('index')))
    if request.method == "POST":
        userId = request.form['uid']
        password = request.form['password']
        user = authenticate_user(userId,password)
        if user:
            if user['status'] == "non-active":
                return jsonify({"status":"error","message":"Akun sudah tidak aktif"}),401
            user.pop('status')
            token = session_manager.generate_token(**user)
            response = make_response(redirect(url_for('index')))
            response.set_cookie('token',token)
            return response
        else:
            return jsonify({'message':'Wrong Email or Passoword'}),400
    return render_template('login.html')

@user_bp.route('/logout')
def logout():
    flash('Logout berhasil!', 'success')
    token = request.cookies.get('token')
    if token:
        session_manager.remove_token(token)
    resp = make_response(redirect(url_for('user.login')))
    resp.delete_cookie('token')
    return resp

@user_bp.route('/api/rolesSelect', methods=['GET'])
def rolesSelect():
    Auth = check_login()
    if Auth:
        return Auth 
    AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['account management']
    if AuthRole:
        data = list(roleCollection.collection.find())
        out = [{"id": str(r["_id"]), "value": r.get("role-name") or r.get("role")} for r in data]
        return jsonify(out)
    return jsonify({'message':"Error Authorization Failed"}),401


@user_bp.route('/api/users',methods=['GET'])
def users():
    if request.method == "GET":
        Auth = check_login()
        if Auth:
            return Auth 
        AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['account management']
        if AuthRole:
            getSalary = list(roleCollection.collection.find())
            salaryDat = {r['_id']:r['role-salary'] for r in getSalary}
            getUser = userCollection.collection.find({}, {'password': 0})
            out = []
            for u in getUser:
                u["salary"] = "Rp."+str(salaryDat[u['role']])
                out.append(u)
            return jsonify(out)
        return jsonify({'status':'error'}),401


@user_bp.route('/api/update',methods=['POST'])
def updateUser():
    if request.method == "POST":
        try:
            Auth = check_login()
            if Auth:
                return Auth 
            AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['account management']
            if AuthRole:
                data = request.form
                userId = data.get('_id')
                action = data.get('webix_operation')
                if action == 'update':
                    updateData = {}
                    for key,value in data.items():
                        if key not in ['id','webix_operation','targetId','salary','lastLogin','delBtn']:
                            updateData[key] = value
                    if not userId:
                        return jsonify({'status':'error','text':'missing id'}),400
                    result = userCollection.collection.update_one(
                        {'_id':userId},
                        {'$set':updateData}
                    )
                    if result:
                        if userId == g.user['id']:
                            token = request.cookies.get('token')
                            session_manager.remove_token(token)
                        return jsonify({'status':'success','text':'data updated'}),200
                return jsonify({'status':'error','text':'unknown error'}),500
        except Exception as e:
            print(f"Error update: {e}")
            return jsonify({"status":"error","text":str(e)}),500


@user_bp.route('/api/delete',methods=['DELETE'])
def deleteUser():
    Auth = check_login()
    if Auth:
        return Auth
    AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['account management']
    if AuthRole:
        idForDelete = request.json
        print(g.user['id'],idForDelete['_id'])
        if g.user['id']==idForDelete['_id']:
            return jsonify({'status':'forbidden'}),403
        deletion = userCollection.collection.delete_one(idForDelete)
        if deletion: 
            return jsonify({'status':'success'}),201
    return jsonify({'message':'no Auth'}),401


@user_bp.route('/api/resetPassword',methods=['PATCH'])
def resetPassword():
    Auth = check_login()
    if Auth:
        return Auth
    if g.user['firstLogon']:
        data = request.get_json()
        newPass = verifier.hash(data['newPassword'])
        setPass = False
        if data['_id']:
            setPass = userCollection.collection.update_one({"_id":data['_id']},{'$set':{"password":newPass}})
        if setPass:
            token = request.cookies.get('token')
            session_manager.remove_token(token)
            return jsonify({'status':'success'}),201
    AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['account management']
    if AuthRole:
        data = request.get_json()
        newPass = verifier.hash(data['newPassword'])
        setPass = False
        if data['_id']:
            setPass = userCollection.collection.update_one({"_id":data['_id']},{'$set':{"password":newPass}})
        if setPass:
            return jsonify({'status':'success'}),201
    data = request.get_json()
    newPass = verifier.hash(data['newPassword'])
    setPass = False
    if data['_id']:
        setPass = userCollection.collection.update_one({"_id":data['_id']},{'$set':{"password":newPass}})
    if setPass:
        return jsonify({'status':'success'}),201
    return jsonify({'status':'error'}),500


