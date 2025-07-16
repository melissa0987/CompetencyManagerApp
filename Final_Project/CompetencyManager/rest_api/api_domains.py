from ..exceptions import PageException
from flask import Blueprint, request, url_for, jsonify, make_response, abort
from ..dbmanager import get_db
from ..domain import Domain

bp = Blueprint('api_domains_bp', __name__, url_prefix='/api/v1/domains')


# Gets domains and post domain
@bp.route('', methods=['GET', 'POST'])
def get_post_domains_api():
    try: 
    
        if request.method == 'POST':
            result = request.json
            if result:
                try:
                    domain = Domain.from_json(result)
                except:
                    return jsonify({'description': 'The given request does not contain a properly formatted domain '}),400
                
                if not get_db().get_domain(domain.domainID) == None:
                    return jsonify({'description': 'The domain you are trying to enter already exixts by that id '}),400
                else:
                    get_db().add_domain(domain)

            resp = make_response({}, 201)  
            resp.headers['Location'] = url_for('api_domains_bp.domain_api', domain_id=domain.domainID)
            return resp


        elif request.method == 'GET':

            page_num = 1
            if request.args:
                page = request.args.get('page')
                if page:
                    page_num = int(page)

            domains, prev_page, next_page = get_db().get_domains(requested_page=page_num)

            
            if len(domains) == 0:
                raise PageException("This page number does not exist for domains, try looking at the first page.")
        
            pagified_domains_dict = __pagify_domains(domains, prev_page, next_page)
            return jsonify(pagified_domains_dict)
    
    except PageException as e:
        error_desc = str(e)
        return jsonify({'description': error_desc}),404
    except ValueError:
        return jsonify({'description': "Page number must be a valid number"}),400
    except:
        return jsonify({'description': "Something went wrong with the database... "}),500

# For pagination
def __pagify_domains(domains, prev_page, next_page):
    next_page_url = None
    prev_page_url = None
    if prev_page:
        prev_page_url = url_for('api_domains_bp.get_post_domains_api', page=prev_page)
    if next_page:
        next_page_url = url_for('api_domains_bp.get_post_domains_api', page=next_page)
    return {'next_page': next_page_url, 'previous_page': prev_page_url, 'results': [domain.__dict__ for domain in domains]}


# Gets a specific domain
@bp.route('/<int:domain_id>', methods=['GET'])
def domain_api(domain_id):
    try:        
        domain = get_db().get_domain(domain_id)
        
        if domain == None:
            return jsonify({'description': "We can't seem to find a domain by that id..."}),404
        else:
            return jsonify(domain.__dict__)
        
    except:
        return jsonify({'description': "Something went wrong with the database... "}),500


# Deletes a specific domain
@bp.route('/<int:domain_id>', methods= ['DELETE'])
def delete_domain(domain_id):
    try:
        
        db = get_db()
        domain = db.get_domain(domain_id)

        if not domain:
            return jsonify({'description': f"Domain {domain_id} not found"}), 404

        db.delete_domain(domain_id)
        return jsonify({}), 204
    except:
        return jsonify({'description': "Something went wrong with the database"}), 500
    

# Puts a domain (Inserts it if it does not alreay exist, Updates it if it does already exist)
@bp.route('/<int:domain_id>', methods= ['PUT'])
def put_domain(domain_id):
    try:
        # if not isinstance(domain_id, int):
        #     return jsonify({'description': "Domain id must be an int"}),400
        
        result = request.json

        if result:
            new_domain = Domain.from_json(result)
            domain_to_replace = get_db().get_domain(domain_id)
            if not domain_to_replace:
                ## if the domain isn't already in the db, create a new record
                get_db().add_domain(new_domain)
                return jsonify({}), 201
            else:
                get_db().update_domain(domain_to_replace.domainID, new_domain)
                return jsonify({}), 204
        else:
            return jsonify({'description': 'The given request does not contain a properly formatted domain '}), 400

    except:
        return jsonify({'description': "Something went wrong with the database... "}), 500
