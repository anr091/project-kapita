"""
Test cases for api_controller.py
"""
import os
import sys
from datetime import datetime
from unittest.mock import patch, MagicMock, ANY
from pymongo import MongoClient
import pytest
from flask import Flask, g, jsonify

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module under test
import common.api_controller as api_controller

# Test utility functions
def test_findABC():
    """Test the findABC function."""
    assert api_controller.findABC('1') == 'A'
    assert api_controller.findABC('2') == 'B'
    assert api_controller.findABC('3') == 'C'
    with pytest.raises(KeyError):
        api_controller.findABC('4')  # Test with invalid input

def test_rulesetProductCategory():
    """Test the rulesetProductCategory function."""
    assert api_controller.rulesetProductCategory('1') == 'Electronics'
    assert api_controller.rulesetProductCategory('6') == 'Consumables'
    with pytest.raises(KeyError):
        api_controller.rulesetProductCategory('7')  # Test with invalid input

def test_sanitizeForWebix():
    """Test the sanitizeForWebix function."""
    input_dict = {
        'int': 1,
        'float': 3.14,
        'bool': True,
        'str': 'test',
        'none': None
    }
    expected = {
        'int': '1',
        'float': '3.14',
        'bool': 'True',
        'str': 'test',
        'none': 'None'
    }
    assert api_controller.sanitizeForWebix(input_dict) == expected

@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    """Monkey patch the MongoDB connection module to return a mock connection."""
    mock_db = {'productCollection': MagicMock(),
               'roleCollection': MagicMock(),
               'supplierCollection': MagicMock(),
               'retailCollection': MagicMock(),
               'inventoryCountCollection': MagicMock(),
               'productInventoryCollection': MagicMock(),
               'userCollection': MagicMock(),
               'productLogCollection': MagicMock()}
    
    def mock_connection(*args, **kwargs):
        return mock_db
    
    monkeypatch.setattr('common.MongoConnection', mock_connection)
    
    yield mock_db


def test_findMaxId(mock_db):
    mock_db['productCollection'].collection.find_one.return_value = {'_id': 'PRD0001'}
    assert api_controller.findMaxId() == 1
    
    mock_db['productCollection'].collection.find_one.return_value = None
    assert api_controller.findMaxId() == 0

    mock_db['productCollection'].collection.find_one.side_effect = Exception("DB Error")
    assert api_controller.findMaxId() == 0



class TestAPIEndpoints:
    def test_products_endpoint_unauthorized(self, client, mock_db):
        with patch('common.api_controller.check_login', return_value=(jsonify({'error': 'Unauthorized'}), 401)):
            response = client.get('/api/products')
            assert response.status_code == 401

    def test_products_endpoint_authorized(self, client, mock_db):
        """Test authorized access to /api/products."""
        with patch('common.api_controller.check_login', return_value=None):
            # Mock the find method to return test data that matches the actual response format
            test_products = [{"_id":"PRD0001","barcodeEAN":"1293813102312","deskripsi":"Product Description","klasifikasi":{"analisisABC":"A","namaKategori":"Electronics"},"logistik":{"buyPrice":"4000","referensiDimensiUnitSimpanCM_PLT":"20x20x20","sellPrice":"4000"},"merk":"Product 1","namaProduk":"Product 1","satuan":{"unitJual":"pcs","unitSimpan":"box"},"statusKontrol":{"status":"Aktif","tglDibuat":"Fri, 05 Dec 2025 07:39:36 GMT"}}]
            mock_db['productCollection'].collection.find.return_value = test_products
            response = client.get('/api/products')
            assert response.status_code == 200

    def test_roles_endpoint_post_unauthorized(self, client, mock_db, app):
        """Test unauthorized POST to /api/roles."""
        with app.app_context():
            with patch('common.api_controller.check_login', return_value=None):
                # Mock g.user
                with patch('common.api_controller.g') as mock_g:
                    mock_g.user = {'role': 'USER'}
                    # Mock role check to return unauthorized
                    mock_db['roleCollection'].collection.find_one.return_value = {
                        'permission': {'account management': False}
                    }
                    
                    response = client.post('/api/roles', json={
                        'role-name': 'Test Role',
                        'permission': {'account_management': True}
                    })
                    assert response.status_code == 401


    def test_roles_endpoint_post_authorized(self, client, mock_db, app):
        """Test authorized POST to /api/roles."""
        with app.app_context():
            with patch('common.api_controller.check_login', return_value=None):
                # Mock g.user
                with patch('common.api_controller.g') as mock_g:
                    mock_g.user = {'role': 'ADMIN'}
                    # Mock role check to return authorized
                    mock_db['roleCollection'].collection.find_one.return_value = {
                        '_id':'R001','role-name':'Admin','permission':{'retail and shipment':True,'account management':True,'report data':True,'stock management':True},'role-salary':20000000
                    }
                    
                    # Mock find_one for role existence check to return None (role doesn't exist)
                    mock_db['roleCollection'].collection.find_one.return_value = None
                    
                    # Mock insert_one to return success
                    mock_db['roleCollection'].collection.insert_one.return_value = MagicMock(acknowledged=True)
                    
                    response = client.post('/api/roles', json={
                        'role-name': 'Test Role',
                        'permission': {'account_management': True}
                    })
                    
                    assert response.status_code == 200


def test_dashboardDataFetch(mock_db):
    result = api_controller.dashboardDataFetch()
    assert result == {
        'suppliers': '3',
        'retails': '2',
        'items': '3',
        'totalPrice': '28000.0'
    }

def test_totalCountUpdater(mock_db):
    mock_db['inventoryCountCollection'].collection.find_one.return_value = {
        '_id': 'ITMCHRT000000001',
        'totalItems': 100,
        'date': '09-12-2025',
        'totalPrice': 5000.0
    }
    mock_db['productInventoryCollection'].collection.find.return_value = [
        {'latestStoredPrice': 100.0},
        {'latestStoredPrice': 200.0}
    ]
    
    # Test case 1: Successful update
    assert api_controller.totalCountUpdater(10) is True
    
    # Test case 2: Updating existing record
    mock_db['inventoryCountCollection'].collection.update_one.return_value = MagicMock(acknowledged=True)
    assert api_controller.totalCountUpdater(5) is True

# Test error handling
def test_error_handling(mock_db):
    """Test error handling in the API."""
    # Test findMaxId with database error
    with patch('common.api_controller.productCollection.collection.find_one', side_effect=Exception("DB Error")):
        assert api_controller.findMaxId() == 0

if __name__ == '__main__':
    pytest.main()
