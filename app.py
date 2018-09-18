# -*- coding: utf-8 -*-
"""Tikki backend

This module serves the RESTful interface required by the Tikki application.
"""

import datetime
import db
from enum import IntEnum
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_simple import JWTManager, jwt_required, jwt_optional, create_jwt, get_jwt_identity
import util
from werkzeug.security import generate_password_hash, check_password_hash

class RecordCategoryType(IntEnum):
    UNKNOWN = 0
    TEST = 1
    QUESTIONNAIRE = 2
    ACTIVITY = 3


class RecordType(IntEnum):
    COOPERS_TEST = 1
    PUSH_UP_60_TEST = 2
    SIT_UPS = 3
    STANDING_JUMP = 4
    PULL_UPS = 5
    ACTIVITY_STATUS = 6
    EDUCATION_DURATION = 7
    CURRENT_FITNESS = 8
    WORKING_ABILITY = 9
    HIGH_BLOOD_PRESSURE = 10
    DIABETES = 11
    ALCOHOL = 12
    SMOKING = 13
    FAMILY_STATUS = 14
    DEPRESSION = 15
    SICK_LEAVE = 16


app = Flask(__name__)
util.init_app_config(app)
db.init(app)
jwt = JWTManager(app)
CORS(app)


def get_obj_type(path):
    if path == '/user':
        return db.User
    elif path == '/record':
        return db.Record
    elif path == '/event':
        return db.Event
    elif path == 'user-event-link':
        return db.UserEventLink


@jwt.jwt_data_loader
def add_claims_to_access_token(identity):
    now = datetime.datetime.utcnow()
    sub, rol = identity['sub'], identity['rol']
    return {
        'exp': now + app.config['JWT_EXPIRES'],
        'iat': now,
        'nbf': now,
        'sub': sub,
        'rol': rol
    }

@app.route('/login', methods=['POST'])
def login():
    try:
        util.flask_validate_request_is_json(request)
        username_filter = util.get_args(request.json, required_args={'username': str})
        password_filter = util.get_args(request.json, required_args={'password': str})
        user = db.get_row(db.User, username_filter)
        if user is not None and check_password_hash(user.password, password_filter['password']):
            identity = util.create_jwt_identity(user)
            return util.flask_return_success({'jwt': create_jwt(identity), 'user': user.jsondict})
        else:
            return util.flask_return_exception('Incorrect username or password', 400)
    except Exception as e:
        return util.flask_handle_exception(e)


@app.route('/user', methods=['DELETE'], strict_slashes=False)
@app.route('/record', methods=['DELETE'], strict_slashes=False)
@app.route('/event', methods=['DELETE'], strict_slashes=False)
@app.route('/user-event-link', methods=['DELETE'], strict_slashes=False)
@jwt_required
def delete_record():
    try:
        # Check object type based on endpoint and define filters accordingly.

        obj_type = get_obj_type(request.path)
        required_args = dict()
        if obj_type is db.UserEventLink:
            required_args['event_id'] = str
        else:
            required_args['id'] = str

        filters = util.get_args(request.args, required_args=required_args)
        filters['user_id'] = get_jwt_identity()
        db.delete_row(obj_type, filters)
        return util.flask_return_success('OK')
    except Exception as e:
        return util.flask_handle_exception(e)


@app.route('/uuid', methods=['GET'], strict_slashes=False)
def get_uuid():
    try:
        args = util.get_args(received_args=request.args, defaultable_args={'count': 1})
        count = args['count']
        if 0 < count <= 1024:
            return util.flask_return_success(util.generate_uuid(count))
        else:
            return util.flask_return_exception('The count parameter cannot be below 1 or greater than 1024.', 400)
    except Exception as e:
        return util.flask_handle_exception(e)


@app.route('/whoami', methods=['GET'], strict_slashes=False)
@jwt_optional
def get_whoami():
    try:

        user = get_jwt_identity()
        if user is None:
            return util.flask_return_success('Nobody')
        else:
            return util.flask_return_success(user)
    except Exception as e:
        return util.flask_handle_exception(e)


