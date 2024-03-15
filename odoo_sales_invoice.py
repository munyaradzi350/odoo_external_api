from flask import Flask, request, jsonify
import xmlrpc.client

# Odoo instance details
url = 'http://20.164.146.60'
db = 'bitnami_odoo'
username = 'user@example.com'
password = 'FKOF4pOJIV'

app = Flask(__name__)

def authenticate_odoo():
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    return uid

@app.route('/create_invoice', methods=['POST'])
def create_invoice():
    uid = authenticate_odoo()
    if uid:
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        # Parse data from request
        data = request.json
        partner_id = data.get('partner_id')
        account_id = data.get('account_id')
        invoice_lines = data.get('invoice_lines')

        # Prepare invoice data
        invoice_data = {
            'partner_id': partner_id,
            'invoice_line_ids': [(0, 0, line) for line in invoice_lines],
        }

        try:
            # Creating sales invoice
            invoice_id = models.execute_kw(db, uid, password, 'account.move', 'create', [invoice_data])
            # Committing the transaction to Odoo
            models.execute_kw(db, uid, password, 'account.move', 'action_post', [[invoice_id]])
            return jsonify({'success': True, 'invoice_id': invoice_id}), 200

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    else:
        return jsonify({'success': False, 'error': 'Authentication failed. Please check your credentials.'}), 401

if __name__ == '__main__':
    app.run(debug=True)
