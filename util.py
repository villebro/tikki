from werkzeug.datastructures import MultiDict
import datetime
import flask
from typing import Dict, Any
import traceback
import json
import uuid
import db
import dateutil.parser
import os
from typing import List
import db

# Exceptions
class Flask400Exception(Exception):
    pass


class Flask500Exception(Exception):
    pass


def _add_config_from_env(app, config_key: str, env_variable: str, missing_list: List[str]) -> bool:
    """Function for adding configuration variables to a Flask app from environment variables.

    :param app: Flask app object.
    :param config_key: the name of the config key in the Flask app: app.config[config_key].
    :param env_variable: the name of the environment variable in which the value is stored.
    :param missing_list: a list of strings to which missing environment variables are added.
    :return: True if successful, False if environment variable was undefined.
    """
    val = os.environ.get(env_variable, None)
    if val is not None:
        app.config[config_key] = val
        return True
    else:
        missing_list.append(env_variable)
        return False


def init_app_config(app):
    """Initializes the Flask app with all necessary config parameters.
    """
    missing_env_vars = list()
    _add_config_from_env(app, 'JWT_SECRET_KEY', 'TIKKI_BACK_JWT_SECRET', missing_env_vars)
    _add_config_from_env(app, 'DB_USERNAME', 'TIKKI_BACK_DB_USERNAME', missing_env_vars)
    _add_config_from_env(app, 'DB_PASSWORD', 'TIKKI_BACK_DB_PASSWORD', missing_env_vars)
    _add_config_from_env(app, 'DB_HOSTNAME', 'TIKKI_BACK_DB_HOSTNAME', missing_env_vars)
    _add_config_from_env(app, 'DB_DATABASE', 'TIKKI_BACK_DB_DATABASE', missing_env_vars)

    if len(missing_env_vars) > 0:
        raise RuntimeError('Following environment variables undefined: ' + ', '.join(missing_env_vars))


def jsonify(obj):
    return json.dumps(obj)


def create_jwt_identity(user) -> Dict:
    return {'sub': str(user.id), 'rol': user.type_id}


def parse_value(value, default_type):
    if type(value) is str and default_type is datetime.datetime:
        return dateutil.parser.parse(value)
    else:
        return value if type(value) is default_type else None


def get_anydict_value(source_dict, key, default_value, default_type):
    if type(source_dict) is dict:
        value = source_dict.get(key, default_value)
        return parse_value(value, default_type)
    elif issubclass(type(source_dict), MultiDict):
        value = source_dict.get(key, default_value, default_type)
        return parse_value(value, default_type)
    else:
        raise Exception('Unsupported dict type: ' + type(source_dict).__name__)


def get_args(received_args, required_args: Dict = None, defaultable_args: Dict = None,
             optional_args: Dict = None, constant_args: Dict = None) -> Dict[str, Any]:
    # Initialize local variables

    required = dict() if required_args is None else required_args
    defaultable = dict() if defaultable_args is None else defaultable_args
    optional = dict() if optional_args is None else optional_args
    constant = dict() if constant_args is None else constant_args
    missing_args = list()
    ret_dict = dict()

    if required is None and defaultable is None and optional is None:
        raise Exception('One of the following is required: required_args, defaultable_args or optional_args.')

    # First loop through required args and add missing keys to error list

    for key, default_type in required.items():
        val = get_anydict_value(received_args, key, None, default_type)
        if val is None:
            missing_args.append(key)
        ret_dict[key] = val

    # Next loop through defaultable args, falling back to default values

    for key, default_value in defaultable.items():
        default_type = type(default_value)
        val = get_anydict_value(received_args, key, default_value, default_type)
        ret_dict[key] = val

    # Next loop through optional args, omitting them if missing

    for key, default_type in optional.items():
        val = get_anydict_value(received_args, key, None, default_type)
        if val is not None:
            ret_dict[key] = val

    # Finally copy constants

    if constant_args is not None:
        ret_dict.update(constant_args)

    # Raise error if

    if len(missing_args) > 0:
        msg = "Missing following arguments:"
        for arg in missing_args:
            msg += ' ' + arg
        raise Exception(msg)

    return ret_dict


def flask_validate_request_is_json(request):
    if not request.is_json:
        raise Flask400Exception('Request body is not JSON.')


def flask_return_exception(e, return_type: int=500):
    return flask.jsonify({'http_status_code': return_type, 'error': str(e)}), return_type


def flask_return_success(result, return_type: int=200):
    return flask.jsonify({'result': result}), return_type


def flask_handle_exception(exception):
    if type(exception) is Flask400Exception:
        return flask_return_exception(exception, 400)
    elif type(exception) is Flask500Exception:
        return flask_return_exception(exception, 500)
    elif type(exception) is db.NoRecordsException:
        return flask_return_exception(exception, 400)
    else:
        return flask_return_exception(traceback.format_exc(), 500)


def generate_uuid(count: int=1):
    if count == 1:
        ret = uuid.uuid4()
    elif count > 1:
        ret = list()
        for i in range(0, count):
            ret.append(uuid.uuid4())
    else:
        ret = None
    return ret
