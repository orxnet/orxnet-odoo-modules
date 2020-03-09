# -*- coding: utf-8 -*-
import ipaddress
from odoo import models, fields, api


class ConnectionType(models.Model):
    _name = 'connection.type'
    _description = 'Orxnet connection type'

    name = fields.Char(required=True)
    subnet_ids = fields.One2many('orxnet.subnet', 'connection_type_id', string='Subnets')

    @api.multi
    def get_used_ips(self):
        used_ips = self.env['orxnet.node'].search([]).mapped('ip')
        # print('       Used ips: ' + str(used_ips))
        return used_ips

    @api.multi
    def get_all_ips(self):
        all_ips = []
        for subnet in self.subnet_ids:
            subnet_ips = list(map(str, ipaddress.ip_network(subnet.ip_network_string)))
            all_ips.extend(subnet_ips)
        # print('       All ips: ' + str(len(all_ips)))
        return all_ips

    @api.multi
    def get_unused_ips(self):
        used_ips = self.get_used_ips()
        all_ips = self.get_all_ips()
        unused_ips = [ip for ip in all_ips if ip not in used_ips]
        # print('      Unused ips: ' + str(len(unused_ips)))
        return unused_ips

    @api.multi
    def get_first_unused_ip(self):
        unused_ips = self.get_unused_ips()
        if not unused_ips:
            raise Warning('No unused ips left!')
            return False
        else:
            return unused_ips[0]

    @api.multi
    def contains(self, ip_string):
        for subnet in self.subnet_ids:
            if subnet.contains(ip_string):
                return True
        return False




