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

@app.route('/create_lead', methods=['POST'])
def create_lead():
    try:
        lead_data = request.json
        logging.debug("Lead data received: %s", lead_data)
        new_lead_id = models.execute_kw(db, uid, password, 'crm.lead', 'create', [lead_data])
        return jsonify({'message': 'Lead created successfully', 'lead_id': new_lead_id}), 201
    except Exception as e:
        logging.error("Error creating lead: %s", str(e))
        return jsonify({'error': 'Failed to create lead'}), 500

@app.route('/convert_lead_to_opportunity/<int:lead_id>', methods=['POST'])
def convert_lead_to_opportunity(lead_id):
    try:
        lead = models.execute_kw(db, uid, password, 'crm.lead', 'read', [[lead_id]])

        if lead:
            # Extract customer information from lead data
            customer_info = lead[0].get('customer_info')  # Assuming customer information is stored under 'customer_info'

            if customer_info:
                customer_id = customer_info.get('id')  # Assuming 'id' is the key for customer ID in customer_info

                if customer_id:
                    opportunity_data = {'lead_id': lead_id, 'partner_id': customer_id}
                    logging.debug("Opportunity data: %s", opportunity_data)

                    opportunity_id = models.execute_kw(db, uid, password, 'crm.lead', 'convert_opportunity',
                                                       [lead_id, opportunity_data])

                    if opportunity_id:
                        return jsonify({'message': 'Lead converted to opportunity successfully',
                                        'opportunity_id': opportunity_id}), 201
                    else:
                        logging.error("Failed to convert lead to opportunity.")
                        return jsonify({'error': 'Failed to convert lead to opportunity'}), 500
                else:
                    logging.error("Customer ID is None for lead with ID %s.", lead_id)
                    return jsonify({'error': 'Customer ID is None for lead'}), 500
            else:
                logging.error("Customer info is missing for lead with ID %s.", lead_id)
                return jsonify({'error': 'Customer info is missing for lead'}), 500
        else:
            logging.error("Lead with ID %s not found.", lead_id)
            return jsonify({'error': 'Lead not found'}), 404

    except Exception as e:
        logging.error("Error converting lead to opportunity: %s", str(e))
        return jsonify({'error': 'Failed to convert lead to opportunity. {}'.format(str(e))}), 500


if __name__ == '__main__':
    app.run(debug=True)
