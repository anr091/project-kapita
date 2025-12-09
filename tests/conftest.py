"""
Test configuration and fixtures for pytest.
"""
import pytest
from unittest.mock import MagicMock, patch

# Mock MongoDB collections for testing
@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    """Mock MongoDB collections used in the application."""
    # Create a mock for each collection used in the application
    collections = {
        'productCollection': MagicMock(),
        'roleCollection': MagicMock(),
        'supplierCollection': MagicMock(),
        'retailCollection': MagicMock(),
        'inventoryCountCollection': MagicMock(),
        'productInventoryCollection': MagicMock(),
        'userCollection': MagicMock(),
        'productLogCollection': MagicMock()
    }

    # Create a module-level mock for the collections
    mock_module = MagicMock()
    for name, mock in collections.items():
        setattr(mock_module, name, mock)
    
    # Patch the module to return our mock collections
    with patch.dict('sys.modules', {'common.MongoConnection': mock_module}):
        # Re-import the module to apply the patch
        import common.api_controller
        yield collections

# Mock Flask application context
@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    from flask import Flask
    from common.api_controller import API_BP
    
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(API_BP)
    return app

# Test client
@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

# Mock user session
@pytest.fixture
def mock_user():
    """Mock user session."""
    return {
        'user_id': 'test_user',
        'role': 'ADMIN',
        'username': 'testuser'
    }
