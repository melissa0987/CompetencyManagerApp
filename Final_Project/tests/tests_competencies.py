import flask_unittest
from CompetencyManager import create_app
from CompetencyManager.competency import Competency


class TestForCompetencyApi(flask_unittest.ClientTestCase):
    app = create_app()


# TESTS FOR GETTING ALL COMPETENCIES

    def test_get_competencies_no_page_specified(self, client):
        response = client.get('/api/v1/competencies')
        self.assertEqual(response.status_code, 200)
        json = response.json
        self.assertIsNotNone(json)
        self.assertIsNotNone(json['results'])
        self.assertIsNotNone(json['next_page'])
        self.assertIsNone(json['previous_page'])


    def test_get_competencies_given_valid_page(self, client):
        response = client.get('/api/v1/competencies?page=1')
        self.assertEqual(response.status_code, 200)
        json = response.json
        self.assertIsNotNone(json)
        self.assertIsNotNone(json['results'])
        self.assertIsNotNone(json['next_page'])
        self.assertIsNone(json['previous_page'])


    def test_get_competencies_given_non_existing_page(self, client):
        response = client.get('/api/v1/competencies?page=6789')
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(response.json)


    def test_get_competencies_given_invalid_page_parameter(self, client):
        response = client.get('/api/v1/competencies?page=abc')
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json)



# TESTS FOR GETTING A SPECIFIC COMPETENCY

    def test_get_competency_successful(self, client):
        resp = client.get(f'/api/v1/competencies/00SH')
        self.assertEqual(resp.status_code, 200)
        json = resp.json
        self.assertIsNotNone(json['competencyID'])
        self.assertIsNotNone(json['competencyName'])
        self.assertIsNotNone(json['competencyAchievement'])
        self.assertIsNotNone(json['competencyType'])


    def test_get_competency_given_invalid_competency_id(self, client):
        response = client.get('/api/v1/competencies/12345')
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json)

    

# TESTS FOR POSTING A COMPETENCY


    def test_post_competency_successful(self, client):
        ## Creating entry in database to delete
        new_competency = Competency("XXXX", "NEW COMPETENCY", "ACHIEVEMENT", "MANDATORY")
        client.delete(f'/api/v1/competencies/XXXX')
        response = client.post('/api/v1/competencies', json=new_competency.to_dict())
        self.assertEqual(response.status_code, 201)

        response = client.get('/api/v1/competencies/XXXX')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json, new_competency.to_dict())
        client.delete(f'/api/v1/competencies/XXXX')


    def test_post_competency_given_already_existing_competency(self, client):
        new_competency = Competency("00Q3", "Solve computer-related problems using mathematics", 
                                    "* Based on situational problems * Using quantitative data", "Mandatory")
        response = client.post('/api/v1/competencies', json=new_competency.to_dict())

        # checking that 500 was returned, and error message something went wrong with the database (unique constraint)
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json)



# TESTS FOR DELETING A COMPETENCY


    def test_delete_competency_successful(self, client):
        new_competency = Competency("XXXX", "NEW COMPETENCY", "ACHIEVEMENT", "MANDATORY")
        response = client.post('/api/v1/competencies', json=new_competency.to_dict())
        self.assertEqual(response.status_code, 201)

        response = client.delete(f'/api/v1/competencies/XXXX')
        self.assertEqual(response.status_code, 204)


    def test_delete_competency_given_invalid_competency_id(self, client):
        response = client.delete('/api/v1/courses/ZZZZ')
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json)



# TESTS FOR PUTTING A COMPETENCY


    def test_put_competency_update(self, client):
        # Arranging competencies to update
        client.delete('/api/v1/competencies/XXXX')
        competency_to_replace = Competency("ZZZZ","COMPETENCY", "ACHIEVEMENT", "MANDATORY")
        client.post('/api/v1/competencies', json=competency_to_replace.to_dict())
        new_competency = Competency("XXXX","ANOTHER_COMPETENCY", "ACHIEVEMENT", "MANDATORY")

        # Updating competency
        response = client.put(f'/api/v1/competencies/{competency_to_replace.competencyID}', json=new_competency.to_dict())
        self.assertEqual(response.status_code, 204)

        # Evaluate update
        retrieved_competency = client.get('/api/v1/competencies/XXXX')
        self.assertEqual(new_competency.to_dict(), retrieved_competency.json)

        # reset what test added...
        client.delete('/api/v1/competencies/XXXX')


    def test_put_competency_post_successful(self, client):
        client.delete('/api/v1/competencies/XXXX')
        new_competency = Competency("XXXX", "NEW COMPETENCY", "ACHIEVEMENT", "MANDATORY")
        response = client.put('/api/v1/competencies/XXXX', json=new_competency.to_dict())
        newly_added_competency = client.get('/api/v1/competencies/XXXX')

        # checking that the course added was the one provided, and the status code
        self.assertEqual(newly_added_competency.json, new_competency.to_dict())
        self.assertEqual(response.status_code, 201)

        # removing what the test added
        client.delete('/api/v1/competencies/XXXX')


