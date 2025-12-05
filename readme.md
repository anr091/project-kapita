# Werehouse Management System

A comprehensive inventory and user management system built with Python Flask and MongoDB.

## Features

- **User Authentication**

  - Secure login/logout functionality
  - Role-based access control
  - Password hashing with Argon2
  - Session management with JWT

- **Product Management**

  - Add, edit, and delete products
  - Track product inventory
  - Product categorization
  - Inventory logging

- **Supplier & Retailer Management**

  - Manage supplier information
  - Track retailer details
  - Shipment management
  - Arrival reports

- **Reporting**
  - Inventory tracking
  - Sales and shipment reports
  - User activity logs

## Tech Stack

- **Backend**: Python 3.x
- **Web Framework**: Flask
- **Database**: MongoDB
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: Argon2
- **Frontend**: Webix (based on the code structure)

## Project Structure

```
common/
├── api_controller.py    # API endpoints and business logic
├── config.py           # Application configuration
├── login_manager.py    # Authentication and user management
├── MongoConnection.py  # MongoDB connection handler
└── session_manager.py  # Session management with JWT
```

## Prerequisites

- Python 3.7+
- MongoDB (local or remote instance)
- pip (Python package manager)

## Installation

1. Clone the repository:

   ```bash
   git clone [your-repository-url]
   cd 672023173
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure the application:

   - Update the MongoDB connection string in `common/config.py`
   - Configure other settings as needed

5. Run the application:
   ```bash
   python app.py
   ```

## Configuration

All configuration settings are stored in `common/config.py`. Key configurations include:

- MongoDB connection string
- Database and collection names
- Session settings
- Security settings

## API Documentation

### Authentication

- `POST /users/login` - User login
- `POST /users/logout` - User logout
- `POST /users/api/register` - Register new user (admin only)

### Products

- `GET /api/products` - Get all products
- `POST /api/products` - Create new product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product

### Inventory

- `GET /api/inventory` - Get current inventory
- `POST /api/inventory` - Update inventory
- `GET /api/inventory/history` - Get inventory history

## Security Considerations

- All passwords are hashed using Argon2
- JWT tokens are used for session management
- Role-based access control for sensitive operations
- Session timeouts are enforced

## License

[Specify your license here]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## Support

For support, please contact [your contact information]
