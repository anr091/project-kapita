"""
Application Configuration Module

This module contains all the configuration settings and constants used throughout the application.
It includes database connection strings, collection names, and other configuration parameters.

Configuration Sections:
    - CONNECTION: Main database connection string
    - DB AUTH: Authentication-related database and collection names
    - DB PRODUCT: Product-related database and collection names
    - DB EXTERNAL: External service-related database and collection names

Security Note:
    - This file contains sensitive information like database credentials.
    - In a production environment, consider using environment variables or a secure
      configuration management system instead of hardcoded values.

Dependencies:
    - None (this is a configuration-only module)
"""

# CONNECTION
""" MongoDB connection string for the main database cluster """
MONGODB_CONNECTION_STRING = "mongodb+srv://672023173:672023173@cluster0.361agam.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

""" DB AUTH """
MONGODB_AUTH_DB = "pj-kapita-auth"
MONGODB_USERS_COLLECTION = "users"
MONGODB_SESSION_COLLECTION = "sessions"
MONGODB_ROLES_COLLECTION = "roles-manager"

""" DB PRODUCT """
MONGODB_PRODUCT_DB = "pj-kapita-products"
MONGODB_PRODUCT_COLLECTION = 'products'
MONGODB_PRODUCT_LOG_COLLECTION = 'products-log'
MONGODB_PRODUCT_ARRIVAL_COLLECTION = 'products-arrival-report'
MONGODB_PRODUCT_INVENTORY_COLLECTION = 'product-inventory'
MONGODB_PRODUCT_INVENTORY_COUNTER = 'product-inventory-log'

""" DB EXTERNAL """
MONGODB_EXTERNAL_DB = "pj-kapita-external"
MONGODB_SUPPLIER_COLLECTION = "supplier"
MONGODB_SHIPMENT_LOG_COLLECTION = "shipment_log"
MONGODB_SHIPMENT_COLLECTION = "shipment"
MONGODB_RETAIL_COLLECTION = "retail"