from pymongo import MongoClient
from .config import *

class mongoConnection:
    def __init__(self,connectionString:str,dbName:str,collectionName:str):
        self.connection = MongoClient(connectionString)
        self.DB = self.connection[dbName]
        self.collection = self.DB[collectionName]

sessionCollection = mongoConnection(MONGODB_CONNECTION_STRING,MONGODB_AUTH_DB,MONGODB_SESSION_COLLECTION)
productCollection = mongoConnection(MONGODB_CONNECTION_STRING,MONGODB_PRODUCT_DB,MONGODB_PRODUCT_COLLECTION)
roleCollection = mongoConnection(MONGODB_CONNECTION_STRING,MONGODB_AUTH_DB,MONGODB_ROLES_COLLECTION)
userCollection = mongoConnection(MONGODB_CONNECTION_STRING,MONGODB_AUTH_DB,MONGODB_USERS_COLLECTION)
productLogCollection = mongoConnection(MONGODB_CONNECTION_STRING,MONGODB_PRODUCT_DB,MONGODB_PRODUCT_LOG_COLLECTION)
productInventoryCollection = mongoConnection(MONGODB_CONNECTION_STRING,MONGODB_PRODUCT_DB,MONGODB_PRODUCT_INVENTORY_COLLECTION)
supplierCollection = mongoConnection(MONGODB_CONNECTION_STRING,MONGODB_EXTERNAL_DB,MONGODB_SUPPLIER_COLLECTION)
shipmentLogCollection = mongoConnection(MONGODB_CONNECTION_STRING,MONGODB_EXTERNAL_DB,MONGODB_SHIPMENT_LOG_COLLECTION)
shipmentCollection = mongoConnection(MONGODB_CONNECTION_STRING,MONGODB_EXTERNAL_DB,MONGODB_SHIPMENT_COLLECTION)
retailCollection = mongoConnection(MONGODB_CONNECTION_STRING,MONGODB_EXTERNAL_DB,MONGODB_RETAIL_COLLECTION)
arrivalCollection = mongoConnection(MONGODB_CONNECTION_STRING,MONGODB_PRODUCT_DB,MONGODB_PRODUCT_ARRIVAL_COLLECTION)
inventoryCountCollection = mongoConnection(MONGODB_CONNECTION_STRING,MONGODB_PRODUCT_DB,MONGODB_PRODUCT_INVENTORY_COUNTER)

