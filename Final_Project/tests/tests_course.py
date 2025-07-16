### setup.sql must be run before using tests

import flask_unittest
from CompetencyManager import create_app
from CompetencyManager.course import Course

class TestForCourseApi(flask_unittest.ClientTestCase):
    
    app = create_app()

# TESTS FOR POSTING A COURSE

    def test_post_course_given_invalid_json(self, client):
        bad_formatted_course = {'CourseID' : "XXX-XXX-XX", 'description' : "COURSE DESCRIPTION", 'domainID' : 1, 'termID' : 1}
        response = client.post('/api/v1/courses', json=bad_formatted_course)

        # checking that 400 was returned, and error message is present
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json)

    def test_post_course_given_already_existing_course(self, client):
        new_course = Course("420-110-DW", "", 3, 3, 3, "", 1, 1)
        response = client.post('/api/v1/courses', json=new_course.to_dict())

        # checking that 400 was returned, and error message is present
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json)

    def test_post_course_successful(self, client):
        new_course = Course("XXX-XXX-XX", "NEW COURSE", 3, 3, 3, "COURSE DESCRIPTION", 1, 1)
        post_response = client.post('/api/v1/courses', json=new_course.to_dict())
        response = client.get('/api/v1/courses/XXX-XXX-XX')

        # checking that the course added was the one provided, and the status code
        self.assertEqual(response.json, new_course.to_dict())
        self.assertEqual(post_response.status_code, 201)

        # removing what the test added
        client.delete('/api/v1/courses/XXX-XXX-XX')


# TESTS FOR GETTING ALL COURSES (self, clientAND PAGINATION TESTS)

    def test_get_courses_given_invalid_page_parameter(self, client):
        response = client.get('/api/v1/courses?page=abc')
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json)

    def test_get_courses_given_non_existing_page(self, client):
        response = client.get('/api/v1/courses?page=6789')
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(response.json)

    def test_get_courses_successful_no_page_specified(self, client):
        response = client.get('/api/v1/courses')
        json = response.json
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(json)
        self.assertIsNotNone(json['results'])
        self.assertIsNotNone(json['next_page'])
        self.assertIsNone(json['previous_page'])

    def test_get_courses_successful_given_valid_page(self, client):
        response = client.get('/api/v1/courses?page=1')
        json = response.json
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(json)
        self.assertIsNotNone(json['results'])
        self.assertIsNotNone(json['next_page'])
        self.assertIsNone(json['previous_page'])


# TESTS FOR GETTING A SPECIFIC COURSE

    def test_get_course_given_invalid_course_id(self, client):
        response = client.get('/api/v1/courses/6789')
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json)

    def test_get_course_given_non_existing_course_id(self, client):
        client.delete('/api/v1/courses/9999999999')
        response = client.get('/api/v1/courses/9999999999')
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(response.json)

    def test_get_course_successful(self, client):
        response = client.get('/api/v1/courses/420-110-DW')    
        json = response.json
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(json)
        self.assertIsNotNone(json['courseID'])
        self.assertIsNotNone(json['courseTitle'])
        self.assertIsNotNone(json['theoryHours'])
        self.assertIsNotNone(json['labHours'])
        self.assertIsNotNone(json['workHours'])
        self.assertIsNotNone(json['description'])
        self.assertIsNotNone(json['domainID']) 
        self.assertIsNotNone(json['termID'])


# TESTS FOR DELETING A COURSE

    def test_delete_course_given_invalid_course_id(self, client):
        response = client.delete('/api/v1/courses/ZZZZ')
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json)

    def test_delete_course_given_non_existing_course(self, client):
        client.delete('/api/v1/courses/9999999999')
        response = client.delete('/api/v1/courses/9999999999')
        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(response.json)

    def test_delete_course_successful(self, client):
        ## posting course to delete
        new_course = Course("ZZZ-ZZZ-ZZ", "NEW COURSE", 3, 3, 3, "COURSE DESCRIPTION", 1, 1)
        client.post('/api/v1/courses', json=new_course.to_dict())

        ## deleteing and checking status code
        response = client.delete('/api/v1/courses/ZZZ-ZZZ-ZZ')
        self.assertEqual(response.status_code, 204)

        ## checking if course exists
        response = client.get('/api/v1/courses/ZZZ-ZZZ-ZZ')
        self.assertEqual(response.status_code, 404)

    
