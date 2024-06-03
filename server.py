import json
import time
from flask import Flask, render_template, request, jsonify
from urllib.parse import parse_qs
import pymongo


db_client = pymongo.MongoClient('localhost', 27017)
current_db = db_client["OXI"]

collection = current_db["OXI_tokens"]
collection2 = current_db["OXI_improvements"]
tokens = current_db["OXI_values"]

app = Flask(__name__)

vault_size_CONSTANT = {
    1: 5000,
    2: 12000,
    3: 50000,
    4: 120000,
    5: 450000,
    6: 800000,
    7: 1600000,
    8: 3500000,
    9: 5000000,
    10: 10000000
}

def update_tokens_value_vault(id):
    data = collection.find_one({'_id': id})
    data_user_2 = collection2.find_one({'_id': id})
    last_time_update = data['last_time_update']
    current_time = time.time() 
    time_difference = current_time - last_time_update
    time_different_in_hours = time_difference / 3600
    added_tokens = int(time_different_in_hours * 1000)
    vault_size = int(vault_size_CONSTANT[data_user_2['vault']])
    if added_tokens > vault_size:
        return vault_size
    return added_tokens

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/friends')
def friends():
    return render_template('friends.html')

@app.route('/getdata')
def get_data():
    query_string = request.query_string.decode('utf-8')
    parsed_data = parse_qs(query_string)
    id = json.loads(parsed_data['user'][0])
    data = collection.find_one({"_id": id['id']})

    added_tokens = update_tokens_value_vault(id['id'])
    data['added_tokens'] = added_tokens
    return jsonify(data)

@app.route('/get_counter')
def get_counter():
    query_string = request.query_string.decode('utf-8')
    parsed_data = parse_qs(query_string)
    id = json.loads(parsed_data['user'][0])

    added_tokens = update_tokens_value_vault(id['id'])
    return f"{added_tokens}"

@app.route('/update_counter')
def update_counter():
    data = request.get_json()
    query_string = request.query_string.decode('utf-8')
    parsed_data = parse_qs(query_string)
    id = json.loads(parsed_data['user'][0])
    data = tokens.find_one({"_id": id['id']})
    
    return f"{data['oxi_tokens_value']}"

@app.route('/claim_tokens')
def claim_tokens():
    query_string = request.query_string.decode('utf-8')
    parsed_data = parse_qs(query_string)
    id = json.loads(parsed_data['user'][0])
    data = collection.find_one({"_id": id['id']})
    data_user_2 = collection2.find_one({'_id': id})
    added_tokens = update_tokens_value_vault(id['id'])
    data['oxi_tokens_value'] += added_tokens
    data['last_time_update'] = time.time()
    vault_use = int(data['oxi_tokens_value'] / vault_size_CONSTANT[data_user_2['vault']] * 100)
    new_data = collection.replace_one({'_id': id['id']}, data)
    data['vault_use'] = vault_use
    return jsonify(data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=443, ssl_context=('/etc/letsencrypt/live/dmraise.ru/fullchain.pem', '/etc/letsencrypt/live/dmraise.ru/privkey.pem'))