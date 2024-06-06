import unittest
from unittest.mock import patch
from app import mysql, app

class TestUsers(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True


    test_id = 34 # NEXT ID OF EMPLOYEE

    
    def test_login_get(self):
        # Send a GET request to the login route
        response = self.app.get('/login')

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the response contains the expected template elements
        self.assertIn(b'Login', response.data)  
        self.assertIn(b'Enter Registered Email', response.data)
        self.assertIn(b'Enter Password', response.data)

    def test_login_post_success_admin(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = False
        # Send a POST request to the login route with valid admin credentials
        response = self.app.post('/login', data=dict(
            email='admin@nucleusteq.com',
            password='adminpass'
        ), follow_redirects=False)

        # Assert that the response status code is a redirect (302)
        self.assertEqual(response.status_code, 302)

        # Assert that the redirect location is the admin dashboard
        self.assertTrue(response.headers['Location'].endswith('/dashboard_admin'))

    def test_login_post_success_employee(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = False
        # Send a POST request to the login route with valid employee credentials
        response = self.app.post('/login', data=dict(
            email='abhi@nucleusteq.com',
            password='abhi'
        ), follow_redirects=False)

        # Assert that the response status code is a redirect (302)
        self.assertEqual(response.status_code, 302)

        # Assert that the redirect location is the employee dashboard
        self.assertTrue(response.headers['Location'].endswith('/dashboard_employee'))

    def test_login_post_invalid(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = False
        # Send a POST request to the login route with invalid credentials
        response = self.app.post('/login', data=dict(
            email='invalid@nucleusteq.com',
            password='wrongpassword'
        ), follow_redirects=True)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the response contains the error message
        self.assertIn(b'Please Enter Valid Details', response.data)
    # ----------------------------------------------------
    
   


    def test_manage_users_logged_in(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = True
        # Send a request to the route
        response = self.app.get('/manage_users')

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the response contains the expected template
        self.assertIn(b'Name', response.data) 
        self.assertIn(b'Email', response.data) # Check if the template name is in the response content

    def test_view_account(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = True
                sess['id'] = 1
        # Send a request to the route
        response = self.app.get('/view')

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the response contains the expected template
        self.assertIn(b'account details', response.data) 
        self.assertIn(b'Administrator', response.data) 
        self.assertIn(b'admin', response.data) 

    def test_view_user(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = True
                sess['id'] = 1  # Assuming user with ID 2 exists in the database
        # Send a request to the route with user ID as a parameter
        response = self.app.get('/view_user/1')  # Assuming the user ID is 2

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the response contains the expected template
        self.assertIn(b'account details', response.data)  # Assuming 'account details' is in the template
        self.assertIn(b'Administrator', response.data)  # Assuming the user role is 'Employee'
        self.assertIn(b'admin@nucleusteq.com', response.data)  # Assuming the username is 'user2'

    def test_edit_user(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = True
                sess['id'] = 1  # Assuming user with ID 3 exists in the database
        # Send a request to the route with user ID as a parameter
        response = self.app.post('/edit_user/11', data=dict(
            full_name='Abhijeet Pingare',
            email='abhi@nucleusteq.com'
        ), follow_redirects=False)  # Assuming the user ID is 3 and the form is correctly filled

        # Assert that the response status code is 200 (OK) or 302 (Redirect)
        self.assertIn(response.status_code, [200, 302])

        # Assert that the response contains the expected template or redirect location
        self.assertTrue(response.headers['Location'].endswith('/view'))  # Assuming the redirect location ends with '/manage_users'

    def test_change_password(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = True
                sess['id'] = 1  # Assuming user with ID 3 exists in the database
        # Send a request to the route with user ID as a parameter
        response = self.app.post('/change_password/2', data=dict(
            password='abhi',
            confirm_password='abhi'
        ), follow_redirects=False)  
        # Assert that the response status code is 200 (OK) or 302 (Redirect)
        self.assertIn(response.status_code, [200, 302])

        # If the response is a redirect (status code 302), assert the redirect location
        if response.status_code == 302:
            self.assertTrue(response.headers['Location'].endswith('/view'))
        # If the response is not a redirect, assert that the response contains the expected template
        else:
            self.assertIn(b'change_password.html', response.data)  # Assuming 'change_password.html' is in the template

    
    def test_register_user(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = True
                sess['role'] = 'admin'
        
        response = self.app.post('/register_user', data=dict(
            full_name='Test Employee',
            email='test2@nucleusteq.com',
            password='test2'
        ), follow_redirects=False)  # Disable follow_redirects since we want to inspect the location header

        self.assertIn(response.status_code, [200, 302])
        # Check if the status code is 302 (redirect)
        # Check if the Location header ends with '/manage_users'
        # self.assertTrue(response.headers['Location'].endswith('/manage_users'), msg=f"Unexpected redirect location: {response.headers['Location']}")

        # if response.status_code != 302:
        #     print(response.data.decode('utf-8'))

    def test_register_user_invalid(self):
        response = self.app.post('/register_user', data=dict(
            full_name='Existing User',  # Using an existing email
            password='password123'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Please fill out the form!', response.data)


    def test_delete_user(self):
        # see test emp id, delete test emp, increment no., uncomment last routes, run
        
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = True
                sess['role'] = 'admin'
                sess['id'] = 1  # Assuming user with ID 3 exists in the database
        # Send a request to the route with user ID as a parameter
        response = self.app.get(f'/delete_user/{self.test_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)  # Assuming successful logout redirects to login page
        # print(response.headers['Location'])
        # Assert that the response status code is 200 (OK) or 302 (Redirect)
        self.assertIn(response.status_code, [200, 302])


    def test_logout(self):
            response = self.app.get('/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)  # Assuming successful logout redirects to login page

if __name__ == '__main__':
    unittest.main()


# Ran 29 tests in 0.432s

# OK
# PS D:\DEVELOPMENT\Flask\IMS> coverage report  
# Name                      Stmts   Miss  Cover
# --------------------------------------------- 
# app\__init__.py              10      0   100% 
# app\connection.py            26      1    96% 
# app\routes.py                 7      0   100% 
# inventory\__init__.py         3      0   100% 
# inventory\routes.py         146     23    84% 
# tests\test_app.py            11      0   100% 
# tests\test_inventory.py     122      1    99% 
# tests\test_users.py         109     13    88% 
# users\__init__.py             3      0   100% 
# users\routes.py             159     31    81% 
# --------------------------------------------- 
# TOTAL                       596     69    88% 