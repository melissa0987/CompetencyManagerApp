### IMPORTANT setup.sql must be run before using tests

import flask_unittest
from CompetencyManager import create_app
from CompetencyManager.element import Element
from CompetencyManager.dbmanager import get_db

class TestForElementApi(flask_unittest.ClientTestCase):
    
    app = create_app()

    # TESTS FOR POSTING A ELEMENT

    def test_post_element_given_invalid_json(self, client):
        bad_formatted_element = {'ElementOreder' : "", 'a' : ""}
        response = client.post('/api/v1/elements', json=bad_formatted_element)

        # checking that 400 was returned, and error message is present
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json)

    def test_post_element_successful(self, client):
        new_element = Element(elementOrder = 1, elementName="NEW ELEM", elementCriteria="CRITERIA", elementID=64, competencyID="00SH")
        post_response = client.post('/api/v1/elements', json=new_element.to_dict())
        # checking that the element added was the one provided, and the status code
        self.assertEqual(post_response.status_code, 201)


    # TESTS FOR GETTING ALL ELEMENTS (AND PAGINATION TESTS)

    def test_get_elements_given_invalid_page_parameter(self, client):
        response = client.get('/api/v1/elements?page=abc')
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json)

    def test_get_elements_given_non_existing_page(self, client):
        response = client.get('/api/v1/elements?page=6789')
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(response.json)

    def test_get_elements_successful_no_page_specified(self, client):
        response = client.get('/api/v1/elements')
        json = response.json
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(json)
        self.assertIsNotNone(json['results'])
        self.assertIsNotNone(json['next_page'])
        self.assertIsNone(json['previous_page'])

    def test_get_elements_successful_given_valid_page(self, client):
        response = client.get('/api/v1/elements?page=1')
        json = response.json
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(json)
        self.assertIsNotNone(json['results'])
        self.assertIsNotNone(json['next_page'])
        self.assertIsNone(json['previous_page'])


    # TESTS FOR GETTING A SPECIFIC ELEMENT

    def test_get_element_given_non_existing_element_id(self, client):
        client.delete('/api/v1/elements/99')
        response = client.get('/api/v1/elements/99')
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(response.json)

    def test_get_element_successful(self, client):
        response = client.get('/api/v1/elements/2')    
        json = response.json
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(json)
        self.assertIsNotNone(json['elementOrder'])
        self.assertIsNotNone(json['elementName'])
        self.assertIsNotNone(json['elementCriteria'])
        self.assertIsNotNone(json['elementID'])
        self.assertIsNotNone(json['competencyID'])


    # TESTS FOR DELETING A ELEMENT

    def test_delete_element_successful(self, client):
        ## deleteing and checking status code
        response = client.delete('/api/v1/elements/3')
        self.assertEqual(response.status_code, 204)

        ## checking if element exists
        response = client.get('/api/v1/elements/3')
        self.assertEqual(response.status_code, 404)

    
    # TESTS FOR PUTTING A ELEMENT

    def test_put_element_given_invalid_json(self, client):
        bad_formatted_element = {'ElementID' : "XXX-XXX-XX", 'description' : "ELEMENT DESCRIPTION", 'domainID' : 1, 'termID' : 1}
        response = client.put('/api/v1/elements/AAAAAAAAAA', json=bad_formatted_element)

        # Ensuring correct status code and json error message is present
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json)
    
    def test_put_element_update_successful(self, client):
        element_to_update = Element(elementOrder = 5, elementName="NEW ELEM", elementCriteria="CRITERIA", elementID=78, competencyID="00SH")

        # updating the element in the db
        response = client.put('/api/v1/elements/5', json=element_to_update.to_dict())

        self.assertEqual(response.status_code, 204)

    def test_put_element_post_successful(self, client):
        new_element = Element(elementOrder = 5, elementName="NEW ELEM", elementCriteria="CRITERIA", elementID=78, competencyID="00SH")
        response = client.put('/api/v1/elements/88', json=new_element.to_dict())

        # checking that the element added was the one provided, and the status code
        self.assertEqual(response.status_code, 201)