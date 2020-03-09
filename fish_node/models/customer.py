# -*- coding: utf-8 -*-
from odoo import models, fields, api, http


class Customer(models.Model):
    _inherit = 'res.partner'
    _description = 'Orxnet Customer'

    afdeling = fields.Char(string='Afdeling')
    node_ids = fields.One2many('orxnet.node', 'partner_id', string='Nodes')

    data_usage = fields.Integer()

    events_accepted_customer = fields.Boolean()
    events_accepted_orxnet = fields.Boolean()

    @api.multi
    def accept_events_orxnet(self):
        for this in self:
            this.events_accepted_orxnet = True

    @api.onchange('events_accepted_customer', 'events_accepted_orxnet')
    def onchange_accept_events(self):
        if self.events_accepted_customer & self.events_accepted_orxnet:
            for node_id in self.node_ids:
                node_id.accept_events()
                self.events_accepted_customer = False
                self.events_accepted_orxnet = False
        if (not self.events_accepted_customer) & self.events_accepted_orxnet:
            for node_id in self.node_ids:
                node_id.accept_events_orxnet()
                if not node_id.event_happened:
                    self.events_accepted_orxnet = False
        if self.events_accepted_customer & (not self.events_accepted_orxnet):
            for node_id in self.node_ids:
                node_id.accept_events_customer()
                if not node_id.event_happened:
                    self.events_accepted_customer = False




