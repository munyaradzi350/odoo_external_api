from flask import Flask, jsonify, request

import xmlrpc.client

app = Flask(__name__)

# Odoo connection parameters
url = 'http://20.164.146.60'
db = 'bitnami_odoo'
username = 'user@example.com'
password = 'FKOF4pOJIV'

# Function to authenticate with Odoo
def authenticate():
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    return common.authenticate(db, username, password, {})


# {
#     "name": "New Product",
#     "list_price": 50.00,
#     "standard_price": 40.00,
#     "qty_available": 100,
#     "type": "product",
#     "detailed_type": "product",
#     "invoice_policy": "delivery"
# }


# Creating a product
@app.route('/create_product', methods=['POST'])
def create_product():
    uid = authenticate()
    if not uid:
        return jsonify({'error': 'Authentication failure'}), 401

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    product_data = request.json

    product_id = models.execute_kw(db, uid, password, 'product.product', 'create', [product_data])

    if product_id:
        return jsonify({'message': f'Product created with ID: {product_id}'}), 201
    else:
        return jsonify({'error': 'Failed to create the product.'}), 500


@app.route('/search_product', methods=['GET'])
def search_product():
    uid = authenticate()
    if not uid:
        return jsonify({'error': 'Authentication failure'}), 401

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    product_name = request.args.get('name')

    product_ids = models.execute_kw(db, uid, password, 'product.product', 'search', [[['name', '=', product_name]]])

    if product_ids:
        product_details = models.execute_kw(db, uid, password, 'product.product', 'read', [product_ids], {
            'fields': ['name', 'list_price', 'standard_price', 'qty_available', 'type', 'detailed_type',
                       'invoice_policy']})
        return jsonify(product_details)
    else:
        return jsonify({'message': 'Product not found.'}), 404

    # {
    #     "name": "Updated Product",
    #     "list_price": 120.00
    # }



@app.route('/update_product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    uid = authenticate()
    if not uid:
        return jsonify({'error': 'Authentication failure'}), 401

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    updated_data = request.json

    success = models.execute_kw(db, uid, password, 'product.product', 'write', [[product_id], updated_data])

    if success:
        return jsonify({'message': 'Product updated successfully.'}), 200
    else:
        return jsonify({'error': 'Failed to update the product.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
