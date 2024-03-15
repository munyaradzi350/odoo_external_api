import logging
from flask import Flask, request, jsonify
from xmlrpc import client

app = Flask(__name__)

url = 'http://20.164.146.60'
db = 'bitnami_odoo'
username = 'user@example.com'
password = 'FKOF4pOJIV'

common = client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})
models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))

logging.basicConfig(level=logging.DEBUG)


# {
#     "name": "John Doe",
#     "email": "john@example.com",
#     "phone": "123456789",
#     "street": "123 Main Street",
#     "city": "Anytown",
#     "zip": "12345",
#     "country_id": 1,
#     // Add other fields as needed
# }


@app.route('/create_customer', methods=['POST'])
def create_customer():
    try:
        customer_data = request.json
        logging.debug("Customer data received: %s", customer_data)
        new_customer_id = models.execute_kw(db, uid, password, 'res.partner', 'create', [customer_data])
        return jsonify({'message': 'Customer created successfully', 'customer_id': new_customer_id}), 201
    except Exception as e:
        logging.error("Error creating customer: %s", str(e))
        return jsonify({'error': 'Failed to create customer'}), 500

if __name__ == '__main__':
    app.run(debug=True)
