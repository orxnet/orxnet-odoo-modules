#!/usr/bin/env python3
import odoorpc
import random
# Prepare the connection to the server
odoo = odoorpc.ODOO('localhost', port=8069)

# Check available databases
print(odoo.db.list())

# Login
odoo.login('boekenbalie', 'admin', 'admin')

# # access the sale.order model
# if 'sale.order' in odoo.env:
#     Order = odoo.env['sale.order']
#     order_ids = Order.search([])
#
#     # ask user for the number of records to generate
#     num = input("Enter the number of records to duplicate: ")
#     for i in range(0, int(num)+1):
#         order = Order.browse(random.choice(order_ids))
#         order.copy()
#         print("%s Successfully copied." % order.name)

# access the sale.order model
if 'sale.order' in odoo.env:
    Order = odoo.env['sale.order']
    order_ids = Order.search([('state', '=', 'draft')], limit=500)
    to_confirm = Order.browse(order_ids)
    for order in to_confirm:
        order.action_confirm()
        print("%s Confirmed!" % order.name)
