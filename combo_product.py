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

# Create a combo product
@app.route('/create_combo_product', methods=['POST'])
def create_combo_product():
    uid = authenticate()
    if not uid:
        return jsonify({'error': 'Authentication failure'}), 401

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    combo_product_data = request.json

    combo_product_id = models.execute_kw(db, uid, password, 'pos.combo', 'create', [combo_product_data])

    if combo_product_id:
        return jsonify({'message': f'Combo product created with ID: {combo_product_id}'}), 201
    else:
        return jsonify({'error': 'Failed to create the combo product.'}), 500

# Add individual products to a combo product
@app.route('/add_individual_products_to_combo/<int:combo_id>', methods=['POST'])
def add_individual_products_to_combo(combo_id):
    uid = authenticate()
    if not uid:
        return jsonify({'error': 'Authentication failure'}), 401

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    individual_product_ids = request.json.get('individual_product_ids', [])

    for product_id in individual_product_ids:
        combo_line_data = {
            'product_id': product_id,
            'combo_id': combo_id
        }
        combo_line_id = models.execute_kw(db, uid, password, 'pos.combo.line', 'create', [combo_line_data])
        if not combo_line_id:
            return jsonify({'error': f'Failed to add product {product_id} to the combo product.'}), 500

    return jsonify({'message': 'Individual products added to the combo product successfully.'}), 200

# Search for a combo product
@app.route('/search_combo_product', methods=['GET'])
def search_combo_product():
    uid = authenticate()
    if not uid:
        return jsonify({'error': 'Authentication failure'}), 401

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    combo_product_name = request.args.get('name')

    combo_product_ids = models.execute_kw(db, uid, password, 'pos.combo', 'search', [[['name', '=', combo_product_name]]])

    if combo_product_ids:
        combo_product_id = combo_product_ids[0]  # Assuming only one combo product matches the criteria
        combo_product_details = models.execute_kw(db, uid, password, 'pos.combo', 'read', [combo_product_id])

        return jsonify(combo_product_details)
    else:
        return jsonify({'message': 'Combo product not found.'}), 404

if __name__ == '__main__':
    app.run(debug=True)
