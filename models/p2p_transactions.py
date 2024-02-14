# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
from odoo.exceptions import Warning
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)

class Place2PayTransactions(models.Model):
    _name = 'p2p.transactions'
    _description = 'PlaceToPay Transactions'
    _table = 'payment_transaction'

    name = fields.Char(string='Name')
    reference = fields.Char(string='Reference', required=True, readonly=True, index=True, help='Internal reference of the TX')
    date = fields.Datetime('Validation Date', readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, readonly=True)
    amount = fields.Monetary(string='Amount', currency_field='currency_id', required=True, readonly=True)    
    state_message = fields.Text(string='Message', readonly=True, help='Field used to store error and/or validation messages for information')
    partner_id = fields.Many2one('res.partner', 'Customer')
    partner_name = fields.Char('Partner Name')
    p2p_reference = fields.Char("PlacetoPay Reference")
    
    state = fields.Selection([
                                ('draft', 'Draft'),
                                ('pending', 'Pending'),
                                ('authorized', 'Authorized'),
                                ('done', 'Done'),
                                ('cancel', 'Canceled'),
                                ('error', 'Error'),
                             ],
                                string='Status', 
                                copy=False, 
                                default='draft', 
                                required=True, 
                                readonly=True
                            )
    # Placetopay fields
    p2p_request_id = fields.Char("Placetopay ID")
    p2p_payment_method = fields.Char("Method")
    acquirer_id = fields.Many2one('payment.provider', string='Acquirer', readonly=True, required=True)
    acquirer_name = fields.Char('Pasarela', compute='_compute_acquirer_name', readonly=True,)
    provider = fields.Selection(string='Provider', related='acquirer_id.code', readonly=True)
    
    def _compute_acquirer_name(self):
        for model in self:
            payment_acquirer = model.env["payment.provider"].browse(model.acquirer_id.id)
            model.acquirer_name =  payment_acquirer.name
