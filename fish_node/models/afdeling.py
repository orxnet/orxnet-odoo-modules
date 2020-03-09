# -*- coding: utf-8 -*-
import ipaddress
from openerp import models, fields, api


class DeviceType(models.Model):
    _name = 'orkz.afdeling'
    _description = 'Orkz afdeling'

    name = fields.Char(required=True)


