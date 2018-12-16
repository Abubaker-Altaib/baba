# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
from openerp.tools.amount_to_text_en import amount_to_text
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar
import openerp.netsvc as netsvc
from openerp.osv import osv,fields
from tools.translate import _

class report_cash_payment(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_cash_payment, self).__init__(cr, uid, name, context)
        self.context = context
        self.localcontext.update({
            'get_title': self.get_title,
            'get_tax': self.get_tax,
            'get_lines':self.get_lines,
            'get_move_lines':self.get_move_lines,
            'get_on_account':self.get_on_account,
            'convert':self.convert,
        })
        self.context = context
    def set_context(self, objects, data, ids, report_type=None):
        for obj in self.pool.get('account.voucher').browse(self.cr, self.uid, ids, self.context):
            if obj.state != 'posted':
		            raise osv.except_osv(_('Error!'), _('You can not print this voucher, Please validated it First')) 
            if obj.journal_id.type not in ['purchase','purchase_refund']:
		        raise osv.except_osv(_('Error!'), _('You can not print this report from this form, Please choose another report')) 
        return super(report_cash_payment, self).set_context(objects, data, ids, report_type=report_type) 
 
    def convert(self, amount, currency_id):
        amount_in_word = ''
        currency_format =  self.pool.get('res.users').browse(self.cr, self.uid, self.uid).company_id.currency_format 
        if currency_format=='ar':
            if currency_id:
			    currency = self.pool.get('res.currency').read(self.cr, self.uid, currency_id, ['units_name','cents_name'], context=self.context)
			    amount_in_word = amount_to_text_ar(amount, currency_format, currency['units_name'], currency['cents_name'])
            else:
			    amount_in_word = amount_to_text_ar(amount, currency_format)
        else: 
            amount_in_word = amount_to_text(amount)
        return amount_in_word

    def get_tax(self, voucher):
        result = []
        taxes = voucher.tax_id and (isinstance(voucher.tax_id,list)and voucher.tax_id or [voucher.tax_id]) or []
        for taxess in taxes:
            res = {}
            res['tax'] = taxess.name
            res['tax_last'] = 0
            for line in voucher.line_ids:
                tax_amount =self.pool.get('account.tax').compute_all(self.cr, self.uid, [taxess], line.amount, 1)['taxes'][0]['amount']
                res['tax_last'] += tax_amount
            result.append(res)  
        return result 
                    
    def get_lines(self, voucher):

        result = []
        if voucher.type in ('payment','receipt'):
            
            type = voucher.line_ids and voucher.line_ids[0].type or False
            for move in voucher.line_ids:
                    res = {'pname': move.partner_id.name, 'ref': 'Agst Ref'+" "+str(move.name),
                           'aname': move.account_id.name,'name': move.name,'account_id': move.account_id, 'amount':                         move.amount,'account_analytic_id':move.account_analytic_id,'partner_id':move.res_partner_id}
                    result.append(res)
        else:
            type = voucher.line_ids and voucher.line_ids[0].type or False
            '''for move in voucher.line_ids:
                    res = {'ref':  move.name, 'name': move.name, 'account_id': move.account_id.name, 'amount': move.amount,'account_analytic_id':move.account_analytic_id.name,'partner_id':move.res_partner_id.name,'permission':move.permission}
                    result.append(res)'''

            self.cr.execute("""select coalesce(p.name || ']' || p.code || '[',p.name) as partner_name, p.code as partner_code, sum(l.amount) as amount, min(l.permission) as permission, min(l.name) as name, bool_and(l.custody) as custody
                               from account_voucher_line l
                               left join account_voucher v on (v.id=l.voucher_id)
                               left join res_partner p on (p.id=l.res_partner_id)
                          where  l.voucher_id=%s group by l.res_partner_id,l.seq,p.name,p.code 
                          order by min(l.id)"""%(voucher.id,)) 
            res = self.cr.dictfetchall()
        return res

    def get_move_lines(self, voucher):
        move_id=voucher.move_id.id
        res=[]
        if voucher.type=='purchase' and move_id:

          self.cr.execute("""select acc.code as code,acc.name as acc_name,l.debit as debit , l.credit as credit,ana.name as ana_name ,
                               l.name as name from account_move_line l
                               left join account_account acc on (acc.id=l.account_id)
                               left join account_analytic_account ana on (ana.id=l.analytic_account_id)
                          where  l.move_id=%s """%(move_id,)) 
          res = self.cr.dictfetchall()
        return res

    def get_title(self, voucher):
       
        #  Purchase Options      
        result = []
        if (voucher.type == 'purchase' and voucher.pay_now == 'pay_now' and voucher.pay_journal_id.type == 'cash') or (voucher.type == 'payment' and voucher.pay_journal_id.type == 'cash'):
            result = 'سند دفع نقدا'  

        elif (voucher.type == 'purchase' and voucher.pay_now == 'pay_now' and voucher.pay_journal_id.type == 'bank') or (voucher.type == 'payment' and voucher.pay_journal_id.type == 'bank'):
            result = 'سند دفع شيك'  

        elif (voucher.type == 'purchase' and voucher.pay_now != 'pay_now' ) :
            result = 'اشعار خصم'  
        #  Sale Options 

        elif (voucher.type == 'sale' and voucher.pay_now == 'pay_now' ) or (voucher.type == 'receipt'):
            result = 'سند قبض'
        elif (voucher.type == 'sale' and voucher.pay_now != 'pay_now' ):
            result = 'اشعار اضافة' 
               
       
        return result 

    def get_on_account(self, voucher):
        return (voucher.type == 'receipt' and "Received cash from "+str(voucher.partner_id.name)) or \
               (voucher.type == 'payment' and "Payment from "+str(voucher.partner_id.name)) or \
               (voucher.type == 'sale' and "Sale to "+str(voucher.partner_id.name)) or \
               (voucher.type == 'purchase' and "Purchase from "+str(voucher.partner_id.name)) or ""

report_sxw.report_sxw('report.cash.payment', 'account.voucher', 'addons/account_arabic_reports/report/account_crsedit_note.rml', parser=report_cash_payment,header='external' )




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
