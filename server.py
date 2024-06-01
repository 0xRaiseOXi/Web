import json
from flask import Flask, render_template, request, jsonify
from urllib.parse import parse_qs
import pymongo


db_client = pymongo.MongoClient('localhost', 27017)
current_db = db_client["OXI"]

collection = current_db["OXI_tokens"]
collection2 = current_db["OXI_improvements"]
tokens = current_db["OXI_values"]

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getdata')
def get_data():
    query_string = request.query_string.decode('utf-8')
    parsed_data = parse_qs(query_string)
    id = json.loads(parsed_data['user'][0])
    print(id)
    print(type(id))
    print(id['id'])
    data = collection.find_one({"_id": id['id']})
    return f"{data['oxi_tokens_value']}"

@app.route('/get_counter')
def get_counter():
    query_string = request.query_string.decode('utf-8')
    parsed_data = parse_qs(query_string)
    id = json.loads(parsed_data['user'][0])
    data = tokens.find_one({"_id": id['id']})
    
    return f"{data['oxi_tokens_value']}"

@app.route('/update_counter')
def update_counter():
    data = request.get_json()
    query_string = request.query_string.decode('utf-8')
    parsed_data = parse_qs(query_string)
    id = json.loads(parsed_data['user'][0])
    data = tokens.find_one({"_id": id['id']})
    
    return f"{data['oxi_tokens_value']}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=443, ssl_context=('/etc/letsencrypt/live/dmraise.ru/fullchain.pem', '/etc/letsencrypt/live/dmraise.ru/privkey.pem'))