@app.route('/schema', methods=['GET'], strict_slashes=False)
@jwt_optional
def get_schema():
    try:
        jwt_id = get_jwt_identity()
        type_dict = dict()
        if jwt_id is not None:
            filters = {'user_id': str(jwt_id)}
            records = db.get_rows(db.Record, filters)

            # sort records based on user_id and creation date to pick most recent result per user
            # TODO: sort in db.get_rows

            records.sort(key=lambda x: (x.type_id, x.created_at), reverse=True)
            lag_type_id = None
            for record in records:
                if lag_type_id != record.type_id:
                    lag_type_id = record.type_id
                    type_dict[record.type_id] = record

        rows = db.get_rows(db.RecordType, {})
        result_list = list()
        for row in rows:
            result = row.jsondict
            result['ask'] = 1 if jwt_id is not None and row.category_id == 2 and row.category_id not in type_dict else 0
            result_list.append(result)
        return util.flask_return_success(result_list)
    except Exception as e:
        return util.flask_handle_exception(e)


@app.route('/user', methods=['GET'], strict_slashes=False)
@jwt_required
def get_user():
    filters = util.get_args(received_args=request.args, optional_args={'id': str, 'username': str})
    try:
        users = db.get_rows(db.User, filters)
        return util.flask_return_success([i.jsondict for i in users])
    except Exception as e:
        return util.flask_handle_exception(e)


@app.route('/user', methods=['POST'], strict_slashes=False)
def post_user():
    try:
        util.flask_validate_request_is_json(request)
        now = datetime.datetime.now()
        uuid = str(util.generate_uuid())
        in_user = util.get_args(request.json,
                                required_args={'username': str, 'password': str},
                                defaultable_args={'id': uuid, 'created_at': now, 'updated_at': now, 'payload': {}})
        in_user['password'] = generate_password_hash(in_user['password'])
        user = db.add_row(db.User, in_user)
        identity = util.create_jwt_identity(user)
        return util.flask_return_success({'jwt': create_jwt(identity), 'user': user.jsondict})
    except Exception as e:
        return util.flask_handle_exception(e)


@app.route('/user', methods=['PUT'], strict_slashes=False)
@jwt_required
def put_user():
    try:
        util.flask_validate_request_is_json(request)
        now = datetime.datetime.now()
        in_user = util.get_args(request.json,
                                optional_args={'username': str, 'password': str},
                                defaultable_args={'created_at': now, 'updated_at': now, 'payload': {}})
        in_user['password'] = generate_password_hash(in_user['password'])
        filters = {'id': get_jwt_identity()}
        user = db.update_row(db.User, filters, in_user)
        return util.flask_return_success(user.jsondict)
    except Exception as e:
        return util.flask_handle_exception(e)


@app.route('/user', methods=['PATCH'], strict_slashes=False)
@jwt_required
def patch_user():
    try:
        util.flask_validate_request_is_json(request)
        now = datetime.datetime.now()
        in_user = util.get_args(request.json, required_args={'id': str}, defaultable_args={'updated_at': now},
                                optional_args={'created_at': datetime.datetime, 'username': str,
                                               'password': str, 'payload': dict})
        if 'password' in in_user:
            in_user['password'] = generate_password_hash(in_user['password'])
        filters = {'id': in_user.pop('id', None)}
        user = db.update_row(db.User, filters, in_user)
        return util.flask_return_success(user.jsondict)
    except Exception as e:
        return util.flask_handle_exception(e)


@app.route('/test/cooperstest/compstat', methods=['GET'], strict_slashes=False)
@jwt_required
def get_cooperstest_compstat():
    try:
        user_id = get_jwt_identity()
        filters = {'type_id': int(RecordType.COOPERS_TEST)}
        records = db.get_rows(db.Record, filters)

        # sort records based on user_id and creation date to pick most recent result per user
        # TODO: do sorting in db.get_rows
        records.sort(key=lambda x: (x.user_id, x.created_at), reverse=True)
        filtered_records = list()
        lag_user_id = None
        user_record = None
        for record in records:
            if lag_user_id != record.user_id:
                lag_user_id = record.user_id
                filtered_records.append(record)
                if user_id == str(record.user_id):
                    user_record = record

        # sort filtered records and get index for quantile calculation
        try:
            index = sorted(filtered_records, key=lambda x: x.payload['distance']).index(user_record)
        except ValueError:
            index = None

        if index is None or len(filtered_records) == 0:
            quantile = 0
        else:
            quantile = (index + 1) / len(filtered_records)
        return util.flask_return_success({'quantile': quantile})

    except Exception as e:
        return util.flask_return_exception(e, 500)


