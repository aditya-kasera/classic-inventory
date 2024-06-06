import unittest
from unittest.mock import patch
from app import mysql, app

class TestUsers(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True


    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'INVENTORY MANAGEMENT SYSTEM', response.data)


    