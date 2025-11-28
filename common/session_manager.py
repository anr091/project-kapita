import jwt 
from .MongoConnection import mongoConnection
from .config import *
from datetime import datetime,timedelta,timezone
from .MongoConnection import mongoConnection
rolesManConnect = mongoConnection(MONGODB_CONNECTION_STRING,MONGODB_AUTH_DB,MONGODB_ROLES_COLLECTION)
sessionConnect = mongoConnection(MONGODB_CONNECTION_STRING,MONGODB_AUTH_DB,MONGODB_SESSION_COLLECTION)
WIB_OFFSET = timezone(timedelta(hours=7), name='WIB')
class SessionManager:
    def __init__(self):
        self.authMongo = mongoConnection(MONGODB_CONNECTION_STRING,MONGODB_AUTH_DB,MONGODB_SESSION_COLLECTION)
        self.secret_key = "secret_key_kapita_2025"

    def generate_token(self,username,role,firstTime,id):
        today = datetime.now(WIB_OFFSET).date()
        cutoff_datetime = datetime(today.year, today.month, today.day, tzinfo=WIB_OFFSET)
        result = sessionConnect.collection.delete_many({
                "expires_at": {"$lt": cutoff_datetime}
            })
        if result:
            print(f"Purge Data: {result.deleted_count} dari old session")
        now = datetime.now(WIB_OFFSET)
        roleData = rolesManConnect.collection.find_one({'_id':role})
        payload = {
            "name" : username,
            "role" : role,
            "roleName":roleData['role-name'],
            "rolePerm":roleData['permission'],
            "id":id,
            "firstLogon":firstTime,
            'exp': now + timedelta(hours=12),
            'iat': now
        }
        token = jwt.encode(payload,self.secret_key,algorithm="HS256")
        session_data = {
            "username":username,
            "role":role,
            "token":token,
            "created_at":now,
            "expires_at":payload['exp']
        }
        self.authMongo.collection.insert_one(session_data)
        return token
    def verify_token(self,token):
        try:
            session = self.authMongo.collection.find_one({"token":token})
            if session is None:
                return None
            #mastiin apakah token masih valid
            payload = jwt.decode(token,self.secret_key,algorithms=['HS256'])
            payload['roleName'] = rolesManConnect.collection.find_one({'_id':payload['role']})['role-name']
            return payload
        except jwt.ExpiredSignatureError:
            self.remove_token(token)
            print(f"token expired: {token}")
            return None
        except jwt.InvalidTokenError:
            print(f"Token invalid: {token}")
            return None
        except Exception as e:
            print(f"error verifying token: {e}")
            return None
    
    def remove_token(self, token):
        try:
            self.authMongo.collection.delete_one({"token": token})
        except Exception as e:
            print(f"error at deleting token {e}")
            return None
