from .config import *
from argon2 import PasswordHasher
import datetime
from flask import jsonify
from .MongoConnection import mongoConnection
hasher = PasswordHasher()
usersConnect = mongoConnection(MONGODB_CONNECTION_STRING,MONGODB_AUTH_DB,MONGODB_USERS_COLLECTION)
rolesConnect = mongoConnection(MONGODB_CONNECTION_STRING,MONGODB_AUTH_DB,MONGODB_ROLES_COLLECTION)
class accountCreator:
    def __init__(self):
        latestDate = datetime.datetime.now()
        year_prefix = f"P{latestDate.year}"
        cursor = usersConnect.collection.find({"_id": {"$regex": f"^{year_prefix}"}}, {"_id": 1})
        maxId = 0
        for doc in cursor:
            suffix = doc["_id"][len(year_prefix):]
            if suffix.isdigit():
                num = int(suffix)
                if num > maxId:
                    maxId = num
        self.newId = f"{year_prefix}{maxId+1:03d}"
        return None
    def crateAccount(self,NDepan:str,NBelakang:str,email:str,noTelp:str,pw:str,role:str,immediateInput=False) -> dict:
        userData = {
            "_id": self.newId,
            "namaDepan": NDepan,
            "namaBelakang":NBelakang,
            "email":email,
            "noTelp":noTelp,
            "status":"active",
            "password": hasher.hash(pw),
            "role": role,
            "createdAt":datetime.datetime.now(),
            "lastLogin":None
        }
        print("Created successfully") #debug
        if immediateInput:
            self.inputCreated(userData)
        return userData
    def inputCreated(self,userDat:dict):
        creator = usersConnect.collection.insert_one(userDat)
        if creator:
            print("Account Inserted to database")
            return jsonify({'message':'created successfully'}),201
        return jsonify({'message':'error when inputing account'}),500
    
