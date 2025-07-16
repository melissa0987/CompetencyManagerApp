from ..exceptions import PageException
from flask import Blueprint, request, url_for, jsonify, make_response, abort
from ..dbmanager import get_db
from ..competency import Competency

bp = Blueprint('api_competencies_bp', __name__, url_prefix='/api/v1/competencies')


# Gets competencies and post competency
@bp.route('', methods=['GET', 'POST'])
def get_post_competencies_api():
    try: 
   
        if request.method == 'POST':
            result = request.json
            if result:
                try:
                    competency = Competency.from_json(result)
                except:
                    return jsonify({'description': 'The given request does not contain a properly formatted competency '}),400
                
                if not get_db().get_competency(competency.competencyID) == None:
                    return jsonify({'description': 'The competency you are trying to enter already exixts by that id '}),400
                else:
                    get_db().add_competency(competency)

            resp = make_response({}, 201)  
            resp.headers['Location'] = url_for('api_competencies_bp.competency_api', competency_id=competency.competencyID)
            return resp


        elif request.method == 'GET':

            page_num = 1
            if request.args:
                page = request.args.get('page')
                if page:
                    page_num = int(page)

            competencies, prev_page, next_page = get_db().get_competencies(requested_page=page_num)

            
            if len(competencies) == 0:
                raise PageException("This page number does not exist for competencies, try looking at the first page.")
        
            pagified_competencies_dict = __pagify_competencies(competencies, prev_page, next_page)
            return jsonify(pagified_competencies_dict)
    
    except PageException as e:
        error_desc = str(e)
        return jsonify({'description': error_desc}),404
    except ValueError:
        return jsonify({'description': "Page number must be a valid number"}),400
    except:
        return jsonify({'description': "Something went wrong with the database... "}),500


# Gets a specific competency
@bp.route('/<competency_id>', methods=['GET'])
def competency_api(competency_id):
    try:        
        competency = get_db().get_competency(competency_id)
        
        if competency == None:
            return jsonify({'description': "We can't seem to find a competency by that id..."}),400
        else:
            return jsonify(competency.__dict__)
        
    except:
        return jsonify({'description': "Something went wrong with the database... "}),500


# For pagination
def __pagify_competencies(competencies, prev_page, next_page):
    next_page_url = None
    prev_page_url = None
    if prev_page:
        prev_page_url = url_for('api_competencies_bp.get_post_competencies_api', page=prev_page)
    if next_page:
        next_page_url = url_for('api_competencies_bp.get_post_competencies_api', page=next_page)
    return {'next_page': next_page_url, 'previous_page': prev_page_url, 'results': [competency.__dict__ for competency in competencies]}


# Deletes a specific competency
@bp.route('/<competency_id>', methods= ['DELETE'])
def delete_competency(competency_id):
    try:
        if not isinstance(competency_id, str):
            return jsonify({'description': "Competency id must be a string"}),400
        
        db = get_db()
        competency = db.get_competency(competency_id)

        if not competency:
            return jsonify({'description': f"Competency {competency_id} not found"}), 404

        db.delete_competency(competency_id)
        return jsonify({}), 204
    except:
        return jsonify({'description': "Something went wrong with the database"}), 500
    

# Puts a competency (Inserts it if it does not alreay exist, Updates it if it does already exist)
@bp.route('/<competency_id>', methods= ['PUT'])
def put_competency(competency_id):
    try:
        if not isinstance(competency_id, str):
            return jsonify({'description': "Competency id must be a string"}),400
        
        result = request.json

        if result:
            new_competency = Competency.from_json(result)
            competency_to_replace = get_db().get_competency(competency_id)
            if not competency_to_replace:
                ## if the competency isn't already in the db, create a new record
                get_db().add_competency(new_competency)
                return jsonify({}), 201
            else:
                ## if the competency is already in the db, update the record, but if the new data exists already, throw an error
                if get_db().get_competency(new_competency.competencyID):
                    return jsonify({'description': "You can't replace a competency with a competency that already exists. "}), 400
                get_db().update_competency(competency_to_replace.competencyID, new_competency)
                return jsonify({}), 204
        else:
            return jsonify({'description': 'The given request does not contain a properly formatted competency '}), 400

    except:
        return jsonify({'description': "Something went wrong with the database... "}), 500
