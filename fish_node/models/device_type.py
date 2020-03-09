# -*- coding: utf-8 -*-
import ipaddress
from openerp import models, fields, api


class DeviceType(models.Model):
    _name = 'device.type'
    _description = 'Orxnet device type'

    name = fields.Char(required=True)


