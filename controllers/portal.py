# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii

from odoo import fields, http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import logging
_logger = logging.getLogger(__name__)


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        SaleOrder = request.env['sale.order']
        values['draft_quotation_count'] = SaleOrder.search_count([
                                                                    ('partner_id', 'child_of', [partner.id]),
                                                                    ('state', '=', 'draft')
                                                                 ])
        _logger.warning("values['draft_quotation_count']")
        _logger.warning(values['draft_quotation_count'])
        return values
        
    @http.route(['/my/draft_quotes', '/my/draft_quotes/page/<int:page>'], type='http', auth="user", website=True)
    def portal_draft_quotes(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = [
            ('partner_id', 'child_of', [partner.id]),
            ('state', '=', 'draft')
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        #if date_begin and date_end:
        #    domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = SaleOrder.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/draft_quotes",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        quotations = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        _logger.warning('quotations')
        _logger.warning(quotations)
        request.session['my_quotations_history'] = quotations.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': quotations.sudo(),
            'page_name': 'quote',
            'pager': pager,
            'default_url': '/my/draft_quotes',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("sale.portal_my_quotations", values)