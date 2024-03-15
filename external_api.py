import os
import xmlrpc.client


db ='bitnami_odoo'
url ='http://20.164.146.60'
username ='user@example.com'
password ='FKOF4pOJIV'

# Initialize XML-RPC server proxy
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
#print("version info", common.version())

uid = common.authenticate(db, username, password, {})

if uid:
    print('authentication success')

else:

    print('authentication failure')

