# -*- coding: utf-8 -*-
import ipaddress
from odoo import models, fields, api


class Subnet(models.Model):
    _name = 'orxnet.subnet'
    _description = 'Orxnet subnet'

    name = fields.Char()
    ip_network_string = fields.Char(required=True)
    ip_address_count = fields.Integer(store=True, compute="_get_ip_address_count")
    connection_type_id = fields.Many2one('connection.type', string='Connection Type')

    @api.multi
    def contains(self, ip_string):
        return ipaddress.IPv4Address(ip_string) in ipaddress.ip_network(self.ip_network_string)

    @api.depends('ip_network_string')
    def _get_ip_address_count(self):
        for this in self:
            this.ip_address_count = len(list(ipaddress.ip_network(this.ip_network_string)))

    @api.constrains('ip_network_string')
    def _check_overlap_subnet(self):
        for this in self:
            print('Constrains: ', this.ip_network_string)
            ip_network = ipaddress.ip_network(this.ip_network_string)
            all_ip_network_strings = self.env['orxnet.subnet'].search([('id', '!=', this.id)]).mapped('ip_network_string')
            for existing_ip_network_string in all_ip_network_strings:
                existing_ip_network = ipaddress.ip_network(existing_ip_network_string)
                if ip_network.overlaps(existing_ip_network):
                    raise models.ValidationError('New ip network ' + this.ip_network_string + ' overlaps with existing ip network ' + existing_ip_network_string)

