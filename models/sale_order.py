# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class sale_order(models.Model):
    _inherit = 'sale.order'

    def get_portal_last_draft_transaction(self):
        self.ensure_one()
        return self.transaction_ids.get_last_draft_transaction()
