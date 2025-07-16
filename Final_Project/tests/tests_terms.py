import flask_unittest
from CompetencyManager import create_app
from CompetencyManager.term import Term


class TestForTermApi(flask_unittest.ClientTestCase):
    app = create_app()


 # TESTS FOR GETTING ALL TERMS

    def test_get_terms_given_invalid_page_parameter(self, client):
        response = client.get('/api/v1/terms?page=abc')
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json)


    def test_get_terms_given_non_existing_page(self, client):
        response = client.get('/api/v1/terms?page=6789')
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(response.json)


    def test_get_terms_successful_no_page_specified(self, client):
        response = client.get('/api/v1/terms')
        self.assertEqual(response.status_code, 200)
        json = response.json
        self.assertIsNotNone(json)
        self.assertIsNotNone(json['results'])
        self.assertIsNotNone(json['next_page'])
        self.assertIsNone(json['previous_page'])


    def test_get_courses_successful_given_valid_page(self, client):
        response = client.get('/api/v1/terms?page=1')
        json = response.json
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(json)
        self.assertIsNotNone(json['results'])
        self.assertIsNotNone(json['next_page'])
        self.assertIsNone(json['previous_page'])




# TESTS FOR GETTING A SPECIFIC TERM

    def test_get_term_successful(self, client):
        resp = client.get(f'/api/v1/terms/3')
        self.assertEqual(resp.status_code, 200)
        json = resp.json
        self.assertIsNotNone(json['termID'])
        self.assertIsNotNone(json['termName'])

    def test_get_term_given_invalid_term_id(self, client):
        response = client.get('/api/v1/terms/25')
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(response.json)

    def test_get_term_given_non_existing_term_id(self, client):
        client.delete('/api/v1/terms/9999999999')
        response = client.get('/api/v1/terms/9999999999')
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(response.json)


    
# TESTS FOR POSTING A TERM

    def test_post_term_successful(self, client):
        new_term = Term(7, "Summer")
        response = client.post('/api/v1/terms', json=new_term.to_dict())
        self.assertEqual(response.status_code, 201)

        response = client.get('/api/v1/terms/7')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json, new_term.to_dict())
        client.delete(f'/api/v1/terms/7')

    def test_post_term_given_already_existing_term(self, client):
        new_term = Term(1, "Fall")
        response = client.post('/api/v1/terms', json=new_term.to_dict())

        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json)




# TESTS FOR DELETING A TERM

    def test_delete_term_successful(self, client):
        new_term = Term(7, "Summer")
        response = client.post('/api/v1/terms', json=new_term.to_dict())
        self.assertEqual(response.status_code, 201)
        response = client.delete(f'/api/v1/terms/7')
        self.assertEqual(response.status_code, 204)


    def test_delete_term_given_invalid_term_id(self, client):
        response = client.delete('/api/v1/terms/9')
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(response.json)


    def test_delete_term_given_non_existing_term(self, client):
        client.delete('/api/v1/terms/9999999999')
        response = client.delete('/api/v1/terms/9999999999')
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(response.json)



# TESTS FOR PUTTING A TERM

    def test_put_term_update(self, client):
        # Arranging competencies to update
        client.delete('/api/v1/terms/7')
        term_to_replace = Term(6, "Summer")
        client.post('/api/v1/terms', json=term_to_replace.to_dict())
        new_term = Term(7, "Spring")

        # Updating competency
        response = client.put(f'/api/v1/terms/{term_to_replace.termID}', json=new_term.to_dict())
        self.assertEqual(response.status_code, 204)

        # Evaluate update
        retrieved_term = client.get('/api/v1/terms/7')
        self.assertEqual(new_term.to_dict(), retrieved_term.json)

        # reset what test added...
        client.delete('/api/v1/terms/7')


    def test_put_term_post_successful(self, client):
        client.delete('/api/v1/terms/7')
        new_term = Term(7, "Winter")
        response = client.put('/api/v1/terms/7', json=new_term.to_dict())
        newly_added_term = client.get('/api/v1/terms/7')

        # checking that the course added was the one provided, and the status code
        self.assertEqual(newly_added_term.json, new_term.to_dict())
        self.assertEqual(response.status_code, 201)

        # removing what the test added
        client.delete('/api/v1/terms/7')



        
    









    
