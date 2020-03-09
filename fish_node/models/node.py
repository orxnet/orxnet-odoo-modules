# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.fields import Date as fDate
from openerp.exceptions import Warning


class Node(models.Model):
    _name = 'orxnet.node'
    _description = 'Orxnet Node'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    device_type_id = fields.Many2one('device.type', string='Device Type', required=True)
    connection_type_id = fields.Many2one('connection.type', string='Connection Type', required=True)
    name = fields.Char()
    ip = fields.Char(store=True, compute='_get_ip')
    mac = fields.Char(required=True)

    add_event = fields.Boolean(default=False)
    delete_event = fields.Boolean(default=False)
    event_happened = fields.Boolean(compute='_event_happened')

    @api.one
    def accept_connection(self):
        if self.add_event | self.partner_id.exceeds_data_limit():
            return False
        else:
            return True

    @api.multi
    def _event_happened(self):
        for this in self:
            if this.add_event or this.delete_event:
                this.event_happened = True
            else:
                this.event_happened = False

    @api.multi
    def accept_events(self):
        for this in self:
            print(str(this.name) + ' Accept: ' + str(this.delete_event) + ' ' + str(this.add_event))
            if this.delete_event:
                print('Delete')
                this.unlink()
                return
            if this.add_event:
                print('Add')
                this.add_event = False

    @api.depends('connection_type_id')
    def _get_ip(self):
        for this in self:
            if this.connection_type_id:
                if this.ip == False | this.connection_type_id.contains(this.ip) == False:
                    unused_ip = this.connection_type_id.get_first_unused_ip()
                    this.ip = unused_ip
            else:
                this.ip = False

    @api.multi
    def edit_button(self):
        view = {
            'name': ('Edit'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'orxnet.node',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'readonly': True,
            'res_id': self.id,
        }
        return view
