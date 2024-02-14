# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.addons.place2pay.models.place2pay import Place2Pay
import os, hashlib, decimal, datetime, re, json, sys
from odoo.addons.place2pay.models.place2pay import Place2Pay
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)

class payment_transaction(models.Model):
    _inherit = 'payment.transaction'

    p2p_request_id = fields.Char("Placetopay ID")
    p2p_payment_method = fields.Char("Method")
    p2p_reference = fields.Char("Reference")
    p2p_internal_transactions = fields.Html("Internal Transactions")
    
    def get_last_draft_transaction(self):
        transactions = self.filtered(lambda t: t.state == 'draft')
        return transactions and transactions[0] or transactions

    def unlink_non_p2p_payments_transactions(self, order_id):
        transactions_rel = self.get_order_transactions(order_id)
        if(transactions_rel):
            for transaction_rel in transactions_rel:
                _payment_transaction = self.env["payment.transaction"].sudo().browse(int(transaction_rel["transaction_id"]))
                if(not _payment_transaction.p2p_request_id and _payment_transaction.state == str("draft")):
                    _payment_transaction.sudo().unlink()

    def _process_payment(self, _payment_information, order_id):
        _logger.warning("_process_payment")
        if("payment" in _payment_information):
            _logger.warning("_process_payment1")
            _logger.warning(_payment_information["payment"])
            try:   
                has_receips = False 
                if("payment" in _payment_information):
                    try:
                        if(len(_payment_information["payment"] or [])):
                            has_receips = True
                    except:
                        has_receips = False
                        pass
                    if(has_receips):
                        _transaction = self.get_transaction(_payment_information["requestId"])
                        for _payment in reversed(_payment_information["payment"]):
                            if("status" in _payment):
                                _logger.warning("_process_payment2")
                                _logger.warning(_payment)
                                #_payment["status"]["status"] = "PENDING"
                                _order = self.env["sale.order"].sudo().browse(int(order_id))
                                if(str(_payment["status"]["status"]) == str("APPROVED")):
                                    _logger.warning("_process_payment3")
                                    _transaction.sudo().update({"state":"done", "p2p_payment_method":_payment["paymentMethodName"], "state_message":_payment["status"]["message"]})
                                    _transaction.sudo().write({"state":"done", "p2p_payment_method":_payment["paymentMethodName"], "state_message":_payment["status"]["message"]})
                                    state = _order.state
                                    if(state=="draft" or state=="sent" or state=="cancel"):
                                        _order.sudo().action_confirm()
                                        _order.sudo()._send_order_confirmation_mail()
                                    try:
                                        request.website.sale_reset()
                                    except:
                                        pass
                                    _order = self.env["sale.order"].sudo().browse(int(order_id))
                                    _logger.warning(_order.state)
                                elif(str(_payment["status"]["status"]) == str("REJECTED")):
                                    _transaction.sudo().update({"state":"cancel", "state_message":_payment["status"]["message"], "p2p_payment_method":_payment["paymentMethodName"]})
                                    _transaction.sudo().write({"state":"cancel", "state_message":_payment["status"]["message"], "p2p_payment_method":_payment["paymentMethodName"]})
                                elif(str(_payment["status"]["status"]) == str("PENDING")):
                                    _transaction.sudo().update({"state":"pending", "state_message":_payment["status"]["message"], "p2p_payment_method":_payment["paymentMethodName"]})
                                    _transaction.sudo().write({"state":"pending", "state_message":_payment["status"]["message"], "p2p_payment_method":_payment["paymentMethodName"]})
                                    state = _order.state
                                    _logger.warning("state_STATE")
                                    _logger.warning(state)
                                    _order.sudo().write({'state':'sent'})
                                    _order.sudo()._send_order_confirmation_mail()
                                    if(state=="draft"):
                                        _order.sudo().write({'state':'sent'})
                                        _order.sudo()._send_order_confirmation_mail()
                                    try:
                                        request.website.sale_reset()
                                    except:
                                        pass
                                elif(str(_payment["status"]["status"]) == str("DECLINED")):
                                    _transaction.sudo().update({"state":"pending", "state_message":_payment["status"]["message"], "p2p_payment_method":_payment["paymentMethodName"]})
                                    _transaction.sudo().write({"state":"pending", "state_message":_payment["status"]["message"], "p2p_payment_method":_payment["paymentMethodName"]})
                                else:
                                    _logger.warning("_process_payment4")
                                    _transaction.sudo().update({"p2p_payment_method":_payment["paymentMethodName"]})

                                self.action_send_notification(order_id, _order.name, _transaction, _payment["status"]["message"])
                        try:
                            transactions_list = self.get_transactions_list(reversed(_payment_information["payment"]))
                            _logger.warning('transactions_list')
                            _logger.warning(transactions_list)
                            _transaction.sudo().update({"p2p_internal_transactions": transactions_list})
                            _transaction.sudo().write({"p2p_internal_transactions": transactions_list})
                        except:
                            pass
                    else:
                        if _payment_information['requestId'] and self.get_transaction(_payment_information['requestId']):
                            _payment = _payment_information
                            _transaction = self.get_transaction(_payment_information['requestId'])
                            _transaction.sudo().update({"state": "error", "state_message": _payment["status"]["message"], "p2p_payment_method": ''})
                            _transaction.sudo().write({"state": "error", "state_message": _payment["status"]["message"], "p2p_payment_method": ''})
            except Exception as e:
                exc_traceback = sys.exc_info()
                _logger.warning(getattr(e, 'message', repr(e))+" ON LINE "+format(sys.exc_info()[-1].tb_lineno))

    def get_transactions_list(self, payments):
        transactions_list = str()
        for payment in payments:
            if('issuerName' in payment):
                transactions_list = str(transactions_list) + str("<div class='d-grid gap-3 mb-3'>")
                transactions_list = str(transactions_list) + str("<div class='p-2 bg-secondary border'>") + str("Referencia: ") + str(payment['internalReference']) + str("</div>")
                transactions_list = str(transactions_list) + str("<div class='p-2 bg-light border'>") + str("Metodo: ") + str(payment['paymentMethodName']) + str("</div>")
                transactions_list = str(transactions_list) + str("<div class='p-2 bg-light border'>") + str("Emisor: ") + str(payment['issuerName']) + str("</div>")
                transactions_list = str(transactions_list) + str("<div class='p-2 bg-light border'>") + str("Estado: ") + str(payment['status']['message']) + str("</div>")
                transactions_list = str(transactions_list) + str("</div>")
        return transactions_list

    def get_transaction(self, request_id=None):
        _transaction = None
        if(request_id):
            query = "select * from payment_transaction where p2p_request_id = '" + str(request_id) + "' limit 1"        
        self.env.cr.execute(query)
        transaction = self.env.cr.dictfetchone()
        if("id" in transaction):
            _transaction = self.sudo().browse(transaction["id"])
        return _transaction
    
    def action_send_notification(self, _id, _record_name, _transaction, message=None):
        _logger.warning([('res_id', '=', _id), ('body', 'ilike', str(_transaction.p2p_request_id))])
        _mail_messages = self.env['mail.message'].sudo().search([('res_id', '=', _id), ('body', 'ilike', str(_transaction.p2p_request_id))])
        _logger.warning('_mail_messages')
        _logger.warning(_mail_messages)
        if(_mail_messages):
            for _mail_message in _mail_messages:
                mail_message = self.env['mail.message'].sudo().browse(int(_mail_message.id))
                _logger.warning(mail_message.body)
                if(message):
                    mail_message.sudo().update({'body': str(mail_message.body) + str("<br>") + str(message)})
        else:
            mail_message_values = {
                                        'email_from': self.env.user.partner_id.email,
                                        'author_id': self.env.user.partner_id.id,
                                        'model': 'sale.order',
                                        'message_type': 'comment',
                                        'body': str("Placetopay") + str("<br>") + str("Transacción: ") + str(_transaction.reference) + str("<br> <span style='display:none;'>") + str("Petición Nº: ") + str(_transaction.p2p_request_id) + str("<br></span>") + str("Referencia Nº: ") + str(_transaction.p2p_reference) + str("<br>")+ str(message),
                                        'res_id': _id,
                                        'subtype_id': self.env.ref('mail.mt_comment').id,
                                        'record_name': _record_name,
                                    }
            self.env['mail.message'].sudo().create(mail_message_values)
    
    def cron(self):
        _p2p = Place2Pay()
        _acquirer = self.get_this_acquirer()
        _transactions = self.search([("state", "in", ["draft", "pending"]), ("p2p_request_id", "!=", False)])
        if(_transactions):
            for _transaction in _transactions:
                _p2p.set_webservice_call(str(_transaction['p2p_request_id']), _acquirer["state"])
                payload = _p2p.get_payment_request_information({"login":_acquirer["place2pay_login"], "secretkey":_acquirer["secretkey"]})
                _payment_information = _p2p.send_request(payload, _acquirer["state"])
                _logger.warning(_payment_information)
                order_id = self.get_order_id(_transaction.id)
                _logger.warning("ORDERID"+str(order_id))
                if(order_id):
                    self.unlink_non_p2p_payments_transactions(order_id)
                    self._process_payment(_payment_information, order_id)

    def get_this_acquirer(self):        
        query = "select name, website_id,company_id, state, place2pay_login, secretkey from payment_provider where code = 'place2pay' limit 1"
        self.env.cr.execute(query)
        acquirer = self.env.cr.dictfetchone()
        return acquirer
    
    def get_order_id(self, transaction_id):
        query = "select * from sale_order_transaction_rel where transaction_id = '" + str(transaction_id) + "'"
        self.env.cr.execute(query)
        transactions_rel = self.env.cr.dictfetchone()
        if("sale_order_id" in transactions_rel):
            return transactions_rel["sale_order_id"]
        return None

    def get_order_transactions(self, order_id):
        query = "select * from sale_order_transaction_rel where sale_order_id = '" + str(order_id) + "'"
        self.env.cr.execute(query)
        transactions_rel = self.env.cr.dictfetchall()
        return transactions_rel