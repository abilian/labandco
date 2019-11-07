from __future__ import annotations

import json
import sys
import traceback
from json import JSONDecodeError
from pprint import pformat, pprint

from flask import Blueprint, Flask
from flask import Request as FlaskRequest
from flask import Response
from jsonrpcserver.dispatcher import call, create_requests, schema
from jsonrpcserver.methods import global_methods
from jsonrpcserver.request import Request
from jsonrpcserver.response import ErrorResponse, ExceptionResponse, \
    InvalidJSONResponse, InvalidJSONRPCResponse
from jsonrpcserver.response import Response as JsonRpcResponse
from jsonrpcserver.response import SuccessResponse
from jsonschema import ValidationError
from jsonschema.validators import validator_for
from werkzeug.exceptions import Forbidden, Unauthorized

from labster.auth import AuthContext
from labster.types import JSON

blueprint = Blueprint("rpc", __name__, url_prefix="/rpc")
route = blueprint.route

validator_class = validator_for(schema)
validator_class.check_schema(schema)
validator = validator_class(schema)


@blueprint.record
def configure(state):
    from . import (
        roles,
        structures,
        contacts,
        membres,
        demande,
        demandes,
        users,
        home,
        forms,
        home_boxes,
    )


@route("/", methods=["POST"])
def index(app: Flask, request: FlaskRequest, auth: AuthContext):
    if not auth.current_user.is_authenticated:
        raise Unauthorized()

    req = request.get_data(as_text=True)
    return run(req, app)


@route("/debug/<method_name>")
def debug(method_name: str, app: Flask, request: FlaskRequest):
    if not app.debug:
        raise Forbidden()

    args = dict(request.args)
    req_dict = {"id": 0, "jsonrpc": "2.0", "method": method_name, "params": args}
    req = json.dumps(req_dict)
    return run(req, app)


def run(req: str, app: Flask) -> Response:
    debug = app.config["DEBUG"]
    if debug:
        print(78 * "#")
        print("RPC request:")
        pprint(json.loads(req))
        print(78 * "#")
        sys.stdout.flush()

    response = dispatch(req)

    if debug:
        print(78 * "#")
        print("RPC response:")
        s = pformat(response.deserialized())
        if isinstance(response, ErrorResponse):
            print(s)
        elif len(s) < 200:
            print(s)
        else:
            print(s[0:200] + "...")
        if hasattr(response, "exc"):
            print(response.exc)
        print(78 * "#")
        sys.stdout.flush()

    return Response(str(response), response.http_status, mimetype="application/json")


def dispatch(request_raw: str) -> JsonRpcResponse:
    """
    Dispatch a request (or requests) to methods.

    This is the main public method, it's the only one with optional params, and the only
    one that can be configured with a config file/env vars.

    Args:
        request_raw: The incoming request string.

    Returns:
        A Response.

    """
    methods = global_methods
    try:
        request_json: JSON = json.loads(request_raw)
        validator.validate(request_json)
    except JSONDecodeError as exc:
        return InvalidJSONResponse(data=str(exc), debug=True)
    except ValidationError:
        return InvalidJSONRPCResponse(data=None)

    request = create_requests(request_json, convert_camel_case=False)
    assert isinstance(request, Request)

    try:
        result = call(methods.items[request.method], *request.args, **request.kwargs)
        return SuccessResponse(result=result, id=request.id)
    except Exception as exc:
        traceback.print_exc()
        sys.stdout.flush()
        sys.stderr.flush()
        return ExceptionResponse(exc, id=request.id, debug=True)
