"""
MongoDB Connection Handler

This module provides a simplified interface for connecting to MongoDB collections.
It initializes and manages connections to various MongoDB collections used throughout the application.

The module creates a mongoConnection class that wraps PyMongo's functionality and provides
pre-configured connections to all required collections.

Classes:
    mongoConnection: A wrapper class for MongoDB collection connections.

Global Variables:
    sessionCollection: MongoDB collection for session management
    productCollection: MongoDB collection for product data
    roleCollection: MongoDB collection for user roles and permissions
    userCollection: MongoDB collection for user accounts
    productLogCollection: MongoDB collection for product change logs
    productInventoryCollection: MongoDB collection for inventory data
    supplierCollection: MongoDB collection for supplier information
    shipmentLogCollection: MongoDB collection for shipment logs
    shipmentCollection: MongoDB collection for shipment data
    retailCollection: MongoDB collection for retail information
    arrivalCollection: MongoDB collection for product arrivals
    inventoryCountCollection: MongoDB collection for inventory counts

Dependencies:
    - pymongo: MongoDB Python driver
    - config: Local module containing database configuration
"""

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

