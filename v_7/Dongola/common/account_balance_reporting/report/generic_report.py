# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw
from account_custom.common_report_header import common_report_header
from account_arabic_reports.report import account_balance as account_balance_report
from datetime import datetime, timedelta


class account_generic_report(report_sxw.rml_parse, common_report_header):
    
    def __init__(self, cr, uid, name, context=None):
        super(account_generic_report, self).__init__(cr, uid, name, context=context)
        self.context = context


        arabic_date_to = ''
        # By Mudathir : convert English Date To Arabic(Hindi Date)
        if context.get('active_id'):
            date_to_b_conv = self.pool.get('account.balance.reporting').read(cr, uid, context['active_ids'],['date_to'], context)
            eastern_to_western = {"-":"-","0": "۰", "1": "١", "2": "٢", "3": "٣", "4": "٤", "5": "٥", "6": "٦", "7": "٧",
                                  "8": "٨", "9": "٩"}
            date = datetime.strptime(date_to_b_conv[0]['date_to'], '%Y-%m-%d').strftime('%d-%m-%Y')
            for w in date:
                arabic_date_to += ''.join([eastern_to_western[w] ])



        self.localcontext.update({
            'temp_lines_with_detail': self._get_temp_lines_with_detail,
            'lines': self._detail_lines,
            'get_multi_company': self._get_multi_company,
            'get_total': self._get_total,
            'sign_round': self._get_sign_round,
            'arabic_date_to':arabic_date_to
        })

    def _detail_lines(self,accounts, report):
        fiscalyear = report.current_fiscalyear_id
#        period_from = report.period_from
#        period_to = report.period_to
        chart = report.chart_account_id.id
        account_ids = self.pool.get('account.account').search(self.cr, self.uid, [('id','in',accounts),
                        ('company_id','=',report.company_id.id)], context=self.context)
        form = {
            'initial_balance': True, 
            'chart_account_id': chart,
            'fiscalyear_id': False, 
            'filter': 'filter_date', 
            'date_from': fiscalyear.date_start.val, 
            'date_to': fiscalyear.date_stop.val,
            'period_from': False, 
            'period_to': False, 
            'periods': [],  
            'used_context': {'fiscalyear': False, 'date_from': fiscalyear.date_start.val, 'date_to': fiscalyear.date_stop.val, 'chart_account_id': chart}, 
            'display_account': report.detail == 'min' and 'bal_movement' or 'bal_all', 
            'moves': 1, 
            'target_move': str(report.target_move) , 
            'detail': report.detail,
            'all_accounts': True,
            'account_ids': account_ids}
    
        self.account_balance = account_balance_report.account_balance(self.cr, self.uid, self.name, context=self.context)
        self.account_balance.set_context(self.objects, {'model': 'ir.ui.menu', 'form':form}, accounts)
        res = self.account_balance.lines(form)
        lines = [l for l in res if round(l['balance']+l['init_balance'],2) != 0.0]
        if report.detail == 'regular':
            return [line for line in lines if line['type']!='view' and line['type']!='consolidation']
        return lines or [{'no_rows': 'لا يوجد'}]


    def _get_temp_lines_with_detail(self,report_temp):
        line_with_detail = self.pool.get('account.balance.reporting.template.line')
        line_ids = line_with_detail.search(self.cr, self.uid, [('report_id', '=', report_temp),('detail','=',True),
                                                                   ('detail_account_ids','!=',False)], context=self.context)
        return line_with_detail.read(self.cr, self.uid, line_ids, ['name','detail_account_ids'], context=self.context)

    def _get_total(self,report):
        debit = 0.0
        credit = 0.0
        count = 0
        for line in report.line_ids:
            if line.css_class == 'l3':
                count += 1
                debit += (line.current_value+line.previous_value) > 0 and (line.current_value+line.previous_value) or 0.0
                credit += (line.current_value+line.previous_value) < 0 and (line.current_value+line.previous_value) or 0.0
        return [{'debit': debit, 'credit': credit, 'counts': count}]

    def _get_sign_round(self,amount,report):
        return_amount=report.round and round(amount,2) or int(amount)
        if return_amount > 0:
            return str(return_amount)
        if return_amount == 0:
            return str(0.00)
        if report.sign=='no_sign':
            return str(abs(return_amount))
        elif report.sign=='bracket':
            return '('+str(abs(return_amount))+')' 
        else :
            return str(return_amount)
        

report_sxw.report_sxw('report.account.generic.report', 'account.balance.reporting', 'addons/account_balance_reporting/report/generic_report.rml', parser=account_generic_report, header='external')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
