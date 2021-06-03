from __future__ import annotations

import json
import sys
import time
import traceback
from json import JSONDecodeError
from pprint import pformat, pprint

import sentry_sdk
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

from ..domain2.services.roles import Role
from .registry import register_submodules

blueprint = Blueprint("rpc", __name__, url_prefix="/rpc")
route = blueprint.route

validator_class = validator_for(schema)
validator_class.check_schema(schema)
validator = validator_class(schema)

timer_d = {}


@blueprint.record
def configure(state):
    register_submodules()


@route("/", methods=["POST"])
def index(app: Flask, request: FlaskRequest, auth: AuthContext):
    req = request.get_data(as_text=True)
    req_json = json.loads(req)
    if app.debug:
        pprint(req_json)

    user = auth.current_user
    if user and not user.is_authenticated:
        raise Unauthorized()

    return run(req, app)


@route("/debug/<method_name>")
def debug(
    method_name: str, app: Flask, request: FlaskRequest, auth_context: AuthContext
):
    user = auth_context.current_profile
    if user and not user.has_role(Role.ADMIN_CENTRAL) and not app.debug:
        raise Forbidden()

    args = dict(request.args)
    req_dict = {"id": 0, "jsonrpc": "2.0", "method": method_name, "params": args}
    req = json.dumps(req_dict)
    return run(req, app)


def run(req: str, app: Flask) -> Response:
    if app.debug:
        print(78 * "#")
        print("# RPC request:")
        req_json = json.loads(req)
        print(78 * "#")
        sys.stdout.flush()
        timer_d[req_json["id"]] = time.time()

        response = dispatch(req)

        print(78 * "#")
        print("# RPC response:")

        print("request:")
        s = pformat(req_json)
        if len(s) < 200:
            print(s)
        else:
            print(s[0:200] + "...")

        print("response:")
        s = pformat(response.deserialized())
        if isinstance(response, ErrorResponse):
            print(s)
        elif len(s) < 200:
            print(s)
        else:
            print(s[0:200] + "...")
        if hasattr(response, "exc"):
            print(response.exc)

        req_id = req_json["id"]
        if req_id in timer_d:
            dt = 1000 * (time.time() - timer_d[req_id])
            print(f"Elapsed time: {dt:.2f}ms")
            del timer_d[req_id]

        print(78 * "#")
        sys.stdout.flush()

    else:
        response = dispatch(req)

    return Response(str(response), response.http_status, mimetype="application/json")


def dispatch(request_raw: str) -> JsonRpcResponse:
    """Dispatch a request (or requests) to methods.

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
        method_name = request.method
        method = methods.items[method_name]

        with sentry_sdk.start_span(op="rpc", transaction="rpc." + method_name) as span:
            span.set_data("args", request.args)
            span.set_data("kwargs", request.kwargs)
            result = call(method, *request.args, **request.kwargs)

        return SuccessResponse(result=result, id=request.id)

    except Exception as exc:
        traceback.print_exc()
        sys.stdout.flush()
        sys.stderr.flush()
        return ExceptionResponse(exc, id=request.id, debug=True)
