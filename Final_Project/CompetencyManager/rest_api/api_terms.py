from ..exceptions import PageException
from flask import Blueprint, request, url_for, jsonify, make_response, abort
from ..dbmanager import get_db
from ..term import Term

bp = Blueprint('api_terms_bp', __name__, url_prefix='/api/v1/terms')


# Gets terms and post term
@bp.route('', methods=['GET', 'POST'])
def get_post_terms_api():
    try: 

        if request.method == 'POST':
            result = request.json
            if result:
                try:
                    term = Term.from_json(result)
                except:
                    return jsonify({'description': 'The given request does not contain a properly formatted term '}),400
                
                if not get_db().get_term(term.termID) == None:
                    return jsonify({'description': 'The term you are trying to enter already exixts by that id '}),400
                else:
                    get_db().add_term(term)

            resp = make_response({}, 201)  
            resp.headers['Location'] = url_for('api_terms_bp.term_api', term_id=term.termID)
            return resp


        elif request.method == 'GET':

            page_num = 1
            if request.args:
                page = request.args.get('page')
                if page:
                    page_num = int(page)

            terms, prev_page, next_page = get_db().get_terms(requested_page=page_num)

            
            if len(terms) == 0:
                raise PageException("This page number does not exist for terms, try looking at the first page.")
        
            pagified_terms_dict = __pagify_terms(terms, prev_page, next_page)
            return jsonify(pagified_terms_dict)
    
    except PageException as e:
        error_desc = str(e)
        return jsonify({'description': error_desc}), 404
    except ValueError:
        return jsonify({'description': "Page number must be a valid number"}),400
    except:
        return jsonify({'description': "Something went wrong with the database... "}),500


# For pagination
def __pagify_terms(terms, prev_page, next_page):
    next_page_url = None
    prev_page_url = None
    if prev_page:
        prev_page_url = url_for('api_terms_bp.get_post_terms_api', page=prev_page)
    if next_page:
        next_page_url = url_for('api_terms_bp.get_post_terms_api', page=next_page)
    return {'next_page': next_page_url, 'previous_page': prev_page_url, 'results': [term.__dict__ for term in terms]}


# Gets a specific term
@bp.route('/<int:term_id>', methods=['GET'])
def term_api(term_id):
    try:        
        term = get_db().get_term(term_id)
        
        if term == None:
            return jsonify({'description': "We can't seem to find a term by that id..."}),404
        else:
            return jsonify(term.__dict__)
        
    except:
        return jsonify({'description': "Something went wrong with the database... "}),500
    

# Deletes a specific term
@bp.route('/<int:term_id>', methods= ['DELETE'])
def delete_term(term_id):
    try:
        # if not isinstance(term_id, int):
        #     return jsonify({'description': "Term id must be an int"}),400
        
        db = get_db()
        term = db.get_term(term_id)

        if not term:
            return jsonify({'description': f"Term {term_id} not found"}), 404

        db.delete_term(term_id)
        return jsonify({}), 204
    except:
        return jsonify({'description': "Something went wrong with the database"}), 500
    

# Puts a term (Inserts it if it does not alreay exist, Updates it if it does already exist)
@bp.route('/<int:term_id>', methods= ['PUT'])
def put_term(term_id):
    try:
        if not isinstance(term_id, int):
            return jsonify({'description': "Term id must be an int"}),400
        
        result = request.json

        if result:
            new_term = Term.from_json(result)
            term_to_replace = get_db().get_term(term_id)
            if not term_to_replace:
                ## if the term isn't already in the db, create a new record
                get_db().add_term(new_term)
                return jsonify({}), 201
            else:
                ## if the term is already in the db, update the record, but if the new data exists already, throw an error
                if get_db().get_term(new_term.termID):
                    return jsonify({'description': "You can't replace a term with a term that already exists. "}), 400
                get_db().update_term(term_to_replace.termID, new_term)
                return jsonify({}), 204
        else:
            return jsonify({'description': 'The given request does not contain a properly formatted term '}), 400

    except:
        return jsonify({'description': "Something went wrong with the database... "}), 500
