from ..exceptions import PageException, IdInUseException
from flask import Blueprint, request, url_for, jsonify, make_response
from ..dbmanager import get_db
from ..element import Element

bp = Blueprint('api_elements_bp', __name__, url_prefix='/api/v1/elements')
    

# Gets elements and post element
@bp.route('', methods=['GET', 'POST'])
def get_or_post_elements():
    try:
        if request.method == 'POST':
            result = request.json
            if result:
                try:
                    element = Element.from_json(result)
                except:
                    return jsonify({'description': 'The given request does not contain a properly formatted element '}),400
                
                if get_db().get_element(element.elementID) == None:
                    get_db().add_element(element)
                else:
                    return jsonify({'description': 'The element you are trying to enter already exists by that id '}),400

            resp = make_response({}, 201)  
            resp.headers['Location'] = url_for('api_elements_bp.get_element', element_id=element.elementID)
            return resp
        
        ## for GET...
        else:
            page_num = 1
            if request.args:
                page = request.args.get('page')
                if page:
                    page_num = int(page)

            elements, prev_page, next_page = get_db().get_elements(requested_page=page_num)

            if len(elements) == 0:
                raise PageException("This page number does not exist for elements, try looking at the first page.")
            
            pagified_elements_dict = __pagify_elements(elements, prev_page, next_page)
            return jsonify(pagified_elements_dict)
    except PageException as e:
        error_desc = str(e)
        return jsonify({'description': error_desc}),404
    except ValueError:
        return jsonify({'description': "Page number must be a valid number"}),400
    except:
        return jsonify({'description': "Something went wrong with the database ¯\_(ツ)_/¯ "}),500


# Gets a specific element
@bp.route('/<element_id>', methods=['GET'])
def get_element(element_id):
    try:
        if not len(element_id) <= 2 and not len(element_id) > 0:
            return jsonify({'description': f'The id {element_id} must be 2 characters in length or less'}),400

        element = get_db().get_element(element_id)
        
        if element == None:
            return jsonify({'description': f'We can''t seem to find an element by the id {element_id} ¯\_(ツ)_/¯ '}),404
        else:
            return jsonify(element.__dict__)
        
    except:
        return jsonify({'description': "Something went wrong with the database ¯\_(ツ)_/¯ "}),500


# Deletes a specific element
@bp.route('/<element_id>', methods= ['DELETE'])
def delete_element(element_id):
    try:
        if not len(element_id) <= 2 and not len(element_id) > 0:
            return jsonify({'description': f'The id {element_id} must be 2 characters in length'}),400
        
        element = get_db().get_element(element_id)

        if not element:
            return jsonify({'description': f'We can''t seem to find a element by the id {element_id} ¯\_(ツ)_/¯ '}), 404

        get_db().delete_element(element_id)
        return jsonify({}), 204
    except:
        return jsonify({'description': "Something went wrong with the database ¯\_(ツ)_/¯ "}), 500


# Puts an element (Inserts it if it does not alreay exist, Updates it if it does already exist)
@bp.route('/<element_id>', methods= ['PUT']) 
def put_element(element_id):
    try:
        if not len(element_id) <= 2 and not len(element_id) > 0:
            return jsonify({'description': f'The id {element_id} must be 10 characters in length'}),400
        
        result = request.json

        if result:
            try:
                new_element = Element.from_json(result)
            except:
                    return jsonify({'description': 'The given request does not contain a properly formatted element '}),400
                
            old_element = get_db().get_element(element_id)
            if not old_element:
                get_db().add_element(new_element)
                return jsonify({}), 201
            else:
                ## if the element is already in the db, update the record, but if the new data exists already, throw an error
                if not get_db().get_element(new_element.elementID) == None:
                    raise IdInUseException("You can't replace a element with an element that already exists. ")
                get_db().update_element(old_element.elementID, new_element)
                return jsonify({}), 204
        else:
            return jsonify({'description': 'The given request does not contain a properly formatted element '}),400
    except IdInUseException as e:
        error_desc = str(e)
        return jsonify({'description': error_desc}),409
    except:
        return jsonify({'description': "Something went wrong with the database ¯\_(ツ)_/¯ "}), 500


# For pagination
def __pagify_elements(elements, prev_page, next_page):
    next_page_url = None
    prev_page_url = None
    if prev_page:
        prev_page_url = url_for('api_elements_bp.get_or_post_elements', page=prev_page)
    if next_page:
        next_page_url = url_for('api_elements_bp.get_or_post_elements', page=next_page)
    return {'next_page': next_page_url, 'previous_page': prev_page_url, 'results': [element.__dict__ for element in elements]}