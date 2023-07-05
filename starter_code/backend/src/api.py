import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
with app.app_context():
    db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

# GET DRINKS


@app.route('/drinks', methods=['GET'])
def get_drinks():
    response = Drink.query.order_by(Drink.id).all()
    if response is None:
        print('no drinks available at the moment')
        abort(404)
    else:
        return ({
            "success": True,
            "drinks": [i.short() for i in response]
        })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

# GET DRINKS INFORMATIONS


@app.route('/drinks-details', methods=['GET'])
def get_drinks_details():
    response = Drink.query.order_by(Drink.id).all()
    if response is None:
        print('no drinks avilable at the moment')
        abort(404)
    else:
        return jsonify({
            "success": True,
            "drinks": [i.long() for i in response]
        }), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

# CREATE DRINK


@app.route('/drinks', methods=['POST'])
def create_drinks():
    response = request.get_json()
    if response is None:
        abort(404)
    else:
        new_drink = Drink(
            id=response.get('id'),
            title=response.get('title'),
            recipe=response.get('recipe')
        )
        new_drink.insert()
        return jsonify({
            "success": True,
            "drinks": [new_drink.long()]
        }), 200


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


# EDITING DRINKS


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
def update_drink(drink_id):
    response = request.get_json()
    if response is None:
        abort(404)
    else:
        drink = Drink.query.filter(Drink.id == drink_id).first()
        if drink is None:
            abort(404)
        else:
            drink.title = response.get('title')
            drink.recipe = response.get('recipe')
            drink.update()
            return jsonify({
                "success": True,
                "drinks": [drink.long()]
            }), 200


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

# DELETING DRINKS


@app.route('/drinks/<int:drink_id>/delete', methods=['DELETE'])
def delete_drink(drink_id):
    response = Drink.query.filter(Drink.id == drink_id).first()
    if response is None:
        abort(404)
    else:
        response.delete()
        return jsonify({
            "success": True,
            "delete": [response.long()]
        }), 200


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
# ERROR HANDLING


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def handle_auth_error(exception):
    return jsonify({
        "success": False,
        "error": exception.status_code,
        "message": exception.error
    }), exception.status_code
