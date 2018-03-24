"""Definition of the routes for gemini server."""
import flask
from flask import Flask, request
from flask_cors import CORS
from utils import DatabaseIngestion, scan_repo, validate_request_data

app = Flask(__name__)
CORS(app)


@app.route('/api/v1/readiness')
def readiness():
    """Readiness probe."""
    return flask.jsonify({}), 200


@app.route('/api/v1/liveness')
def liveness():
    """Liveness probe."""
    return flask.jsonify({}), 200


@app.route('/aagam')
def aagam():
    return flask.jsonify({"aagam": "aagam"}), 200


@app.route('/api/v1/scan', methods=['POST'])
def scan():
    """Scan endpoint for consumption of the scheduled job."""
    input_json = request.get_json()
    r = {input_json}
    return flask.jsonify(r), 200


@app.route('/api/v1/register', methods=['POST'])
def register():
    """
    Endpoint for registering a new repositor.

    Registers new information and
    updates existing repo information.
    """
    resp_dict = {
        "data": [],
        "success": True,
        "summary": "{} successfully registered"
    }
    input_json = request.get_json()
    if request.content_type != 'application/json':
        resp_dict["success"] = False
        resp_dict["summary"] = "Set content type to application/json"
        return flask.jsonify(resp_dict), 400

    validated_data = validate_request_data(input_json)
    if not validated_data[0]:
        resp_dict["success"] = False
        resp_dict["summary"] = validated_data[1]
        return flask.jsonify(resp_dict), 404
    try:
        status = DatabaseIngestion.store_record(input_json)
        resp_dict["data"] = status
    except Exception as e:
        resp_dict["success"] = False
        resp_dict["summary"] = "Database Ingestion Failure due to" + str(e)
        return flask.jsonify(resp_dict), 500

    status = scan_repo(input_json)
    if status is not True:
        resp_dict["success"] = False
        resp_dict["summary"] = "New Repo Scan Initializtion Failure"
        return flask.jsonify(resp_dict), 500
    rep_summary = resp_dict["summary"].format(input_json['git-url'])
    resp_dict["summary"] = rep_summary
    return flask.jsonify(resp_dict), 200


@app.route('/api/v1/report/<repo>')
def report(repo):
    """Endpoint for fetching generated scan report."""
    return flask.jsonify({})


if __name__ == "__main__":
    app.run()