# TESTS FOR PUTTING A COURSE

    def test_put_course_given_invalid_course_id(self, client):
        new_course = Course("AAAAAAAAAA", "", 3, 3, 3, "", 1, 1)
        response = client.put('/api/v1/courses/AAA', json=new_course.to_dict())

        # Ensuring correct status code and json error message is present
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json)
    
    def test_put_course_given_invalid_json(self, client):
        bad_formatted_course = {'CourseID' : "XXX-XXX-XX", 'description' : "COURSE DESCRIPTION", 'domainID' : 1, 'termID' : 1}
        response = client.put('/api/v1/courses/AAAAAAAAAA', json=bad_formatted_course)

        # Ensuring correct status code and json error message is present
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json)
    
    def test_put_course_update_given_already_existing_course(self, client):
        # arranging an already existing courses in the db
        client.delete('/api/v1/courses/XXX-XXX-XX')
        client.delete('/api/v1/courses/YYY-YYY-YY')
        course_to_put = Course("XXX-XXX-XX", "NEW COURSE", 3, 3, 3, "COURSE DESCRIPTION", 1, 1)
        course_to_replace = Course("YYY-YYY-YY", "NEW COURSE", 3, 3, 3, "COURSE DESCRIPTION", 1, 1)
        client.post('/api/v1/courses', json=course_to_put.to_dict())
        client.post('/api/v1/courses', json=course_to_replace.to_dict())

        # attempting to replace a course with another course that already exists
        response = client.put('/api/v1/courses/YYY-YYY-YY', json=course_to_put.to_dict())

        # Ensuring correct status code and json error message is present
        self.assertEqual(response.status_code, 409)
        self.assertIsNotNone(response.json)

        # removing what the test added
        client.delete('/api/v1/courses/XXX-XXX-XX')
        client.delete('/api/v1/courses/YYY-YYY-YY')

    def test_put_course_update_successful(self, client):
        client.delete('/api/v1/courses/XXX-XXX-XX')
        client.delete('/api/v1/courses/YYY-YYY-YY')
        course_to_update = Course("XXX-XXX-XX", "NEW COURSE", 3, 3, 3, "COURSE DESCRIPTION", 1, 1)
        new_course = Course("YYY-YYY-YY", "NEW COURSE", 3, 3, 3, "COURSE DESCRIPTION", 1, 1)
        client.post('/api/v1/courses', json=course_to_update.to_dict())

        # updating the course in the db
        response = client.put('/api/v1/courses/XXX-XXX-XX', json=new_course.to_dict())
        newly_added_course = client.get('/api/v1/courses/YYY-YYY-YY')

        self.assertEqual(newly_added_course.json, new_course.to_dict())
        self.assertEqual(response.status_code, 204)

        # removing what the test added
        client.delete('/api/v1/courses/YYY-YYY-YY')

    def test_put_course_post_successful(self, client):
        client.delete('/api/v1/courses/XXX-XXX-XX')
        new_course = Course("XXX-XXX-XX", "NEW COURSE", 3, 3, 3, "COURSE DESCRIPTION", 1, 1)
        response = client.put('/api/v1/courses/XXX-XXX-XX', json=new_course.to_dict())
        newly_added_course = client.get('/api/v1/courses/XXX-XXX-XX')

        # checking that the course added was the one provided, and the status code
        self.assertEqual(newly_added_course.json, new_course.to_dict())
        self.assertEqual(response.status_code, 201)

        # removing what the test added
        client.delete('/api/v1/courses/XXX-XXX-XX')