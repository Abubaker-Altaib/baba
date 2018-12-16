# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
from datetime import datetime, timedelta

class account_balance_report(osv.osv_memory):
    """
    Inherit balance report wizard to add some displaying options:
        *  Assisstant Report
    """
    _inherit = "account.balance.report"

    _columns = {
        'assistant_report':fields.boolean('Assistant Report'),
        'unit_type':fields.selection([('ministry', 'ministry'), ('locality', 'locality'), ('other', 'other')], "Type"),

    }


    _defaults = {
        'assistant_report': False,
        'unit': 'assist',
        
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)

        data['form'].update(self.read(cr, uid, ids, ['assistant_report', 'moves', 'unit','unit_type','initial_balance', 'account_ids', 'acc_balances', 'landscape'])[0])
        data['form'].update(self.read(cr, uid, ids, ['assistant_report'])[0])
 

        arabic_date_to = ''
        # By Mudathir : convert English Date To Arabic(Hindi Date)
        if data['form']['date_to']:

            eastern_to_western = {"-": "-", "0": "۰", "1": "١", "2": "٢", "3": "٣", "4": "٤", "5": "٥", "6": "٦",
                                  "7": "٧",
                                  "8": "٨", "9": "٩"}
            date = datetime.strptime(data['form']['date_to'], '%Y-%m-%d').strftime('%d-%m-%Y')
            for w in date:
                arabic_date_to += ''.join([eastern_to_western[w]])

            data['form'].update({'date_to_arabic':arabic_date_to})
        arabic_date_from = ''
        if data['form']['date_from']:

            eastern_to_western = {"-": "-", "0": "۰", "1": "١", "2": "٢", "3": "٣", "4": "٤", "5": "٥", "6": "٦",
                                  "7": "٧",
                                  "8": "٨", "9": "٩"}
            date = datetime.strptime(data['form']['date_from'], '%Y-%m-%d').strftime('%d-%m-%Y')
            for w in date:
                arabic_date_from += ''.join([eastern_to_western[w]])

            data['form'].update({'date_from_arabic':arabic_date_from})
        print ">>>>>>>>>>>>>>>>>>>>>>>>>YYYYYYYYYYYYYYYYYYYYYYYAAAAAAAAAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHOOOO", data['form']['date_to']
        #return
        arabic_date_current = ''
        date_to_b_conv = str(datetime.today())[0:10]
        eastern_to_western = {"-": "-", "0": "۰", "1": "١", "2": "٢", "3": "٣", "4": "٤", "5": "٥", "6": "٦",
                              "7": "٧",
                              "8": "٨", "9": "٩"}
        date = datetime.strptime(date_to_b_conv, '%Y-%m-%d').strftime('%d-%m-%Y')
        for w in date:
            arabic_date_current += ''.join([eastern_to_western[w]])
        data['form'].update({'arabic_date_current': arabic_date_current})

        # ASSISTANT REPORT WITH FIXED TEMPALTE : DESIGED TO MEET DESIGN OF DONGLA
        if data['form']['assistant_report'] and  data['form']['unit']=='assist':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.assistant.report', 'datas': data}
        # BALANCE REPORT WITH FIXED TEMPALTE:: DESIGED TO MEET DESIGN OF DONGLA(LESS IN PERFORMANCE)
        if not data['form']['assistant_report'] and  data['form']['unit']=='balance':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.unit.balance.arabic', 'datas': data}
        # BALANCE REPORT WITH FIXED TEMPALTE:SHOW ACCOUNTS DEPENDS ON CHOOSEN FIELD IN ACCOUNT VIEW
        if not data['form']['assistant_report'] and  data['form']['unit']=='normal':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.balance.arabic', 'datas': data}
        # BALANCE REPORT WITH FIXED TEMPALTE:CAN RETURN FULL ACCOUTS WITHOUT CHOOSEN FILED IN NORMAL REPORT
        if  data['form']['assistant_report'] and  data['form']['unit']=='common':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.balance.all.arabic', 'datas': data}
        if  data['form']['unit']=='asset':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.balance.asset.arabic', 'datas': data}
        if  data['form']['unit']=='consol':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.balance.consol.arabic', 'datas': data}
        if  data['form']['unit']=='consol_sub':
            return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.balance.unit.arabic', 'datas': data}
        # DEFAULT 
        #return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.balance.all.arabic', 'datas': data}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
