# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import werkzeug
from werkzeug import urls
from odoo.addons.place2pay.models.place2pay import Place2Pay
from odoo.addons.place2pay.models.payment_transaction import payment_transaction
import os, sys, hashlib, decimal, datetime, re, json
import logging
from odoo import exceptions
_logger = logging.getLogger(__name__)

class placetopay(http.Controller):

    @http.route('/place2pay/set_partner_location', methods=['POST'], type='json', auth="public", website=True)
    def set_partner_location(self, **kw):
        response = {'country_id':None, 'state_id':None, 'state_id':None, 'county_id':None, 'district_id':None, 'neighborhood_id':None, 'country':None,'state':None,'counties':None,'districts':None, 'neighborhoods':None}
        country_id = str(kw.get('country_id'))
        state_id = str(kw.get('state_id'))
        county_id = str(kw.get('county_id'))
        district_id = str(kw.get('district_id'))
        _from = str(kw.get('from'))
        _location_first_time = str(kw.get('location_first_time'))

        partner_id = kw.get('partner_id')
        try:
            if(int(partner_id) <= 0):
                pass
            else:
                if(_location_first_time == "yes"):
                    _logger.warning("si partner")
                    _partner = http.request.env['res.partner'].sudo().browse(int(partner_id))

                    response['country_id'] = country_id = _partner.country_id.id
                    response['state_id'] = state_id = _partner.state_id.id
                    response['county_id'] = county_id = _partner.county_id.id
                    response['district_id'] = district_id = _partner.district_id.id
                    response['neighborhood_id'] = _partner.neighborhood_id.id

            # country
            query = "select id, code, name from res_country where id = " + str(country_id)
            request.cr.execute(query)
            country = request.cr.dictfetchone()
            if(country):
                response['country'] = country
                _logger.warning("si country 1")

                # state
                state = None
                _logger.warning('state_id')
                _logger.warning(state_id)
                try:
                    if(int(state_id)>0):
                        query = "select id, code, name from res_country_state where id = " + str(state_id)
                except:
                    query = "select id, code, name from res_country_state where country_id = " + str(country['id'])

                _logger.warning(query)
                request.cr.execute(query)
                state = request.cr.dictfetchone()
                _logger.warning(state)
                if(state):
                    response['state'] = state
                    _logger.warning("si states 1")
                    # county
                    query = "select id, code, name from res_country_county where state_id = " + str(state['id'])
                    request.cr.execute(query)
                    counties = request.cr.dictfetchall()
                    _logger.warning(query)
                    _logger.warning(counties)
                    if(counties):
                        response['counties'] = counties
                        _logger.warning("si counties 1")
                        for county in counties:

                            try:
                                if(int(county_id)>0):
                                    query = "select id, code, name from res_country_district where county_id = " + str(county_id)
                            except:
                                query = "select id, code, name from res_country_district where county_id = " + str(counties[0]['id'])

                            request.cr.execute(query)
                            districts = request.cr.dictfetchall()
                            _logger.warning(query)
                            if(districts):
                                response['districts'] = districts
                                _logger.warning("si districts 1")

                                try:
                                    if(int(district_id)>0):
                                        query = "select id, code, name from res_country_neighborhood where district_id = " + str(district_id)
                                except:
                                    query = "select id, code, name from res_country_neighborhood where district_id = " + str(districts[0]['id'])
                                request.cr.execute(query)
                                neighborhoods = request.cr.dictfetchall()
                                _logger.warning(query)
                                if(neighborhoods):
                                    response['neighborhoods'] = neighborhoods


        except Exception as e:
           exc_traceback = sys.exc_info()
           _logger.warning(getattr(e, 'message', repr(e))+" ON LINE "+format(sys.exc_info()[-1].tb_lineno))
        return response

    @http.route('/place2pay/set_document_type', methods=['POST'], type='json', auth="public", website=True)
    def set_document_type(self, **kw):
        http.request.session['identification_id'] = str(kw.get('code'))

    def non_sql_injection(self, params):
        is_psql_query = False
        if(params):
            for param in params:
                try:
                    request.cr.execute(param)
                    psql_response = request.cr.dictfetchone()
                    if (psql_response):
                        is_psql_query = True
                        _logger.warning("SQL INJECTION")
                        _logger.warning(param)
                        return is_psql_query
                except Exception as e:
                    exc_traceback = sys.exc_info()
                    _logger.warning(getattr(e, 'message', repr(e))+" ON LINE "+format(sys.exc_info()[-1].tb_lineno))
        return is_psql_query

    @http.route('/place2pay/get_document_types', methods=['POST'], type='json', auth="public", website=True)
    def get_document_types(self, **kw):
        response = {"document_types":None, "options":None}
        try:
            options = ""
            query = "select id, code, name from res_country where id = " + str(kw.get('country_id'))
            request.cr.execute(query)
            country = request.cr.dictfetchone()
            document_types = None
            if(str(country["code"])!="BR" and str(country["code"])!="CO" and str(country["code"])!="CR" and str(country["code"])!="EC" and str(country["code"])!="PS" and str(country["code"])!="US" and str(country["code"])!="US" and str(country["code"])!="PA" and str(country["code"])!="PE"):
                query = "select id, code, name from res_country where code = '" + str("XX") + str("'")
                request.cr.execute(query)
                country = request.cr.dictfetchone()
                query = "select id, code, name from l10n_latam_document_type where country_id = " + str(country['id'])
            else:
                query = "select id, code, name from l10n_latam_document_type where country_id = " + str(kw.get('country_id'))
            request.cr.execute(query)
            document_types = request.cr.dictfetchall()
            if(document_types):
                for document_type in document_types:
                    options = str(options) + str("<option value='" + str(document_type["id"]) + "' code='" + str(document_type["code"]) + "'>") + str(document_type["name"]) + str("</option>")
            response["options"] = options
            response["document_types"] = document_types
        except Exception as e:
           exc_traceback = sys.exc_info()
           raise Warning(getattr(e, 'message', repr(e))+" ON LINE "+format(sys.exc_info()[-1].tb_lineno))
        return response

    @http.route('/place2pay/process_payment', methods=['GET'], type='http', auth="public", website=True)
    def process_payment(self):
        _logger.warning("PROCESS PAYMENT")
        for key,value in request.session.items():
            _logger.warning(str(key) + str(value))
        _p2p = Place2Pay()
        _logger.warning(http.request.session.p2p_request_id)
        _logger.warning(http.request.session.p2p_order_id)
        transaction = self.get_transaction(http.request.session.p2p_request_id)
        acquirer = self.get_this_acquirer()
        _logger.warning(acquirer)
        _p2p.set_webservice_call(str(http.request.session.p2p_request_id), acquirer["state"])
        payload = _p2p.get_payment_request_information({"login":acquirer["place2pay_login"], "secretkey":acquirer["secretkey"]})
        _payment_information = _p2p.send_request(payload, acquirer["state"])
        _logger.warning(_payment_information)
        self.unlink_non_p2p_payments_transactions(http.request.session.p2p_order_id)
        self._process_payment(_payment_information, http.request.session.p2p_order_id)
        # transaction updated and handles redirection to e-commerce
        transaction = self.get_transaction(http.request.session.p2p_request_id)
        if(not _payment_information):
            http.request.env['payment.transaction'].sudo().cron()
        return self.ecommerce_redirection(transaction, http.request.session.p2p_order_id)

    @http.route('/place2pay/notification', methods=['POST'], type='json', auth="public")
    def process_notification(self):
        response = request.jsonrequest
        _p2p = Place2Pay()
        if not response.get('requestId') or not response.get('reference'):
            return False
        transaction = self.get_transaction(response.get('requestId'))
        _logger.warning(transaction)
        if transaction:
            order = self.get_order_by_transaction(transaction['id'])
            _logger.warning("order")
            _logger.warning(order)
            if(order):
                acquirer = self.get_this_acquirer()
                _logger.warning(acquirer)
                _p2p.set_webservice_call(str(response.get('requestId')), acquirer["state"])
                payload = _p2p.get_payment_request_information({"login": acquirer["place2pay_login"], "secretkey": acquirer["secretkey"]})
                _payment_information = _p2p.send_request(payload, acquirer["state"])
                _logger.warning(_payment_information)
                self.unlink_non_p2p_payments_transactions(order['id'])
                self._process_payment(_payment_information, order['id'])
        return None

    def get_this_acquirer(self):
        query = "select name, website_id,company_id, state, place2pay_login, secretkey from payment_provider where code = 'place2pay' limit 1"
        request.cr.execute(query)
        acquirer = request.cr.dictfetchone()
        return acquirer

    @http.route('/place2pay/get_acquirer', methods=['POST'], type='json', auth="public", website=True)
    def get_acquirer(self):
        response = {"acquirer":None}
        #query = "select name, website_id,company_id, environment, website_published, place2pay_login, secretkey from payment_acquirer where provider = 'place2pay' limit 1"
        query = "select name, website_id,company_id, state, place2pay_login from payment_provider where code = 'place2pay' limit 1"
        request.cr.execute(query)
        acquirer = request.cr.dictfetchone()
        response = {"acquirer":acquirer}
        return response

    # @param partner_id
    # @param online_payment
    @http.route('/place2pay/payment_request', methods=['POST'], type='json', auth="public", website=True)
    def payment_request(self, **kw):
        params = {}
        params['partner_id'] = kw.get('partner_id')
        params['online_payment'] = kw.get('online_payment')

        response = {"status":"FAIL", "message":"", "url":"/"}

        # GET ACQUIRER
        query = "select id, name, website_id,company_id, state, place2pay_login, secretkey from payment_provider where code = 'place2pay' limit 1"
        request.cr.execute(query)
        acquirer = request.cr.dictfetchone()

        # GET BUYER FOR SHIPPING
        res_partner_shipping = self.get_buyer(params['partner_id'])

        # GET ORDER
        draft_order = self.get_order(params['partner_id'], params['online_payment'])

        has_info = self.has_pending_payments(draft_order)
        _has_transactions = has_info['_has_transactions']
        pending_transactions = has_info['pending_transactions']
        if(_has_transactions):
            transaction_text = "transacción"
            if(len(pending_transactions)>0):
                transaction_text = "transacciones"
            state_text = "pendiente"
            if(len(state_text)>0):
                state_text = "pendientes"
            pending_transaction_text = str()
            for pending_transaction in pending_transactions:
                pending_transaction_text = str("Placetopay") + str("<br>") + str("Transacción: ") + str(pending_transaction.reference) + str("<br>") + str("Referencia Nº: ") + str(pending_transaction.p2p_reference) + str("\n")
            return {"status":"FAIL", "message": str("Lo sentimos, tiene ") + str(transaction_text) + " " + str(state_text) + str(" por validar. Por favor esperar a la respuesta del banco emisor." + str("\n") + str(pending_transaction_text))}

        # FORMAT NAME & SURNAME
        _full_name = self.get_buyer_fullname(res_partner_shipping["name"])
        try:
            identification_id = str(http.request.session["identification_id"])
            if res_partner_shipping["document_type"]:
                identification_id = str(res_partner_shipping["document_type"])
            elif(str(identification_id)==str("None")):
                identification_id = str(res_partner_shipping["document_type"])
        except:
            identification_id = str(res_partner_shipping["document_type"])
        payload =   {
                        # AUTH
                            "login": acquirer["place2pay_login"],
                            "secretkey": acquirer["secretkey"],
                        # BUYER
                            "buyer_name": _full_name["name"],
                            "buyer_surname": _full_name["surname"],
                            "buyer_email": res_partner_shipping["email"],
                            "buyer_document": str(res_partner_shipping["vat"]),
                            "buyer_identification_id": identification_id,
                            "buyer_mobile": res_partner_shipping["mobile"] if res_partner_shipping["mobile"] and len(res_partner_shipping["mobile"]) else res_partner_shipping["phone"],
                        # PAYER
                            "payer_document": str(res_partner_shipping["vat"]),
                            "payer_identification_id": identification_id,
                        # PAYMENT
                            "order_name": draft_order["name"],
                            "order_description": str("Pedido\n") + str("ID: ") +str(draft_order["id"]) + str("\n") + str("NAME: ")  + str(draft_order["name"]),
                            "order_amount_currency": self.get_order_currency(draft_order["id"]),
                            "order_amount_total": draft_order["amount_total"],
                            "order_amount_untaxed": draft_order["amount_untaxed"],
                            "order_amount_tax": draft_order["amount_tax"],
                        # EXTRA
                            "return_url": self.get_return_url(),
                            "ip": self.get_ip(),
                            "user_agent": self.get_user_agent(),
                            "locale": res_partner_shipping["lang"],
                    }
        _logger.warning(payload)
        _p2p = Place2Pay()
        payload = _p2p.create_payment_request(payload)
        _payment_request = _p2p.send_request(payload, acquirer["state"])
        _payment_response = _payment_request["status"]

        if(str(_payment_response['status']) =="OK"):
            response["url"] = str(_payment_request['processUrl'])
            response["message"] = str(_payment_response['message'])
            response["status"] = str("OK")
            _transaction = self.prepare_payment_response({"_payment_request":_payment_request,"order":draft_order, "partner":res_partner_shipping, "acquirer":acquirer}, payload)
            self.action_send_notification(draft_order['id'], draft_order['name'], _transaction, response["message"])
        else:
            response["message"] = str(_payment_response['message'])
        return response

    def has_pending_payments(self, draft_order):
        transactions = self.get_order_transactions(draft_order['id'])
        _pending_transactions = []
        _has_transactions = False
        for transaction in transactions:
            _payment_transaction = http.request.env['payment.transaction'].sudo().browse(int(transaction['transaction_id']))
            if(_payment_transaction.p2p_request_id):
                if(_payment_transaction.state == 'pending' or _payment_transaction.state == 'authorized'):
                    _pending_transactions.append(_payment_transaction)
                    _has_transactions = True
        return {'_has_transactions':_has_transactions, 'pending_transactions':_pending_transactions}

    def action_send_notification(self, _id, _record_name, _transaction, message=None):
        _mail_messages = http.request.env['mail.message'].sudo().search([('res_id', '=', _id), ('body', 'ilike', str(_transaction.p2p_request_id))])
        _logger.warning('_mail_messages')
        _logger.warning(_mail_messages)
        if(_mail_messages):
            for _mail_message in _mail_messages:
                mail_message = http.request.env['mail.message'].sudo().browse(int(_mail_message.id))
                _logger.warning(mail_message.body)
                if(message):
                    mail_message.sudo().update({'body': str(mail_message.body) + str("<br>") + str(message)})
        else:
            mail_message_values = {
                                        'email_from': http.request.env.user.partner_id.email,
                                        'author_id': http.request.env.user.partner_id.id,
                                        'model': 'sale.order',
                                        'message_type': 'comment',
                                        'body': str("Placetopay") + str("<br>") + str("Transacción: ") + str(_transaction.reference) + str("<br> <span style='display:none;'>") + str("Petición Nº: ") + str(_transaction.p2p_request_id) + str("</span>") + str("Referencia Nº: ") + str(_transaction.p2p_reference) + str("<br>")+ str(message),
                                        'res_id': _id,
                                        'subtype_id': http.request.env.ref('mail.mt_comment').id,
                                        'record_name': _record_name,
                                    }
            http.request.env['mail.message'].sudo().create(mail_message_values)

    def get_buyer(self, partner_id):
        query = "select res_partner.id, res_partner.name, res_partner.identification_id, res_partner.vat, res_partner.phone, res_partner.mobile, res_partner.email, res_partner.street, res_partner.city, res_partner.zip, res_partner.lang, res_country.name as country_name, res_country.code as country_code, res_country_state.name as state_name, res_currency.name as currency_name, res_currency.symbol as currency_symbol from res_partner left join res_country on res_country.id = res_partner.country_id left join res_country_state on res_country_state.id = res_partner.state_id left join res_currency on res_country.currency_id = res_currency.id   where res_partner.id = '"+str(partner_id)+"' limit 1"
        request.cr.execute(query)
        res_partner_shipping = request.cr.dictfetchone()
        query = "select id, code, name, doc_code_prefix from l10n_latam_document_type where id = " + str(res_partner_shipping['identification_id'])
        request.cr.execute(query)
        document_type = request.cr.dictfetchone()
        res_partner_shipping["document_type"] = document_type["doc_code_prefix"]
        _logger.warning("res_partner_shipping")
        _logger.warning(res_partner_shipping)
        _logger.warning(document_type)
        return res_partner_shipping

    def get_order(self, partner_id, online_payment):
        query = ""
        if(online_payment=="no"):
            query = "select id, name, amount_untaxed, amount_total, amount_tax, date_order, partner_shipping_id from sale_order where partner_id = '"+str(partner_id)+"' and state = '"+str('draft')+"' order by date_order desc limit 1"
        if(online_payment=="yes"):
            query = "select id, name, amount_untaxed, amount_total, amount_tax, date_order, partner_shipping_id from sale_order where partner_id = '"+str(partner_id)+"' and state = '"+str('sent')+"' and require_payment = True order by date_order desc limit 1"
        request.cr.execute(query)
        order = request.cr.dictfetchone()
        return order

    def _get_order(self, order_id):
        query = "select * from sale_order where id = "+str(order_id)
        request.cr.execute(query)
        order = request.cr.dictfetchone()
        return order

    def get_order_by_transaction(self, transaction_id):
        query = "select sale_order_id from sale_order_transaction_rel where transaction_id = " + str(transaction_id)
        request.cr.execute(query)
        transaction = request.cr.dictfetchone()
        if(transaction):
            if("sale_order_id" in transaction):
                query = "select id, name, amount_total, amount_tax, date_order, partner_shipping_id from sale_order where id = "+str(transaction['sale_order_id'])+" and state in ('draft', 'sent') order by date_order desc limit 1"
                request.cr.execute(query)
                order = request.cr.dictfetchone()
                return order
            else:
                return None
        else:
            return None

    def prepare_payment_response(self, params, payload_response=None):
        http.request.session.p2p_request_id = params["_payment_request"]['requestId']
        http.request.session.p2p_order_id = params['order']['id']
        _logger.warning("http.request.session.p2p_order_id")
        _logger.warning(http.request.session.p2p_order_id)
        _transaction = self.create_transaction(params, payload_response)
        self.unlink_non_p2p_payments_transactions(params['order']['id'])
        return _transaction

    def create_transaction(self, params={}, payload_response=None):
        transaction = {
                            'partner_id':params["partner"]["id"],
                            'partner_name':str(params["partner"]["name"])[:50],
                            'date':datetime.datetime.now(),
                            'acquirer_id':int(params["acquirer"]["id"]),
                            'type':'form',
                            'state':'draft',
                            'amount':params["order"]['amount_total'],
                            'reference':str(params["order"]["name"]) + str("/") + str(params["_payment_request"]['requestId']),
                            'currency_id':int(self.get_order_currency(params["order"]['id'], "id")),
                            'state_message':str(params["_payment_request"]["status"]['message']),
                            'p2p_request_id':str(http.request.session.p2p_request_id),

                      }
        if(payload_response):
            transaction['p2p_reference'] = str(payload_response['payment']['reference'])

        _logger.warning(transaction)
        _transaction = request.env['payment.transaction'].sudo().create(transaction)

        query = "insert into  sale_order_transaction_rel (transaction_id, sale_order_id) values ("+ str(_transaction.id) +", "+ str(params["order"]['id']) +")"
        request.cr.execute(query)
        return _transaction

    def get_transaction(self, request_id=None):
        if(request_id):
            transaction = request.env['payment.transaction'].sudo().search([('p2p_request_id', '=', request_id)])
        else:
            if("p2p_request_id" in http.request.session):
                transaction = request.env['payment.transaction'].sudo().search([('p2p_request_id', '=', http.request.session.p2p_request_id)])
        return transaction

    def get_order_transactions(self, order_id):
        query = "select * from sale_order_transaction_rel where sale_order_id = '" + str(order_id) + "'"
        request.cr.execute(query)
        transactions_rel = request.cr.dictfetchall()
        return transactions_rel

    # Currency field isen't in order and just for lines
    def get_order_currency(self, order_id, brings="name"):
        draft_order_lines = http.request.env['sale.order.line'].sudo().search([['order_id','=',order_id]])
        for order_line in draft_order_lines:
            if(brings=="name"):
                return str(order_line.currency_id.name)
            if(brings=="id"):
                return str(order_line.currency_id.id)

    def get_return_url(self):
        return str(request.env['ir.config_parameter'].sudo().get_param('web.base.url')) + str("/place2pay/process_payment")

    def get_ip(self):
        return str(request.httprequest.environ['REMOTE_ADDR'])

    def get_user_agent(self):
        return str(request.httprequest.environ['HTTP_USER_AGENT'])

    def get_buyer_fullname(self, fullname):
        _name_parts = str(fullname).split(" ")
        name = ""
        surname = ""
        if(len(_name_parts)==2):
            name = str(_name_parts[0])
            surname = str(_name_parts[1])
        elif(len(_name_parts)==1):
            name = fullname
        elif(len(_name_parts)==3):
            name = str(_name_parts[0])
            surname = str(_name_parts[1]) + str(_name_parts[2])
        elif(len(_name_parts)==4):
            name = str(_name_parts[0]) + str(_name_parts[1])
            surname =  str(_name_parts[2])  + str(_name_parts[3])
        else:
            name = fullname
        return {"name":name, "surname":surname}

    def unlink_non_p2p_payments_transactions(self, order_id):
        payment_transaction.unlink_non_p2p_payments_transactions(request.env["payment.transaction"], order_id)

    def _process_payment(self, _payment_information, order_id):
        payment_transaction._process_payment(request.env["payment.transaction"], _payment_information, order_id)

    def ecommerce_redirection(self, transaction, order_id):
        try:
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url_send = str(base_url) + str("/shop/payment")
            uid = http.request.env.context.get('uid')
            odoo_order = self._get_order(order_id)
            _logger.warning("TRANSACTION")
            _logger.warning(transaction["state"])
            if(odoo_order["state"]!="draft"):
                _logger.warning("URLLANDIA444")
                if (not uid):
                    _logger.warning("URLLANDIA555")
                    order_env = request.env["sale.order"].sudo().browse(order_id)
                    sharable = order_env._get_share_url(redirect=True)
                    url_send = str(base_url) + str(sharable)
                else:
                    _logger.warning("URLLANDIA666")
                    if('require_payment' in odoo_order):
                        _logger.warning("URLLANDIA777")
                        if(odoo_order['require_payment']):
                            _logger.warning("URLLANDIA222")
                            url_send = str(base_url) + str("/my/orders/") + str(order_id)
                        else:
                            _logger.warning("URLLANDIA888")
                            url_send = str(base_url) + str("/shop/confirmation")
                    else:
                        _logger.warning("URLLANDIA333")
                        url_send = str(base_url) + str("/shop/confirmation")
            if(odoo_order["state"]=="draft"):
                _logger.warning("URLLANDIA444")
                #if (not uid):
                _logger.warning("URLLANDIA555")
                order = request.env["sale.order"].sudo().browse(order_id)
                sharable = order._get_share_url(redirect=True)
                url_send = str(base_url) + str(sharable)
            _logger.warning("URLLANDIA")
            _logger.warning(url_send)
            return werkzeug.utils.redirect(url_send)
        except Exception as e:
           exc_traceback = sys.exc_info()
           _logger.warning(getattr(e, 'message', repr(e))+" ON LINE "+format(sys.exc_info()[-1].tb_lineno))
