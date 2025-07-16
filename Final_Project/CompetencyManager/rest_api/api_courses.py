from ..exceptions import PageException, IdInUseException
from flask import Blueprint, request, url_for, jsonify, make_response
from ..dbmanager import get_db
from ..course import Course

bp = Blueprint('api_courses_bp', __name__, url_prefix='/api/v1/courses')


# Gets courses and post courses
@bp.route('', methods=['GET', 'POST'])
def get_or_post_courses():
    try:
        if request.method == 'POST':
            result = request.json
            if result:
                try:
                    course = Course.from_json(result)
                except:
                    return jsonify({'description': 'The given request does not contain a properly formatted course '}),400
                
                if not get_db().get_course(course.courseID) == None:
                    return jsonify({'description': 'The course you are trying to enter already exixts by that id '}),400
                else:
                    get_db().add_course(course)

            resp = make_response({}, 201)  
            resp.headers['Location'] = url_for('api_courses_bp.get_course', course_id=course.courseID)
            return resp
        
        ## for GET...
        else:
            page_num = 1
            if request.args:
                page = request.args.get('page')
                if page:
                    page_num = int(page)

            courses, prev_page, next_page = get_db().get_courses(requested_page=page_num)

            if len(courses) == 0:
                raise PageException("This page number does not exist for courses, try looking at the first page.")
            
            pagified_courses_dict = __pagify_courses(courses, prev_page, next_page)
            return jsonify(pagified_courses_dict)
    except PageException as e:
        error_desc = str(e)
        return jsonify({'description': error_desc}),404
    except ValueError:
        return jsonify({'description': "Page number must be a valid number"}),400
    except:
        return jsonify({'description': "Something went wrong with the database ¯\_(ツ)_/¯ "}),500


# Gets a specific course
@bp.route('/<course_id>', methods=['GET'])
def get_course(course_id):
    try:
        if not len(course_id) == 10:
            return jsonify({'description': f'The id {course_id} must be 10 characters in length'}),400

        course = get_db().get_course(course_id)
        
        if course == None:
            return jsonify({'description': f'We can''t seem to find a course by the id {course_id} ¯\_(ツ)_/¯ '}),404
        else:
            return jsonify(course.__dict__)
        
    except:
        return jsonify({'description': "Something went wrong with the database ¯\_(ツ)_/¯ "}),500


# Deletes a specific course
@bp.route('/<course_id>', methods= ['DELETE'])
def delete_course(course_id):
    try:
        if not len(course_id) == 10:
            return jsonify({'description': f'The id {course_id} must be 10 characters in length'}),400
        
        course = get_db().get_course(course_id)

        if not course:
            return jsonify({'description': f'We can''t seem to find a course by the id {course_id} ¯\_(ツ)_/¯ '}), 404

        get_db().delete_course(course_id)
        return jsonify({}), 204
    except:
        return jsonify({'description': "Something went wrong with the database ¯\_(ツ)_/¯ "}), 500


# Puts a course (Inserts it if it does not alreay exist, Updates it if it does already exist)
@bp.route('/<course_id>', methods= ['PUT']) 
def put_course(course_id):
    try:
        if not len(course_id) == 10:
            return jsonify({'description': f'The id {course_id} must be 10 characters in length'}),400
        
        result = request.json

        if result:
            try:
                new_course = Course.from_json(result)
            except:
                    return jsonify({'description': 'The given request does not contain a properly formatted course '}),400
                
            old_course = get_db().get_course(course_id)
            if not old_course:
                get_db().add_course(new_course)
                return jsonify({}), 201
            else:
                ## if the course is already in the db, update the record, but if the new data exists already, throw an error
                if not get_db().get_competency(new_course.courseID) == None:
                    raise IdInUseException("You can't replace a course with a course that already exists. ")
                get_db().update_course(old_course.courseID, new_course)
                return jsonify({}), 204
        else:
            return jsonify({'description': 'The given request does not contain a properly formatted course '}),400
    except IdInUseException as e:
        error_desc = str(e)
        return jsonify({'description': error_desc}),409
    except:
        return jsonify({'description': "Something went wrong with the database ¯\_(ツ)_/¯ "}), 500

# For pagination
def __pagify_courses(courses, prev_page, next_page):
    next_page_url = None
    prev_page_url = None
    if prev_page:
        prev_page_url = url_for('api_courses_bp.get_or_post_courses', page=prev_page)
    if next_page:
        next_page_url = url_for('api_courses_bp.get_or_post_courses', page=next_page)
    return {'next_page': next_page_url, 'previous_page': prev_page_url, 'results': [course.__dict__ for course in courses]}