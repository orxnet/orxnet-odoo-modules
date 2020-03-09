# -*- coding: utf-8 -*-
import ipaddress
from openerp import models, fields, api


class Rules(models.Model):
    _name = 'orxnet.rules'
    _description = 'Orxnet rules'

    add_needs_accept_from_customer = fields.Boolean(required=True)
    delete_needs_accept_from_customer = fields.Boolean(required=True)
    name_edit_needs_accept_from_customer = fields.Boolean(required=True)
    type_edit_needs_accept_from_customer = fields.Boolean(required=True)
    connection_edit_needs_accept_from_customer = fields.Boolean(required=True)
    mac_edit_needs_accept_from_customer = fields.Boolean(required=True)

    add_needs_accept_from_orxnet = fields.Boolean(required=True)
    delete_needs_accept_from_orxnet = fields.Boolean(required=True)
    name_edit_needs_accept_from_orxnet = fields.Boolean(required=True)
    type_edit_needs_accept_from_orxnet = fields.Boolean(required=True)
    connection_edit_needs_accept_from_orxnet = fields.Boolean(required=True)
    mac_edit_needs_accept_from_orxnet = fields.Boolean(required=True)


