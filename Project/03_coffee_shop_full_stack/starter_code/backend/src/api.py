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


db_drop_and_create_all()

# ROUTES

@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    drinks_short = [drink.short() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': drinks_short
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all()
    drinks_long = [drink.long() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': drinks_long
    })



@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()
    title = body.get('title')
    recipe = body.get('recipe')
    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
        drink_long = drink.long()
        return jsonify({
            'success': True,
            'drinks': [drink_long]
        })
    except Exception:
        abort(422)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    drink = Drink.query.get(id)
    if not drink:
        abort(404)
    body = request.get_json()
    title = body.get('title')
    recipe = body.get('recipe')
    if title:
        drink.title = title
    if recipe:
        drink.recipe = json.dumps(recipe)
    drink.update()
    drink_long = drink.long()
    return jsonify({
        'success': True,
        'drinks': [drink_long]
    })



@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.get(id)
    if not drink:
        abort(404)
    drink.delete()
    return jsonify({
        'success': True,
        'delete': id
    })


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



@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code