@app.route('/test/pushup60test/compstat', methods=['GET'], strict_slashes=False)
@jwt_required
def get_pushup60test_compstat():
    try:
        user_id = get_jwt_identity()
        if user_id is None:
            return jsonify({'message': 'Undefined user id.'}), 400
        filters = {'type_id': int(RecordType.PUSH_UP_60_TEST)}
        records = db.get_rows(db.Record, filters)

        # sort records based on user_id and creation date to pick most recent result per user
        # TODO: sort in db.get_rows

        records.sort(key=lambda x: (x.user_id, x.created_at), reverse=True)
        filtered_records = list()
        lag_user_id = None
        user_record = None
        for record in records:
            if lag_user_id != record.user_id:
                lag_user_id = record.user_id
                filtered_records.append(record)
                if user_id == str(record.user_id):
                    user_record = record

        # sort filtered records and get index for quantile calculation
        filtered_records.sort(key=lambda x: x.payload['pushups'])
        try:
            index = filtered_records.index(user_record)
        except ValueError:
            index = None

        if index is None or len(filtered_records) == 0:
            quantile = 0
        else:
            quantile = (index + 1) / len(filtered_records)
        return jsonify({'result': {'quantile': quantile}}), 200

    except Exception as e:
        return util.flask_return_exception(e, 500)

@app.route('/record', methods=['GET'], strict_slashes=False)
@jwt_required
def get_record():
    filters = util.get_args(received_args=request.args, optional_args={'id': str, 'user_id': str, 'event_id': str})
    try:
        rows = db.get_rows(db.Record, filters)
        return util.flask_return_success([row.jsondict for row in rows])
    except Exception as e:
        return util.flask_handle_exception(e)


@app.route('/record', methods=['POST'], strict_slashes=False)
@jwt_required
def post_record():
    try:
        util.flask_validate_request_is_json(request)
        now = datetime.datetime.now()
        uuid = str(util.generate_uuid())
        row = util.get_args(request.json,
                            optional_args={'event_id': str},
                            defaultable_args={'id': uuid, 'created_at': now, 'updated_at': now,
                                              'payload': {}, 'type_id': 0, 'user_id': get_jwt_identity()})

        # Add created_user which defaults to the user_id, merging it with the main row object.
        created_user = util.get_args(request.json, defaultable_args={'created_user_id': row['user_id']})
        row.update(created_user)

        # And finally add details of who validated the record and when if provided.
        validated = util.get_args(request.json, defaultable_args={'validated_at': now},
                                  optional_args={'validated_user_id': str})
        if 'validated_user_id' in validated:
            row.update(validated)

        record = db.add_row(db.Record, row)
        return util.flask_return_success(record.jsondict)
    except Exception as e:
        return util.flask_handle_exception(e)


@app.route('/record', methods=['PATCH'], strict_slashes=False)
@jwt_required
def patch_record():
    try:
        util.flask_validate_request_is_json(request)
        now = datetime.datetime.now()
        row = util.get_args(request.json,
                            required_args={'id': str},
                            defaultable_args={'updated_at': now},
                            optional_args={'created_at': datetime.datetime, 'payload': dict, 'type_id': int,
                                           'event_id': str})

        # Add created_user which defaults to the user_id, merging it with the main row object.
        created_user = util.get_args(request.json, defaultable_args={'created_user': get_jwt_identity()})
        row.update(created_user)

        # And finally add details of who validated the record and when if provided.
        validated = util.get_args(request.json, defaultable_args={'validated_at': now},
                                  optional_args={'validated_user_id': str})
        if validated['validated_user_id'] is not None:
            row.update(validated)

        filters = {'id': row.pop('id', None)}
        record = db.update_row(db.Record, filters, row)
        return util.flask_return_success(record.jsondict)
    except Exception as e:
        return util.flask_handle_exception(e)


