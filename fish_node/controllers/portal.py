# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict
from operator import itemgetter

from odoo import http, tools, api
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
import re
from getmac import get_mac_address


class CustomerPortal(CustomerPortal):

    MANDATORY_FIELDS_NODE_ADD = ["name", "device_type_id", "connection_type_id", "mac"]
    MANDATORY_FIELDS_NODE_EDIT = ["name", "device_type_id"]
    MANDATORY_FIELDS_ACCOUNT = ["name", "email", "afdeling"]
    OPTIONAL_FIELDS_ACCOUNT = ["phone"]

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        values['node_ids'] = request.env['orxnet.node'].search([])
        return values

    # ----------------------------------------- Account -------------------------------------------------------------- #

    def account_layout_values(self, partner):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        values.update({
            'partner': partner,
            'page_name': 'my_details',
            'afdelingen': request.env['orkz.afdeling'].search([]),
            'error': {},
            'error_message': [],
        })
        return values

    def account_post(self, partner, post):
        values = {key: post[key] for key in self.MANDATORY_FIELDS_ACCOUNT}
        values.update({key: post[key] for key in self.OPTIONAL_FIELDS_ACCOUNT if key in post})
        partner.sudo().write(values)

    def details_form_validate(self, data):
        error = dict()
        error_message = []

        # Validation
        for field_name in self.MANDATORY_FIELDS_ACCOUNT:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # email validation
        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'error'
            error_message.append('Invalid Email! Please enter a valid email address.')

        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append('Some required fields are empty.')

        unknown = [k for k in data if k not in self.MANDATORY_FIELDS_ACCOUNT + self.OPTIONAL_FIELDS_ACCOUNT]
        if unknown:
            error['common'] = 'Unknown field'
            error_message.append("Unknown field '%s'" % ','.join(unknown))

        return error, error_message

    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, **post):
        partner = request.env.user.partner_id
        error, error_message = dict(), []
        if post:
            error, error_message = self.details_form_validate(post)
            if not error:
                self.account_post(partner, post)
                return request.redirect('/my/home')
        values = self.account_layout_values(partner)
        if post and error:
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
        return request.render("fish_node.portal_my_orkz_details", values)

    # ---------------------------------------- Edit Node ------------------------------------------------------------- #

    def node_edit_layout_values(self, node):
        values = {
            'page_name': 'edit_node',
            'node': node,
            'device_types': request.env['device.type'].search([]),
            'connection_types': request.env['connection.type'].search([]),
            'error': {},
            'error_message': [],
        }
        return values

    def node_edit_post(self, node, post):
        values = {key: post[key] for key in self.MANDATORY_FIELDS_NODE_EDIT}
        node.write(values)

    def node_edit_post_validate(self, post):
        error = dict()
        error_message = []
        # Required fields
        for field_name in self.MANDATORY_FIELDS_NODE_EDIT:
            if not post.get(field_name):
                error[field_name] = 'missing'
        # Error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append('Some required fields are empty.')
        return error, error_message

    @http.route(['/my/device/edit/<int:device_id>'], type='http', auth="public", website=True)
    def portal_my_node_edit(self, device_id=None, **post):
        try:
            node_sudo = self._document_check_access('orxnet.node', device_id)
        except (AccessError, MissingError):
            return request.redirect('/my/home')
        if post:
            error, error_message = self.node_edit_post_validate(post)
            if not error:
                self.node_edit_post(node_sudo, post)
                return request.redirect('/my/home')
        values = self.node_edit_layout_values(node_sudo)
        if post and error:
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
        return request.render("fish_node.portal_edit_node", values)

    # ----------------------------------------- Add Node ------------------------------------------------------------- #

    def node_add_other_layout_values(self, error={}, error_message=[], post=dict()):
        values = {
            'page_name': 'add_node',
            'device_types': request.env['device.type'].search([]),
            'connection_types': request.env['connection.type'].search([]),
            'error': error,
            'error_message': error_message,
            'previous_post_name': post.get('name') or '',
            'previous_post_device_type_id': int(post.get('device_type_id') or 0),
            'previous_post_connection_type_id': int(post.get('connection_type_id') or 0),
            'previous_post_mac': post.get('mac') or '',
        }
        return values

    def node_add_current_layout_values(self, error={}, error_message=[], post=dict()):
        values = {
            'page_name': 'add_node',
            'device_types': request.env['device.type'].search([]),
            'connection_type': self.get_connection_type(),
            'mac': get_mac_address(ip=str(request.httprequest.remote_addr)),
            'error': error,
            'error_message': error_message,
            'previous_post_name': post.get('name') or '',
            'previous_post_device_type_id': int(post.get('device_type_id') or 0),
        }
        return values

    def node_add_post(self, post):
        partner = request.env.user.partner_id
        values = {key: post[key] for key in self.MANDATORY_FIELDS_NODE_ADD}
        values.update({'partner_id': partner.id})
        node = request.env['orxnet.node'].create(values)
        self.send_email_add_node(partner, node)
        node.add_event = True

    def node_add_post_validate(self, post):
        error = dict()
        error_message = []
        # Required fields
        for field_name in self.MANDATORY_FIELDS_NODE_ADD:
            if not post.get(field_name):
                error[field_name] = 'missing'
        # Error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append('Some required fields are empty.')
        # Mac address
        if post.get('mac'):
            if not re.search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})", post.get('mac')).groups()[0]:
                error_message.append('Invalid Mac! Please enter a valid mac address.')
        return error, error_message

    def send_email_add_node(self, partner, node):
        template_obj = request.env['mail.template'].sudo().search([('name', '=', 'Customer Add Device Email')], limit=1)
        body = template_obj.body_html
        body = body.replace('--customer_name--', partner.name)
        body = body.replace('--device_name--', node.name)
        body = body.replace('--type--', node.device_type_id.name)
        body = body.replace('--connection--', node.connection_type_id.name)
        body = body.replace('--mac_address--', node.mac)
        body = body.replace('--ip_address--', node.ip)
        subject = template_obj.subject.replace('--device_name--', node.name)
        if template_obj:
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': partner.email,
                'email_from': template_obj.email_from,
            }
            request.env['mail.mail'].create(mail_values).send()

    @http.route(['/my/add/other'], type='http', auth="public", website=True)
    def portal_add_other(self, **post):
        if post:
            print('Post add other: ' + str(post))
            error, error_message = self.node_add_post_validate(post)
            print('Error: ' + str(error) + ' ' + str(error_message))
            if not error:
                print('No error')
                self.node_add_post(post)
                print('Done posting')
                return request.redirect('/my/home')
            else:
                values = self.node_add_other_layout_values(error, error_message, post)
        else:
            values = self.node_add_other_layout_values()
        return request.render("fish_node.portal_add_other_node", values)

    @http.route(['/my/add/current'], type='http', auth="public", website=True)
    def portal_add_current(self, **post):
        if post:
            error, error_message = self.node_add_post_validate(post)
            if not error:
                self.node_add_post(post)
                return request.redirect('/my/home')
            else:
                values = self.node_add_current_layout_values(error, error_message, post)
        else:
            values = self.node_add_current_layout_values()
        return request.render("fish_node.portal_add_current_node", values)

    # --------------------------------------- Delete Node ------------------------------------------------------------ #

    def send_email_delete_node(self, partner, node):
        template_obj = request.env['mail.template'].sudo().search([('name', '=', 'Customer Delete Device Email')], limit=1)
        body = template_obj.body_html
        body = body.replace('--customer_name--', partner.name)
        body = body.replace('--device_name--', node.name)
        body = body.replace('--type--', node.device_type_id.name)
        body = body.replace('--connection--', node.connection_type_id.name)
        body = body.replace('--mac_address--', node.mac)
        body = body.replace('--ip_address--', node.ip)
        subject = template_obj.subject.replace('--device_name--', node.name)
        if template_obj:
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': partner.email,
                'email_from': template_obj.email_from,
            }
            request.env['mail.mail'].create(mail_values).send()

    def node_delete_layout_values(self, node):
        values = {
            'page_name': 'delete_node',
            'node': node,
        }
        return values

    def node_delete_post(self, node):
        partner = request.env.user.partner_id
        self.send_email_delete_node(partner, node)
        node.unlink()

    @http.route(['/my/device/delete/<int:device_id>'], type='http', auth="public", website=True)
    def portal_my_node_delete(self, device_id=None, delete=None, **kw):
        try:
            node_sudo = self._document_check_access('orxnet.node', device_id)
        except (AccessError, MissingError):
            return request.redirect('/my')
        if delete:
            self.node_delete_post(node_sudo)
            return request.redirect('/my/home')
        values = self.node_delete_layout_values(node_sudo)
        return request.render("fish_node.portal_delete_node", values)

    # --------------------------------------- User functions --------------------------------------------------------- #

    def get_user_connection_type(self, ip_string=None):
        if not ip_string:
            ip_string = request.httprequest.remote_addr
        connection_types = request.env['connection.type'].sudo().search([])
        for connection_type in connection_types:
            if connection_type.contains(ip_string):
                return connection_type

    def get_user_subnet(self, ip_string=None, connection_type=None):
        if not ip_string:
            ip_string = str(request.httprequest.remote_addr)
        if not connection_type:
            connection_type = self.get_user_connection_type(ip_string)
        for subnet in connection_type.subnet_ids:
            if subnet.contains(ip_string):
                return subnet

    def is_new_device(self):
        user_ip = str(request.httprequest.remote_addr)
        user_mac = str(get_mac_address(ip=user_ip))
        if request.env['orxnet.node'].search(['mac', '=', user_mac]):
            return False
        else:
            return True

    def get_connection_type(self):
        user_subnet = self.get_user_subnet()
        if user_subnet.id == request.env.ref('fish_node.orxnet_hutspot_subnet_unregistered').id:
            return request.env.ref('fish_node.orxnet_wifi')
        if user_subnet.id == request.env.ref('fish_node.orxnet_cable_subnet_unregistered').id:
            return request.env.ref('fish_node.orxnet_cable')




