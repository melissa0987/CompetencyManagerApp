import flask_unittest
from CompetencyManager import create_app
from CompetencyManager.domain import Domain


class TestForDomainApi(flask_unittest.ClientTestCase):
    app = create_app()


# TESTS FOR GETTING ALL DOMAINS

    def test_get_domains_given_invalid_page_parameter(self, client):
        response = client.get('/api/v1/domains?page=abc')
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json)


    def test_get_domains_given_non_existing_page(self, client):
        response = client.get('/api/v1/domains?page=6789')
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(response.json)


    def test_get_domains_successful_no_page_specified(self, client):
        response = client.get('/api/v1/domains')
        self.assertEqual(response.status_code, 200)
        json = response.json
        self.assertIsNotNone(json)
        self.assertIsNotNone(json['results'])
        self.assertIsNone(json['next_page'])
        self.assertIsNone(json['previous_page'])

    def test_get_domains_successful_given_valid_page(self, client):
        response = client.get('/api/v1/domains?page=1')
        json = response.json
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(json)
        self.assertIsNotNone(json['results'])
        self.assertIsNone(json['next_page'])
        self.assertIsNone(json['previous_page'])


# TESTS FOR GETTING A SPECIFIC DOMAIN

    def test_get_domain_successful(self, client):
        resp = client.get(f'/api/v1/domains/3')
        self.assertEqual(resp.status_code, 200)
        json = resp.json
        self.assertIsNotNone(json['description'])
        self.assertIsNotNone(json['domainID'])
        self.assertIsNotNone(json['domainName'])


    def test_get_domain_given_invalid_domain_id(self, client):
        response = client.get('/api/v1/domains/25')
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(response.json)

    def test_get_domain_given_non_existing_domain_id(self, client):
        client.delete('/api/v1/domains/9999999999')
        response = client.get('/api/v1/domains/9999999999')
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(response.json)



# TESTS FOR POSTING A DOMAIN


    def test_post_domain_successful(self, client):
        new_domain = Domain("NAME", "DESCRIPTION", 4)
        response = client.post('/api/v1/domains', json=new_domain.to_dict())
        self.assertEqual(response.status_code, 201)

        response = client.get('/api/v1/domains/4')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json, new_domain.to_dict())


    def test_post_domain_given_already_existing_domain(self, client):
        new_domain = Domain("NAME", "DESCRIPTION", 4)
        response = client.post('/api/v1/terms', json=new_domain.to_dict())

        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json)



# TESTS FOR DELETING A DOMAIN


    def test_delete_domain_successful(self, client):
        new_domain = Domain("DESCRIPTION", "NAME", 4)
        response = client.post('/api/v1/domains', json=new_domain.to_dict())
        self.assertEqual(response.status_code, 201)
        response = client.delete(f'/api/v1/domains/4')
        self.assertEqual(response.status_code, 204)

    def test_delete_domain_given_invalid_domain_id(self, client):
        response = client.delete('/api/v1/domains/900')
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(response.json)

    def test_delete_domain_given_non_existing_domain(self, client):
        client.delete('/api/v1/domains/9999999999')
        response = client.delete('/api/v1/domains/9999999999')
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(response.json)



# TESTS FOR PUTTING A DOMAIN


    def test_put_domain_update(self, client):
        # Arranging domains to update
        client.delete('/api/v1/domains/4')
        domain_to_replace = Domain("NAME", "DESCRIPTION", 4)
        client.post('/api/v1/domains', json=domain_to_replace.to_dict())
        new_domain = Domain("NEW NAME", "NEW DESCRIPTION", 4)

        # Updating domain
        response = client.put(f'/api/v1/domains/{domain_to_replace.domainID}', json=new_domain.to_dict())
        self.assertEqual(response.status_code, 204)

        # Evaluate update
        retrieved_domain = client.get('/api/v1/domains/4')
        self.assertEqual(new_domain.to_dict(), retrieved_domain.json)

        # reset what test added...
        resp = client.delete('/api/v1/domains/4')



    def test_put_term_post_successful(self, client):
        client.delete('/api/v1/domains/4')
        new_domain = Domain("NEW NAME", "NEW DESCRIPTION", 4)
        response = client.put('/api/v1/domains/4', json=new_domain.to_dict())
        newly_added_domain = client.get('/api/v1/domains/4')

        # checking that the course added was the one provided, and the status code
        self.assertEqual(newly_added_domain.json, new_domain.to_dict())
        self.assertEqual(response.status_code, 201)

        # removing what the test added
        client.delete('/api/v1/domains/4')
