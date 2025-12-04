""" CONNECTION """
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