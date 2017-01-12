from flask import Flask, request, jsonify, make_response, abort, Response, url_for
import db_functions
import util
import exceptions
import json


app = Flask(__name__)

public_address = json.load(open(util.path_to_this_files_directory() + 'settings.json')).get('public_address', '')


def home_cor(obj):
	return_response = make_response(obj)
	return_response.headers['Access-Control-Allow-Origin'] = "*"
	return_response.headers['Access-Control-Allow-Methods'] = 'POST,GET,OPTIONS,PUT,DELETE'
	return_response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Origin, Accept"
	return return_response


@app.errorhandler(401)
def http_401(message=''):
	if message == '':
		return home_cor(Response('Invalid Credentials', 401, {'Erebus': 'error="Invalid Credentials"'}))
	else:
		return home_cor(Response(message, 401))


@app.route('/', methods=['OPTIONS', 'GET'])
def root():
	if request.method == 'GET':
		response = {
			'endpoints': {
				'account': public_address + url_for('account')
			}
		}
		return home_cor(jsonify(**response))
	else:
		return home_cor(jsonify(**{}))


@app.route('/account', methods=['OPTIONS', 'GET'])
def account():
	if request.method == 'GET':
		response = {
			'endpoints': {
				'create': public_address + url_for('account_create'),
				'login': public_address + url_for('account_login')
			}
		}
		return home_cor(jsonify(**response))
	else:
		return home_cor(jsonify(**{}))


@app.route('/account/create', methods=['OPTIONS', 'GET'])
def account_create():
	response = dict()

	if request.method == 'OPTIONS':
		return home_cor(jsonify(**response))
	elif request.method == 'GET':
		username = request.args.get('username', '')
		password = request.args.get('password', '')

		try:
			uid = db_functions.create_user(username, password)
			response['Success'] = True
			response['uid'] = uid
			return home_cor(jsonify(**response))
		except exceptions.UsernameTakenException:
			response['Success'] = False
			response['reason'] = 'Username Taken'
			return home_cor(jsonify(**response))


@app.route('/account/login', methods=['POST', 'OPTIONS', 'GET'])
def account_login():
	response = dict()

	if request.method == 'OPTIONS':
		return home_cor(jsonify(**response))
	elif request.method == 'GET':
		username = request.args.get('username', '')
		password = request.args.get('password', '')
		aid = db_functions.login(username, password)
		response['valid_aid'] = aid[0]
		response['aid'] = aid[1]
		return home_cor(jsonify(**response))
	elif request.method == 'POST':
		data = request.json
		if data is not None:
			username = data.get('username', None)
			password = data.get('password', None)
			if username is not None and password is not None:
				db_response = db_functions.login(username, password)
				if db_response[0]:
					response['status'] = 'Success'
					response['uid'] = db_response[1]
					return home_cor(jsonify(**response))
		return http_401()

app.run(debug=True, host='0.0.0.0', port=1234)
