from flask import Flask, jsonify, make_response, abort
from flask_cors import CORS
from flask_readw.process import convert_folder, NoRawFilesException, ConversionStatus
import config.config as config


app = Flask(__name__)
CORS(app)
app.config.from_object(config.config)

processes = {}

@app.route('/convert/<path:path>')
def convert(path):
    # make sure we're not already running an operation for given path
    if path in processes: abort(409)

    try:
        processes[path] = convert_folder(path)
    except NoRawFilesException:
        abort(400)

    return success_response('Requested files are being converted')

@app.route('/status/<path:path>')
def status(path):
    if not path in processes: abort(404)

    result = {
        'progress': 0.0,
        'status': 'running',
        'files': []
    }

    statuses = []

    for process in processes[path]:
        process.poll()
        statuses.append(process.status)
        result['files'].append(process.summary)

    # crude estimator of progress
    result['progress'] = round(statuses.count(ConversionStatus.success)/len(processes[path]), 2) * 100

    if ConversionStatus.running not in statuses:
        result['status'] = 'fail' if ConversionStatus.fail in statuses else 'success'
        del processes[path]

    return jsonify(result)

@app.route('/abort/<path:path>')
def abort_conversion(path):
    if not path in processes: abort(404)

    for process in processes[path]:
        process.abort()

    del processes[path]

    return success_response('Conversion successfully aborted')

def error_response(error, code):
    return make_response(jsonify({ 'error': error }), code)

def success_response(message):
    return jsonify({ 'success' : message })

@app.errorhandler(400)
def erroneous_path(error):
    return error_response('No .raw files found at specified path', 400)

@app.errorhandler(404)
def status_failed(error):
    return error_response('There is no conversion operation for the given path', 404)

@app.errorhandler(409)
def conversion_running(error):
    return error_response('There is already a conversion operation running for the given path', 409)
