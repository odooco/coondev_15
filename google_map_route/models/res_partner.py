from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def route(self):
        frm_address = ''
        to_address = ''
        company = self.env.user.company_id
        if company.street:
            frm_address += company.street.replace(' ', '+')
        if company.street2:
            frm_address += (' ')
            frm_address += company.street2.replace(' ', '+')
        if company.city:
            frm_address += (' ')
            frm_address += company.city.replace(' ', '+')
        if company.state_id:
            frm_address += (' ')
            frm_address += company.state_id.name.replace(' ', '+')
        if company.zip:
            frm_address += (' ')
            frm_address += company.zip.replace(' ', '+')
        if company.country_id:
            frm_address += (' ')
            frm_address += company.country_id.name.replace(' ', '+')

        if self.street:
            to_address += self.street.replace(' ', '+')
        if self.street2:
            to_address += (' ')
            to_address += self.street2.replace(' ', '+')
        if self.city:
            to_address += (' ')
            to_address += self.city.replace(' ', '+')
        if self.state_id:
            to_address += (' ')
            to_address += self.state_id.name.replace(' ', '+')
        if self.zip:
            to_address += (' ')
            to_address += self.zip.replace(' ', '+')
        if self.country_id:
            to_address += (' ')
            to_address += self.country_id.name.replace(' ', '+')

        url = "https://www.google.co.in/maps/dir/{}/{}".format(
            frm_address, to_address)
        return {
            'name': ("map_route"),
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }


class SaleOrderAddress(models.Model):
    _inherit = 'sale.order'

    map_name = fields.Text(string='Map Name',
                           store=True, readonly=True, compute='_compute_partner')

    @api.depends('partner_id')
    def _compute_partner(self):
        for rec in self:
            rec.map_name = rec.partner_shipping_id.name

    def action_map_route_sale(self):
        self.ensure_one()
        context = self.env.context.copy()
        self = self.partner_id
        frm_address = ''
        to_address = ''
        company = self.env.user.company_id
        if company.street:
            frm_address += company.street.replace(' ', '+')
        if company.street2:
            frm_address += (' ')
            frm_address += company.street2.replace(' ', '+')
        if company.city:
            frm_address += (' ')
            frm_address += company.city.replace(' ', '+')
        if company.state_id:
            frm_address += (' ')
            frm_address += company.state_id.name.replace(' ', '+')
        if company.zip:
            frm_address += (' ')
            frm_address += company.zip.replace(' ', '+')
        if company.country_id:
            frm_address += (' ')
            frm_address += company.country_id.name.replace(' ', '+')

        if self.street:
            to_address += self.street.replace(' ', '+')
        if self.street2:
            to_address += (' ')
            to_address += self.street2.replace(' ', '+')
        if self.city:
            to_address += (' ')
            to_address += self.city.replace(' ', '+')
        if self.state_id:
            to_address += (' ')
            to_address += self.state_id.name.replace(' ', '+')
        if self.zip:
            to_address += (' ')
            to_address += self.zip.replace(' ', '+')
        if self.country_id:
            to_address += (' ')
            to_address += self.country_id.name.replace(' ', '+')

        url = "https://www.google.co.in/maps/dir/{}/{}".format(
            frm_address, to_address)
        return {
            'name': ("map_route"),
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }



class DeliveryOrderAddress(models.Model):
    _inherit = 'stock.picking'

    @api.depends('partner_id')
    def _compute_delivery_partner_name(self):
        for rec in self:
            rec.delivery_name = rec.partner_id.name

    def action_map_route_delivery(self):
        self.ensure_one()
        context = self.env.context.copy()
        self = self.partner_id
        frm_address = ''
        to_address = ''
        company = self.env.user.company_id
        if company.street:
            frm_address += company.street.replace(' ', '+')
        if company.street2:
            frm_address += (' ')
            frm_address += company.street2.replace(' ', '+')
        if company.city:
            frm_address += (' ')
            frm_address += company.city.replace(' ', '+')
        if company.state_id:
            frm_address += (' ')
            frm_address += company.state_id.name.replace(' ', '+')
        if company.zip:
            frm_address += (' ')
            frm_address += company.zip.replace(' ', '+')
        if company.country_id:
            frm_address += (' ')
            frm_address += company.country_id.name.replace(' ', '+')

        if self.street:
            to_address += self.street.replace(' ', '+')
        if self.street2:
            to_address += (' ')
            to_address += self.street2.replace(' ', '+')
        if self.city:
            to_address += (' ')
            to_address += self.city.replace(' ', '+')
        if self.state_id:
            to_address += (' ')
            to_address += self.state_id.name.replace(' ', '+')
        if self.zip:
            to_address += (' ')
            to_address += self.zip.replace(' ', '+')
        if self.country_id:
            to_address += (' ')
            to_address += self.country_id.name.replace(' ', '+')

        url = "https://www.google.co.in/maps/dir/{}/{}".format(
            frm_address, to_address)
        return {
            'name': ("map_route"),
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    delivery_name = fields.Text(string='Map Name',
                                store=True, readonly=True, compute='_compute_delivery_partner_name')
