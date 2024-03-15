from flask import Flask, request, jsonify
import xmlrpc.client
import logging

# Odoo instance details
url = 'http://20.164.146.60'
db = 'bitnami_odoo'
username = 'user@example.com'
password = 'FKOF4pOJIV'

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)  # Configure logging

def authenticate_odoo():
    try:
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        return uid
    except Exception as e:
        app.logger.error('Odoo authentication failed: %s', str(e))
        return None

@app.route('/create_sales_order', methods=['POST'])
def create_sales_order():
    uid = authenticate_odoo()
    if not uid:
        return jsonify({'success': False, 'error': 'Authentication failed. Please check your credentials.'}), 401

    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    data = request.json
    if not data or 'order_data' not in data:
        return jsonify({'success': False, 'error': 'Invalid request data.'}), 400

    order_data = data['order_data']
    partner_id = order_data.get('partner_id')
    order_lines = order_data.get('order_lines')
    activities = order_data.get('activities')

    if not partner_id or not order_lines:
        return jsonify({'success': False, 'error': 'Missing required fields in request data.'}), 400

    try:
        partner_name = order_data.get('partner_name')
        if partner_name:
            existing_partner_ids = models.execute_kw(
                db, uid, password,
                'res.partner', 'search', [[('name', '=', partner_name)]]
            )
            if not existing_partner_ids:
                partner_id = models.execute_kw(
                    db, uid, password,
                    'res.partner', 'create', [{'name': partner_name}]
                )
            else:
                partner_id = existing_partner_ids[0]

        order_line_data = []
        for line in order_lines:
            order_line_data.append((0, 0, {
                'product_id': line['product_id'],
                'product_uom_qty': line['product_uom_qty'],
                'price_unit': line['price_unit']
            }))

        activity_data = []
        for activity in activities:
            activity_data.append((0, 0, {
                'name': activity['name'],
                'date_deadline': activity['date_deadline']
            }))

        order_id = models.execute_kw(
            db, uid, password,
            'sale.order', 'create', [{
                'partner_id': partner_id,
                'order_line': order_line_data,
                'activity_ids': activity_data
            }]
        )

        return jsonify({'success': True, 'order_id': order_id}), 200

    except Exception as e:
        app.logger.error('Failed to create sales order: %s', str(e))
        return jsonify({'success': False, 'error': 'Failed to create sales order. Check logs for details.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
