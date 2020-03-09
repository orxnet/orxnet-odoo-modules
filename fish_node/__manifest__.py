# -*- coding: utf-8 -*-
{
    'name': "Orxnet",
    'summary': "Manage customers and nodes",
    'depends': ['base', 'partner_firstname', 'portal'],
    'data': ['data/default_rules.xml',
             'data/tom_eijkelenkamp.xml',
             'data/device_types.xml',
             'data/email_template_add.xml',
             'data/email_template_delete.xml',
             'data/orxnet_wifi.xml',
             'data/orxnet_cable.xml',
             'data/orxnet_hutspot.xml',
             'views/customer.xml',
             'views/afdeling.xml',
             'views/node.xml',
             'views/connection_type.xml',
             'views/subnet.xml',
             'views/device_type.xml',
             'views/orxnet_portal_templates.xml',
             'security/ir.model.access.csv',
             'security/node_security.xml'
             ],
}