@app.route('/record', methods=['PUT'], strict_slashes=False)
@jwt_required
def put_record():
    try:
        util.flask_validate_request_is_json(request)
        now = datetime.datetime.now()
        uuid = str(util.generate_uuid())
        row = util.get_args(request.json,
                            defaultable_args={'id': uuid, 'created_at': now, 'updated_at': now,
                                              'payload': {}, 'type_id': 0, 'user_id': get_jwt_identity()},
                            optional_args={'event_id': str})
        filters = {'id': row.pop('id', None)}

        # Add created_user which defaults to the user_id, merging it with the main row object.
        created_user = util.get_args(request.json, defaultable_args={'created_user': get_jwt_identity()})
        row.update(created_user)

        # And finally add details of who validated the record and when if provided.
        validated = util.get_args(request.json, defaultable_args={'validated_at': now},
                                  optional_args={'validated_user_id': str})
        if validated['validated_user_id'] is not None:
            row.update(validated)

        record = db.update_row(db.Record, filters, row)
        return util.flask_return_success(record.jsondict)
    except Exception as e:
        return util.flask_handle_exception(e)


@app.route('/event', methods=['GET'], strict_slashes=False)
@jwt_required
def get_event():
    filters = util.get_args(received_args=request.args, optional_args={'id': str, 'user_id': str, 'type_id': int})
    try:
        rows = db.get_rows(db.Event, filters)
        return util.flask_return_success([row.jsondict for row in rows])
    except Exception as e:
        return util.flask_handle_exception(e)


@app.route('/event', methods=['POST'], strict_slashes=False)
@jwt_required
def post_event():
    try:
        util.flask_validate_request_is_json(request)
        now = datetime.datetime.now()
        uuid = str(util.generate_uuid())
        row = util.get_args(request.json,
                            required_args={'name': str, 'description': str, 'address': str,
                                           'postal_code': str, 'event_at': datetime.datetime},
                            defaultable_args={'id': uuid, 'created_at': now, 'updated_at': now,
                                              'payload': {}, 'organization_id': 0,
                                              'user_id': get_jwt_identity()})
        event = db.add_row(db.Event, row)
        return util.flask_return_success(event.jsondict)
    except Exception as e:
        return util.flask_handle_exception(e)


@app.route('/event', methods=['PUT'], strict_slashes=False)
@jwt_required
def put_event():
    try:
        util.flask_validate_request_is_json(request)
        now = datetime.datetime.now()
        uuid = str(util.generate_uuid())
        row = util.get_args(request.json,
                            required_args={'name': str, 'description': str, 'address': str,
                                           'postal_code': str, 'event_at': datetime.datetime},
                            defaultable_args={'id': uuid, 'created_at': now, 'updated_at': now,
                                              'payload': {}, 'organization_id': 0,
                                              'user_id': get_jwt_identity()})

        filters = {'id': row.pop('id', None)}
        event = db.update_row(db.Event, filters, row)
        return util.flask_return_success(event.jsondict)
    except Exception as e:
        return util.flask_handle_exception(e)


@app.route('/user-event-link', methods=['GET'], strict_slashes=False)
@jwt_required
def get_user_event_link():
    filters = util.get_args(received_args=request.args, optional_args={'user_id': str, 'event_id': str})
    try:
        rows = db.get_rows(db.UserEventLink, filters)
        return util.flask_return_success([row.jsondict for row in rows])
    except Exception as e:
        return util.flask_handle_exception(e)


@app.route('/user-event-link', methods=['POST'], strict_slashes=False)
@jwt_required
def post_user_event_link():
    try:
        util.flask_validate_request_is_json(request)
        now = datetime.datetime.now()
        row = util.get_args(request.json, required_args={'event_id': str},
                            defaultable_args={'created_at': now, 'updated_at': now,
                                              'user_id': get_jwt_identity(), 'payload': {}})

        obj = db.add_row(db.UserEventLink, row)
        return util.flask_return_success(obj.jsondict)
    except Exception as e:
        return util.flask_handle_exception(e)


@app.route("/")
def hello():
    return "Greetings from the Tikki API"

if __name__ == "__main__":
    app.run()
