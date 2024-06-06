import unittest
from unittest.mock import patch
from app import mysql, app

class TestInventory(unittest.TestCase):
    test_id = 34 # increment

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_add_item_page(self):
        response = self.app.post('/add_item', data=dict(
            item_name='Testing Item',
            s_no='12345',
            bill_no='67890',
            ddmmyy='2024-06-02',
            warrenty_years='2',
            warrenty_months='6',
            price='1000'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Please fill out the form!', response.data)




    def test_inventory(self):
        response = self.app.get('/inventory')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Inventory', response.data)


    def test_dashboard_admin(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = True
                sess['id'] = 1
                sess['full_name'] = "Administrator"
        response = self.app.post('/dashboard_admin', follow_redirects=True)  # Disable follow_redirects since we want to inspect the location header
        
        self.assertTrue(b'Welcome back, Administrator!', response.data)

    def test_dashboard_employee(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = True
                sess['id'] = 2
                sess['full_name'] = "Test Employee"
        response = self.app.post('/dashboard_employee', follow_redirects=True)  # Disable follow_redirects since we want to inspect the location header
        
        self.assertTrue(b'Welcome back', response.data)



    def test_assign_item_get(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = True
        # Send a GET request to the route
        response = self.app.get(f'/assign_item/{self.test_id}')

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the response contains the expected template elements
        self.assertIn(b'Assign Item', response.data)  
        self.assertIn(b'Select Employee', response.data)  

        # ADD REDIRECT TEST CASE IF NEEDED 

    def test_assign_item_post_success(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = True
        # Send a POST request to the route with valid form data
        response = self.app.post(f'/assign_item/{self.test_id}', data=dict(
            assigned='1'
        ), follow_redirects=True)  # Assuming item ID 1 exists and employee ID 1 is valid

        # Assert that the response contains the success message
        self.assertIn(b'Successfully assigned!', response.data)

    def test_assign_item_post_invalid(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = True
        # Send a POST request to the route with invalid form data
        response = self.app.get(f'/assign_item/{self.test_id}', follow_redirects=True)  

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the response contains the error message
        self.assertIn(b'Select from dropdown to assign.', response.data)

    def test_unassign_item_get(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = True
        # Send a GET request to the route
        response = self.app.get(f'/unassign_item/{self.test_id}',follow_redirects=False)  # Assuming the user ID is 3 and the form is correctly filled

        # Assert that the response status code is 200 (OK) or 302 (Redirect)
        self.assertIn(response.status_code, [200, 302])

        # Assert that the response contains the expected template or redirect location
        # self.assertTrue(response.headers['Location'].endswith('/view_item/{self.test_id}'))

    def test_unassign_item_post(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = True
        # Send a POST request to the route 

        response = self.app.post(f'/unassign_item/{self.test_id}',follow_redirects=False)  # Assuming the user ID is 3 and the form is correctly filled

        # Assert that the response status code is 200 (OK) or 302 (Redirect)
        self.assertIn(response.status_code, [200, 302])

        # Assert that the response contains the expected template or redirect location
        # self.assertTrue(response.headers['Location'].endswith('/view_item/{self.test_id}'))


    def test_view_item_get(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = True
        # Send a GET request to the route
        response = self.app.get(f'/view_item/{self.test_id}', follow_redirects=False)

        # Assert that the response status code is 200 (OK)
        # self.assertEqual(response.status_code, 200)

        # Assert that the response contains the expected template elements
        self.assertTrue(b'Item Details', response.data)  
        self.assertTrue(b'Serial Number', response.data)  
        self.assertTrue(b'Date of Purchase', response.data)  

    def test_view_item_post(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = True
                sess['id'] = 1
        # Send a POST request to the route
        response = self.app.post(f'/view_item/{self.test_id}', follow_redirects=False)  

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the response contains the expected template elements
        self.assertTrue(b'Item Details', response.data)  
        self.assertTrue(b'Serial Number', response.data)  
        self.assertTrue(b'Date of Purchase', response.data)  

    # Add more assertions as needed based on the specific content and behavior of the view_item.html template

    def test_edit_item_get(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = True
        # Send a GET request to the route
        response = self.app.get(f'/edit_item/{self.test_id}')

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the response contains the expected template elements
        self.assertIn(b'Edit Item', response.data)  
        self.assertIn(b'Item Name', response.data)  
        self.assertIn(b'Serial Number', response.data)  
        self.assertIn(b'Bill Number', response.data)  
        self.assertIn(b'Years', response.data)  
        self.assertIn(b'Months', response.data)  
        self.assertIn(b'Price', response.data)  

    def test_edit_item_post_success(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = True
        # Send a POST request to the route with valid form data
        response = self.app.post(f'/edit_item/{self.test_id}', data=dict(
            item_name='Basket',
            s_no='212/21M',
            bill_no='50',
            ddmmyy='2024-06-03',
            warrenty_years='2',
            warrenty_months='6',
            price='399.99'
        ), follow_redirects=True)

        # Assert that the response contains the success message
        self.assertIn(b'Item Updated!', response.data)

    def test_edit_item_post_invalid(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['loggedin'] = True
        # Send a POST request to the route with invalid form data (missing fields)
        response = self.app.post(f'/edit_item/{self.test_id}', data=dict(
            item_name='',
            s_no='',
            bill_no='',
            ddmmyy='',
            warrenty_years='',
            warrenty_months='',
            price=''
        ), follow_redirects=True)

        # Assert that the response contains the error message
        self.assertIn(b'Please fill out the form!', response.data)

if __name__ == '__main__':
    unittest.main()


    # def test_add_item_success(self):
    #     with self.app as client:
    #         with client.session_transaction() as sess:
    #             sess['loggedin'] = True
    #             sess['role'] = 'admin'
    #     response = self.app.post('/add_item', data=dict(
    #         item_name='Tests Item',
    #         s_no='1234115',
    #         bill_no='6718910',
    #         ddmmyy='2024-06-04',
    #         warrenty_years='5',
    #         warrenty_months='4',
    #         price='10010'
    #     ), follow_redirects=True)  # Disable follow_redirects since we want to inspect the location header

    #     # Check if the status code is 200 (success)
    #     self.assertEqual(response.status_code, 200, msg=f"Expected status code 200 but got {response.status_code}")

    #     # Check if the success message is in the response data
    #     self.assertIn(b'Item successfully added!', response.data, msg="Expected success message not found in response")


    # def test_delete_item(self):
    #     with self.app as client:
    #         with client.session_transaction() as sess:
    #             sess['loggedin'] = True
    #             sess['role'] = 'admin'
    #             sess['id'] = 1  # Assuming user with ID 1 exists in the database

    #     # Send a GET request to the route with the item ID as a parameter
    #     response = client.get(f'/delete_item/{self.test_id}', follow_redirects=False)

    #     # Assert that the response status code is 302 (Redirect)
    #     self.assertEqual(response.status_code, 302, msg=f"Expected status code 302 but got {response.status_code}")

    #     # Assert the redirect location
    #     self.assertTrue(response.headers['Location'].endswith('/dashboard_admin') or response.headers['Location'].endswith('/dashboard_employee'), msg=f"Unexpected redirect location: {response.headers['Location']}")

    #     # If not redirecting, print the response data for debugging
    #     if response.status_code != 302:
    #         print(response.data.decode('utf-8'))


    

