# -*- coding: utf-8 -*-
{
    'name': 'PlaceToPay - website',
    'description': "Addon para recibir pagos a través del sitio web de comercio electrónico",
    'author': "Felipe Montero Jimenez",
    'website': "https://www.linkedin.com/in/lfelipecr/",
    'summary': "PlaceToPay para sitio web de comercio electrónico",
    'version': '0.1',
    "license": "OPL-1",
    'price': '0',
    'currency': 'USD',
    'support': 'lmontero@zoho.com',
    'category': 'Website',
    "images": ["images/banner.png"],
    'depends': [
        'base',
        'website_sale',
        'payment',
        'account',
        'l10n_cr_identification_type',
        'portal',
        'mail',
        'l10n_cr_territories'
    ],
    'data': [
        'views/payment_acquirer.xml',
        'views/sale_order.xml',
        'views/payment_transaction.xml',
        'views/ir_cron.xml',
        'views/website.xml',
        'views/website_documents.xml',
        'views/website_quote_preview.xml',
        'data/default.xml',
        'views/p2p_transactions.xml',
        'views/menus.xml',
        'views/report_saleorder_document.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_frontend': [
            'place2pay/static/src/css/place2pay.css'
        ],
        'web.assets_backend': [
            'place2pay/static/src/css/place2pay.css',
        ]
    },
    'qweb': [],
    'installable': True,
}
