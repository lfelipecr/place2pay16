# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class payment_acquirer_placetopay(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('place2pay', 'PlaceToPay')], default="place2pay", ondelete={'place2pay': 'set default'})
    place2pay_login = fields.Char(string='Login', required_if_code='place2pay')
    secretkey = fields.Char(string='Secret Key', required_if_code='place2pay')
    # https://youtu.be/UlAJYJLKURQ
    # https://youtu.be/OlY93XeMhiw
    # https://youtu.be/5itKrTyGwRk

    def render(self, reference, amount, currency_id, partner_id=False, values=None):
        response = super(payment_acquirer_placetopay, self).render(reference, amount, currency_id, partner_id, values)
        _payment_transaction = self.env["payment.transaction"].search([('reference','=',reference)], limit=1)
        if(_payment_transaction):
            if(_payment_transaction.acquirer_id.code == "place2pay"):
                _payment_transaction.sudo().unlink()
        return response
