import os
import math
import oracledb
from flask import flash
from glob import escape
from .course import Course
from .term import Term
from .domain import Domain
from .element import Element
from .competency import Competency
from .member import Member
from .exceptions import PageException, IdInUseException

class Database:
    def __init__(self, autocommit=True):
        self.__connection = self.__connect()
        self.__connection.autocommit = autocommit

    def run_file(self, file_path):
        statement_parts = []
        with self.__connection.cursor() as cursor:
            with open(file_path, 'r') as f:
                for line in f:
                    statement_parts.append(line)
                    if line.strip('\n').strip('\n\r').strip().endswith(';'):
                        statement = "".join(
                            statement_parts).strip().rstrip(';')
                        if statement:
                            try:
                                cursor.execute(statement)
                            except Exception as e:
                                print(e)
                        statement_parts = []



    #Adding A Course
    def add_course(self, course: Course):
        with self.__get_cursor() as cursor:
            statement = "INSERT INTO courses (course_id, course_title, theory_hours, lab_hours, work_hours, description, domain_id, term_id) VALUES (:courseID, :courseTitle, :theoryHours, :labHours, :workHours, :description, :domainID, :termID)"
            cursor.execute(statement, courseID=course.courseID, courseTitle=course.courseTitle, theoryHours=course.theoryHours, labHours=course.labHours, workHours=course.workHours, description=course.description, domainID=course.domainID, termID=course.termID)
                
    #Editing A Course
    def update_course(self, courseID, course: Course):
        if courseID != course.courseID and self.get_course(course.courseID) != None:
            raise IdInUseException("That course ID is already in use.")
        
        with self.__get_cursor() as cursor:
            statement = "UPDATE courses SET course_id=:courseID, course_title=:courseTitle, theory_hours=:theoryHours, lab_hours=:labHours, work_hours=:workHours, description=:description, domain_id=:domainID, term_id=:termID WHERE course_id=:ID"
            statementDelete = "DELETE FROM courses_elements WHERE element_id = :elementID AND course_id = :courseID"
            statementAdd = "INSERT INTO courses_elements VALUES (:courseID, :elementID, :elementHours)"
            elements = self.get_course_elements(courseID)
            for element in elements:
                element.elementHours = self.get_element_hours(element.elementID, courseID)
            
            for element in elements:
                cursor.execute(statementDelete, elementID=element.elementID, courseID=courseID)
            
            cursor.execute(statement, courseID=course.courseID, courseTitle=course.courseTitle, theoryHours=course.theoryHours, labHours=course.labHours, workHours=course.workHours, description=course.description, domainID=course.domainID, termID=course.termID, ID=courseID)
            
            for element in elements:
                cursor.execute(statementAdd, courseID=course.courseID, elementID=element.elementID, elementHours=element.elementHours)
            
            return cursor.rowcount
        
    #Deleting A Course
    def delete_course(self, courseID):
        with self.__get_cursor() as cursor:
            statement = "DELETE FROM courses WHERE course_id=:courseID"
            cursor.execute(statement, courseID=courseID)
            return cursor.rowcount  
    
    #Get A Course
    def get_course(self, courseID):
        with self.__get_cursor() as cursor:
            statement = "SELECT course_id, course_title, theory_hours, lab_hours, work_hours, description, domain_id, term_id FROM courses WHERE course_id = :courseID"        
            course = None
            result = cursor.execute(statement, courseID=courseID)
            for row in result:
                course = Course(courseID=row[0], courseTitle=row[1], theoryHours=row[2], labHours=row[3], workHours=row[4], description=row[5], domainID=row[6], termID=row[7])  
            return course

    #Get All Courses
    def get_courses(self, requested_page=1, page_size=3):
        courses = []
        next_page = None
        prev_page = None
        offset = (requested_page-1)*page_size
        query =  "SELECT course_id, course_title, theory_hours, lab_hours, work_hours, description, domain_id, term_id FROM courses order by course_id offset :offset rows fetch next :page_size rows only"

        with self.__get_cursor() as cursor:
            
            result = cursor.execute(query, offset=offset, page_size=page_size)
            for row in result:
                course = Course(courseID=row[0], courseTitle=row[1], theoryHours=row[2], labHours=row[3], workHours=row[4], description=row[5], domainID=row[6], termID=row[7])
                courses.append(course)

            if len(courses) > 0:
                total_pages = math.ceil(self.get_course_count()/page_size)
                if requested_page < 1 or requested_page > total_pages:
                    raise PageException("This page number does not exist for courses, try looking at the first page.")
                next_page = requested_page + 1
                prev_page = requested_page - 1
                if requested_page == total_pages:
                    next_page = None
                if requested_page == 1: 
                    prev_page = None
            else:
                total_pages = 0
                next_page = None
                prev_page = None

            return courses, prev_page, next_page

    #Get The Domain Of A Course
    def get_course_domain(self, courseID):
        with self.__get_cursor() as cursor:
            statement = "SELECT domain_id, domain, domain_description FROM view_courses_domains WHERE course_id = :courseID"
            domain = None
            result = cursor.execute(statement, courseID=courseID)
            for row in result:
                domain = Domain(domainID=row[0], domainName=row[1], description=row[2])  
            return domain
    
        #Get The Term Of A Course
    def get_course_term(self, courseID):
        with self.__get_cursor() as cursor:
            statement = "SELECT term_id, term_name FROM view_courses_terms WHERE course_id = :courseID"
            term = None
            result = cursor.execute(statement, courseID=courseID)
            for row in result:
                term = Term(termID=row[0], termName=row[1])  
            return term

    
    #Get All Competencies Of A Course        
    def get_course_competencies(self, courseID):
        competencies = []
        with self.__get_cursor() as cursor:
            statement = "SELECT DISTINCT competency_id, competency, competency_achievement, competency_type FROM view_courses_elements_competencies WHERE course_id = :courseID ORDER BY competency_id ASC"
            result = cursor.execute(statement, courseID=courseID)
            for row in result:
                competency = Competency(competencyID=row[0], competencyName=row[1], competencyAchievement=row[2], competencyType=row[3])
                competency.elements = self.get_course_elements_by_competency(courseID, competency.competencyID)  
                competencies.append(competency)
            return competencies
    
    #Get All Elements Of A Course Grouped By Competencies            
    def get_course_elements_by_competency(self, courseID, competencyID):
        elements = []
        with self.__get_cursor() as cursor:
            statement = "SELECT element_id, element_order, element, element_criteria, competency_id FROM view_courses_elements_competencies WHERE course_id = :courseID AND competency_id = :competencyID"
            result = cursor.execute(statement, courseID=courseID, competencyID=competencyID)
            for row in result:
                element = Element(elementID=row[0], elementOrder=row[1], elementName=row[2], elementCriteria=row[3], competencyID=row[4])
                element.elementHours = self.get_element_hours(element.elementID, courseID)   
                elements.append(element)
            return elements
                    
    #Get All Elements Of A Course           
    def get_course_elements(self, courseID):
        elements = []
        with self.__get_cursor() as cursor:
            statement = "SELECT element_id, element_order, element, element_criteria, competency_id FROM view_courses_elements_competencies WHERE course_id = :courseID"
            result = cursor.execute(statement, courseID=courseID)
            for row in result:
                element = Element(elementID=row[0], elementOrder=row[1], elementName=row[2], elementCriteria=row[3], competencyID=row[4]) 
                elements.append(element)    
            return elements

    #Adding a term
    def add_term(self, term: Term):
        
        with self.__get_cursor() as cursor:
            statement = "INSERT INTO terms VALUES (:termID, :termName)"
            cursor.execute(statement, termID=term.termID, termName=term.termName)
            return cursor.rowcount
    
    #Editing A Term
    def update_term(self, termID, term: Term):
        if termID != term.termID and self.get_term(term.termID) != None:
            flash("That term number is already in use.")
            raise Exception()
        
        with self.__get_cursor() as cursor:
            statement = "UPDATE terms SET term_id=:termID, term_name=:termName WHERE term_id=:ID"
            cursor.execute(statement, termID=term.termID, termName=term.termName, ID=termID)
            return cursor.rowcount
    
    #Deleting A Term
    def delete_term(self, termID):
        with self.__get_cursor() as cursor:
            statement = "DELETE FROM terms WHERE term_id = :termID"
            cursor.execute(statement, termID=termID)
            return cursor.rowcount
    
    #Getting a term        
    def get_term(self, termID):
        
        with self.__get_cursor() as cursor:
            statement = "SELECT term_id, term_name FROM terms WHERE term_id = :termID"
            term = None
            result = cursor.execute(statement, termID=termID)
            for row in result:
                term = Term(termID=row[0], termName=row[1])  
            return term

    #Getting All Terms
    def get_terms(self, requested_page=1, page_size=3):
        
        terms = []
        next_page = None
        prev_page = None
        offset = (requested_page-1)*page_size
        query = "SELECT term_id, term_name FROM terms ORDER BY term_id offset :offset rows fetch next :page_size rows only"

        with self.__get_cursor() as cursor:
            result = cursor.execute(query, offset=offset, page_size=page_size)
            for row in result:
                term = Term(termID=row[0], termName=row[1]) 
                terms.append(term)

            if len(terms) > 0:
                total_pages = math.ceil(self.get_term_count()/page_size)
                if requested_page < 1 or requested_page > total_pages:
                    raise PageException("This page number does not exist for term, try looking at the first page.")
                next_page = requested_page + 1
                prev_page = requested_page - 1
                if requested_page == total_pages:
                    next_page = None
                if requested_page == 1: 
                    prev_page = None
            else:
                total_pages = 0
                next_page = None
                prev_page = None
                
            return terms, prev_page, next_page 

    #Getting all courses belonging to a term
    def get_term_courses(self, termID):
        courses = []        
        with self.__get_cursor() as cursor:
            statement = "SELECT course_id, course_title, theory_hours, lab_hours, work_hours, description, domain_id, term_id FROM view_courses_terms WHERE term_id = :termID"
            result = cursor.execute(statement, termID=termID)
            for row in result:
                course = Course(courseID=row[0], courseTitle=row[1], theoryHours=row[2], labHours=row[3], workHours=row[4], description=row[5], domainID=row[6], termID=row[7])
                courses.append(course)                
            return courses
    
    #Adding a domain
    def add_domain(self, domain: Domain):
        with self.__get_cursor() as cursor:
            statement = "INSERT INTO domains VALUES (:domainID, :domainName, :description)"
            domains = self.get_domains(page_size=self.get_domain_count())[0]
            domainID = domains[len(domains) - 1].domainID + 1
            cursor.execute(statement, domainID=domainID , domainName=domain.domainName, description=domain.description)
            return domainID
    
    #Getting a domain        
    def get_domain(self, domainID):
        with self.__get_cursor() as cursor:
            statement = "SELECT domain_id, domain, domain_description FROM domains WHERE domain_id = :domainID"
            domain = None
            result = cursor.execute(statement, domainID=domainID)
            for row in result:
                domain = Domain(domainID=row[0], domainName=row[1], description=row[2])  
            return domain

    #Getting All Domains
    def get_domains(self, requested_page=1, page_size=3):
        
        domains = []
        next_page = None
        prev_page = None
        offset = (requested_page-1)*page_size
        query = "SELECT domain_id, domain, domain_description FROM domains order by domain_id offset :offset rows fetch next :page_size rows only"

        with self.__get_cursor() as cursor:
            result = cursor.execute(query, offset=offset, page_size=page_size)
            for row in result:
                domain = Domain(domainID=row[0], domainName=row[1], description=row[2])  
                domains.append(domain)
                
            if len(domains) > 0:
                total_pages = math.ceil(self.get_domain_count()/page_size)
                if requested_page < 1 or requested_page > total_pages:
                    raise PageException("This page number does not exist for domain, try looking at the first page.")
                next_page = requested_page + 1
                prev_page = requested_page - 1
                if requested_page == total_pages:
                    next_page = None
                if requested_page == 1: 
                    prev_page = None
            else:
                total_pages = 0
                next_page = None
                prev_page = None
            
            return domains, prev_page, next_page
    
    #Getting the courses belonging to a domain
    def get_domain_courses(self, domainID):
        courses = []
        with self.__get_cursor() as cursor:
            statement = "SELECT course_id, course_title, theory_hours, lab_hours, work_hours, description, domain_id, term_id FROM view_courses_domains WHERE domain_id = :domainID"
            result = cursor.execute(statement, domainID=domainID)
            for row in result:
                course = Course(courseID=row[0], courseTitle=row[1], theoryHours=row[2], labHours=row[3], workHours=row[4], description=row[5], domainID=row[6], termID=row[7])
                courses.append(course)    
            return courses

    #Update a domain
    def update_domain(self, domainID, domain: Domain):
        with self.__get_cursor() as cursor:
            statement = "UPDATE domains SET domain=:domainName, domain_description=:description WHERE domain_id=:domainID"
            cursor.execute(statement, domainName=domain.domainName, description=domain.description, domainID=domainID)
            return cursor.rowcount

    #Delete a domain
    def delete_domain(self, domainID):
        with self.__get_cursor() as cursor:
            statement = "DELETE FROM domains WHERE domain_id = :domainID"
            cursor.execute(statement, domainID=domainID)
            return cursor.rowcount

    #Add an element    
    def add_element(self, element: Element):
        with self.__get_cursor() as cursor:
            statement = "INSERT INTO elements (element_order, element, element_criteria, competency_id) VALUES (:elementOrder, :elementName, :elementCriteria, :competencyID)"
            cursor.execute(statement, elementOrder=element.elementOrder, elementName=element.elementName, elementCriteria=element.elementCriteria, competencyID=element.competencyID)
            return cursor.rowcount

    #Get an element    
    def get_element(self, elementID):
        with self.__get_cursor() as cursor:
            statement = "SELECT element_id, element_order, element, element_criteria, competency_id FROM elements WHERE element_id = :elementID"
            element = None
            result = cursor.execute(statement, elementID=elementID)
            for row in result:
                element = Element(elementID=row[0], elementOrder=row[1], elementName=row[2], elementCriteria=row[3], competencyID=row[4])  
            return element
    
    #Update an element
    def update_element(self, elementID, element: Element):
        with self.__get_cursor() as cursor:
            statement = "UPDATE elements SET element_order=:elementOrder, element=:elementName, element_criteria=:elementCriteria, competency_id=:competencyID WHERE element_id=:elementID"
            cursor.execute(statement, elementOrder=element.elementOrder, elementName=element.elementName, elementCriteria=element.elementCriteria, competencyID=element.competencyID, elementID=elementID)

    #Delete an element
    def delete_element(self, elementID):
        with self.__get_cursor() as cursor:
            statement = "DELETE FROM elements WHERE element_id = :elementID"
            cursor.execute(statement, elementID=elementID)
    
    #Get the competency of an element
    def get_element_competency(self, elementID):
        with self.__get_cursor() as cursor:
            statement = "SELECT competency_id, competency, competency_achievement, competency_type FROM view_competencies_elements WHERE element_id = :elementID"
            competency = None
            result = cursor.execute(statement, elementID=elementID)
            for row in result:
                competency = Competency(competencyID=row[0], competencyName=row[1], competencyAchievement=row[2], competencyType=row[3])  
            return competency

    #Gets all elements
    def get_elements(self, requested_page=1, page_size=3):
        
        elements = []
        next_page = None
        prev_page = None
        offset = (requested_page-1)*page_size        
        statement = "SELECT element_id, element_order, element, element_criteria, competency_id FROM elements order by element_id offset :offset rows fetch next :page_size rows only"
        
        with self.__get_cursor() as cursor:

            result = cursor.execute(statement, offset=offset, page_size=page_size)
            for row in result:
                element = Element(elementID=row[0], elementOrder=row[1], elementName=row[2], elementCriteria=row[3], competencyID=row[4])   
                elements.append(element)
                
            if len(elements) > 0:
                total_pages = math.ceil(self.get_element_count()/page_size)
                if requested_page < 1 or requested_page > total_pages:
                    raise PageException("This page number does not exist for elements, try looking at the first page.")
                next_page = requested_page + 1
                prev_page = requested_page - 1
                if requested_page == total_pages:
                    next_page = None
                if requested_page == 1: 
                    prev_page = None
            else:
                total_pages = 0
                next_page = None
                prev_page = None

            return elements, prev_page, next_page  
    
    #Get competency of element
    def get_element_competency(self, elementID):
        competency = None
        with self.__get_cursor() as cursor:
            statement = "SELECT competency_id, competency, competency_achievement, competency_type FROM view_competencies_elements WHERE element_id = :elementID"
            result = cursor.execute(statement, elementID=elementID)
            for row in result:
                competency = Competency(competencyID=row[0], competencyName=row[1], competencyAchievement=row[2], competencyType=row[3])  
            return competency


    #Get courses that teach an element
    def get_element_courses(self, elementID):
        courses = None
        with self.__get_cursor() as cursor:
            statement = "SELECT course_id, course_title, theory_hours, lab_hours, work_hours, description, domain_id, term_id FROM view_courses_elements_competencies WHERE element_id = :elementID"
            courses = []
            result = cursor.execute(statement, elementID=elementID)
            for row in result:
                course = Course(courseID=row[0], courseTitle=row[1], theoryHours=row[2], labHours=row[3], workHours=row[4], description=row[5], domainID=row[6], termID=row[7])
                courses.append(course)
            return courses

    #Add a competency    
    def add_competency(self, competency: Competency):
        with self.__get_cursor() as cursor:
            statement = "INSERT INTO competencies VALUES (:competencyID, :competencyName, :competencyAchievement, :competencyType)"
            cursor.execute(statement, competencyID=competency.competencyID, competencyName=competency.competencyName, competencyAchievement=competency.competencyAchievement, competencyType=competency.competencyType)
            return cursor.rowcount
            
    #Get a specific competency
    def get_competency(self, competencyID):
        with self.__get_cursor() as cursor:
            statement = "SELECT competency_id, competency, competency_achievement, competency_type FROM competencies WHERE competency_id = :competencyID"
            competency = None
            result = cursor.execute(statement, competencyID=competencyID)
            for row in result:
                competency = Competency(competencyID=row[0], competencyName=row[1], competencyAchievement=row[2], competencyType=row[3])  
            return competency

    #Get the elements of a competency
    def get_competency_elements(self, competencyID):
        elements = []
        with self.__get_cursor() as cursor:
            statement = "SELECT element_id, element_order, element, element_criteria, competency_id FROM view_competencies_elements WHERE competency_id = :competencyID"
            result = cursor.execute(statement, competencyID=competencyID)
            for row in result:
                element = Element(elementID=row[0], elementOrder=row[1], elementName=row[2], elementCriteria=row[3], competencyID=row[4])   
                elements.append(element)
            return elements

    #Get all competencies
    def get_competencies(self, requested_page=1, page_size=3):
        competencies = []
        next_page = None
        prev_page = None
        offset = (requested_page-1)*page_size
        query = "SELECT competency_id, competency, competency_achievement, competency_type FROM competencies order by competency_id offset :offset rows fetch next :page_size rows only"

        with self.__get_cursor() as cursor:
            result = cursor.execute(query, offset=offset, page_size=page_size)
            for row in result:
                competency = Competency(competencyID=row[0], competencyName=row[1], competencyAchievement=row[2], competencyType=row[3])  
                competencies.append(competency)
            
            if len(competencies) > 0:
                total_pages = math.ceil(self.get_competency_count()/page_size)
                if requested_page < 1 or requested_page > total_pages:
                    raise PageException("This page number does not exist for competency, try looking at the first page.")
                next_page = requested_page + 1
                prev_page = requested_page - 1
                if requested_page == total_pages:
                    next_page = None
                if requested_page == 1: 
                    prev_page = None
            else:
                total_pages = 0
                next_page = None
                prev_page = None

            return competencies, prev_page, next_page


    #Update a competency                
    def update_competency(self, competencyID, competency: Competency):
        with self.__get_cursor() as cursor:
            if competencyID != competency.competencyID and self.get_competency(competency.competencyID) != None:
                flash("That competency ID is already in use.")
                raise Exception()
            
            elements = self.get_competency_elements(competencyID)
            
            #Update elements foreign key
            if competencyID != competency.competencyID and len(elements) > 0:
                statement = "INSERT INTO competencies VALUES (:competencyID, :competencyName, :competencyAchievement, :competencyType)"
                cursor.execute(statement, competencyID=competency.competencyID, competencyName=competency.competencyName, competencyAchievement=competency.competencyAchievement, competencyType=competency.competencyType)
                
                for element in elements:
                    statement = "UPDATE elements SET element_order=:elementOrder, element=:elementName, element_criteria=:elementCriteria, competency_id=:competencyID WHERE element_id=:elementID"
                    cursor.execute(statement, elementOrder=element.elementOrder, elementName=element.elementName, elementCriteria=element.elementCriteria, competencyID=competency.competencyID, elementID=element.elementID)
                
                statement = "DELETE FROM competencies WHERE competency_id = :competencyID"
                cursor.execute(statement, competencyID=competencyID)
            else:
                statement = "UPDATE competencies SET competency_id=:competencyID, competency=:competencyName, competency_achievement=:competencyAchievement, competency_type=:competencyType WHERE competency_id=:compID"
                cursor.execute(statement, competencyID=competency.competencyID, competencyName=competency.competencyName, competencyAchievement=competency.competencyAchievement, competencyType=competency.competencyType, compID=competencyID)
                return cursor.rowcount

    #Delete a competency
    def delete_competency(self, competencyID):
        with self.__get_cursor() as cursor:
            statement = "DELETE FROM competencies WHERE competency_id = :competencyID"
            cursor.execute(statement, competencyID=competencyID)

    #Get bridging table entry between course and element
    def get_courses_teaching_element(self, elementID):
        courses = []       
        with self.__get_cursor() as cursor:
            statement = "SELECT course_id, course_title, theory_hours, lab_hours, work_hours, description, domain_id, term_id FROM view_courses_elements WHERE element_id = :elementID"
            result = cursor.execute(statement, elementID=elementID)
            for row in result:
                course = Course(courseID=row[0], courseTitle=row[1], theoryHours=row[2], labHours=row[3], workHours=row[4], description=row[5], domainID=row[6], termID=row[7])
                courses.append(course)
            return courses
                    
    #Add a bridging table entry between course and element. Course will teach the element.
    def add_course_teaching_element(self, elementID, courseID, elementHours):
        with self.__get_cursor() as cursor:
            statement = "INSERT INTO courses_elements VALUES (:courseID, :elementID, :elementHours)"
            cursor.execute(statement, courseID=courseID, elementID=elementID, elementHours=elementHours)
            return cursor.rowcount
        
    #Delete a bridging table entry between course and element. Course will not teach the element.
    def delete_course_teaching_element(self, elementID, courseID):
        with self.__get_cursor() as cursor:
            statement = "DELETE FROM courses_elements WHERE element_id = :elementID AND course_id = :courseID"
            cursor.execute(statement, elementID=elementID, courseID=courseID)
            return cursor.rowcount
    
    #Get the hours for an element
    def get_element_hours(self, elementID, courseID):
        hours = 0
        with self.__get_cursor() as cursor:
            statement = "SELECT element_hours FROM courses_elements WHERE element_id = :elementID AND course_id = :courseID"
            result = cursor.execute(statement, elementID=elementID, courseID=courseID)
            for row in result:
                hours = row[0]
            return hours
                    
    #Update the element hours between a course and element
    def update_element_hours(self, elementID, courseID, elementHours):
        with self.__get_cursor() as cursor:
            statement = "UPDATE courses_elements SET element_hours = :elementHours WHERE element_id = :elementID AND course_id = :courseID"
            cursor.execute(statement, courseID=courseID, elementID=elementID, elementHours=elementHours)

                    
    #Search through courses
    def search_courses(self, query):
        courses=[]
        with self.__get_cursor() as cursor:
            statement = "SELECT course_id FROM courses WHERE CONTAINS (course_id, :query, 1) > 0 UNION "
            statement += "SELECT course_id FROM courses WHERE CONTAINS (course_title, :query, 1) > 0 UNION "
            statement += "SELECT course_id FROM courses WHERE CONTAINS (description, :query, 1) > 0"

            result = cursor.execute(statement, query=query)
            for row in result:
                courses.append(self.get_course(row[0]))
            
        return courses
    
    #Search through competencies
    def search_competencies(self, query):
        competencies=[]
        
        with self.__get_cursor() as cursor:
            statement = "SELECT competency_id FROM competencies WHERE CONTAINS (competency_id, :query, 1) > 0 UNION "
            statement += "SELECT competency_id FROM competencies WHERE CONTAINS (competency, :query, 1) > 0 UNION "
            statement += "SELECT competency_id FROM competencies WHERE CONTAINS (competency_achievement, :query, 1) > 0"
            
            result = cursor.execute(statement, query=query)
            for row in result:
                competencies.append(self.get_competency(row[0]))
            
        return competencies
    
    #Search through elements
    def search_elements(self, query):
        element_competency=[]
        
        with self.__get_cursor() as cursor:
            statement = "SELECT element_id FROM elements WHERE CONTAINS (competency_id, :query, 1) > 0 UNION "
            statement += "SELECT element_id FROM elements WHERE CONTAINS (element, :query, 1) > 0 UNION "
            statement += "SELECT element_id FROM elements WHERE CONTAINS (element_criteria, :query, 1) > 0"

            result = cursor.execute(statement, query=query)
            for row in result:
                element = self.get_element(row[0])
                competency = self.get_competency(element.competencyID)
                element_competency.append( (element, competency))

        return element_competency
                
    #Search through domains
    def search_domains(self, query):
        domains=[]
        
        with self.__get_cursor() as cursor:
            statement = "SELECT domain_id FROM domains WHERE CONTAINS (domain, :query, 1) > 0 UNION "
            statement += "SELECT domain_id FROM domains WHERE CONTAINS (domain_description, :query, 1) > 0"

            result = cursor.execute(statement, query=query)
            for row in result:
                domains.append(self.get_domain(row[0]))
            
        return domains
        
                
                      
    #Get a user by email
    def get_user(self, email: str):
        user = None
        with self.__connection.cursor() as cursor:
            results = cursor.execute("SELECT id, email, password, name, avatar_path, account_type, is_locked FROM app_users where email=:email", email=email)
            for row in results:
                user = Member(id=row[0], email=row[1], password=row[2], name=row[3], avatar_path=str(row[4]), account_type=row[5], is_locked=int(row[6]))
        return user

    #Add a user
    def add_user(self, user: Member):
        with self.__connection.cursor() as cursor:
            cursor.execute('INSERT into app_users (email, password, name, avatar_path, account_type, is_locked) VALUES (:email, :password, :name, :avatar_path, :account_type, :is_locked)',
                            email = user.email,
                           password = user.password,
                           name = user.name,
                           avatar_path = user.avatar_path,
                           account_type = user.account_type,
                           is_locked = user.is_locked)
            return cursor.rowcount
            
    #Get a user by id
    def get_user_by_id(self, user_id):
        user = None
        with self.__connection.cursor() as cursor:
            statement = "SELECT id, email, password, name, avatar_path, account_type, is_locked FROM view_all_users where id=:user_id"
            results = cursor.execute( statement, user_id=user_id)
            for row in results:
                user = Member(id=row[0], email=row[1], password=row[2], name=row[3], avatar_path=escape(row[4]), account_type=row[5], is_locked=row[6])  
        return user

    #Fetches all users based on their account type
    def get_users_by_account_type(self, account_type):
        members = []
        with self.__get_cursor() as cursor:
            result = cursor.execute("SELECT id, email, password, name, avatar_path, account_type, is_locked FROM view_all_users where account_type=:account_type",account_type=account_type)
            for row in result:
                member = Member(id=row[0], email=row[1], password=row[2], name=row[3], avatar_path=escape(row[4]), account_type=row[5], is_locked=row[6])  
                members.append(member)
                    
        return members
    
    #Fetches all registered users in the database
    def get_all_users(self):
        users = []
        with self.__get_cursor() as cursor:
            result = cursor.execute("SELECT id, email, password, name, avatar_path, account_type, is_locked FROM view_all_users" )
            for row in result:
                user = Member(id=row[0], email=row[1], password=row[2], name=row[3], avatar_path=escape(row[4]), account_type=row[5], is_locked=row[6])  
                users.append(user)
                    
        return users
        


    #Get course count
    def get_course_count(self):   
        with self.__get_cursor() as cursor:
            results = cursor.execute("SELECT count(*) FROM courses")
            courses_quantity = results.fetchone()[0]
        return courses_quantity

    #Get competency count
    def get_competency_count(self): 
        with self.__get_cursor() as cursor:
            results = cursor.execute("SELECT count(*) FROM competencies")
            competencies_quantity = results.fetchone()[0]
        return competencies_quantity

    #Get term count
    def get_term_count(self):
        with self.__get_cursor() as cursor:
            results = cursor.execute("SELECT count(*) FROM terms")
            terms_quantity = results.fetchone()[0]
        return terms_quantity

    #Get domain count
    def get_domain_count(self):
        with self.__get_cursor() as cursor:
            results = cursor.execute("SELECT count(*) FROM domains")
            domains_quantity = results.fetchone()[0]
        return domains_quantity
    
    #Get element count
    def get_element_count(self):
        with self.__get_cursor() as cursor:
            results = cursor.execute("SELECT count(*) FROM elements")
            elements_quantity = results.fetchone()[0]
        return elements_quantity
     

    
    #Get blocked users
    def get_blocked_users(self):
        users = []
        with self.__get_cursor() as cursor:
            result = cursor.execute("SELECT id, email, password, name, avatar_path, account_type, is_locked FROM view_blocked_users" )
            for row in result:
                user = Member(id=row[0], email=row[1], password=row[2], name=row[3], avatar_path=escape(row[4]), account_type=row[5], is_locked=row[6])  
                users.append(user)
                    
        return users

    #Delete a user
    def delete_user(self, email):
        with self.__get_cursor() as cursor:
            statement = "DELETE FROM app_users WHERE email=:email"
            cursor.execute(statement, email=email)
            return cursor.rowcount

    #Update a user
    def update_user(self, user_id, user: Member):
        
            with self.__get_cursor() as cursor:
                statement = "UPDATE app_users SET email=:email, password=:password, name=:name, account_type=:account_type, is_locked=:is_locked WHERE id=:id"
                try:
                    cursor.execute(statement, email=user.email, password=user.password, name=user.name, account_type=user.account_type, is_locked=user.is_locked, id=user_id)
                    return cursor.rowcount
                except:
                    raise Exception("An error occured while updating the user.")
        


    #Close connection
    def close(self):
        '''Closes the connection'''
        if self.__connection is not None:
            self.__connection.close()
            self.__connection = None

    #Gets the cursor
    def __get_cursor(self):
            for i in range(3):
                try:
                    return self.__connection.cursor()
                except Exception as e:
                    # Might need to reconnect
                    self.__reconnect()

    #To reconnect
    def __reconnect(self):
        try:
            self.close()
        except oracledb.Error as f:
            pass
        self.__connection = self.__connect()

    #To connect to pdbora database
    def __connect(self):
        return oracledb.connect(user=os.environ['DBUSER'], password=os.environ['DBPWD'],
                                             host="198.168.52.211", port=1521, service_name="pdbora19c.dawsoncollege.qc.ca")


if __name__ == '__main__':
    print('Provide file to initialize database')
    file_path = input()
    if os.path.exists(file_path):
        db = Database()
        db.run_file(file_path)
        db.close()
    else:
        print('Invalid Path')
