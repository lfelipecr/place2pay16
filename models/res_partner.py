# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_cr_document_type_id = fields.Char()
    p2p_document_type = fields.Char()
    zip = fields.Char('Zip', required=False)
    city = fields.Char('City', required=False)
