# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import itertools
from operator import itemgetter
from datetime import datetime
from calendar import monthrange
from openerp.tools.translate import _
from account_custom.common_report_header import common_report_header
from openerp.osv import osv, orm
import time
import pooler
from report.interface import report_rml, toxml
from report import report_sxw
from openerp.tools import ustr
from account_budget_custom.report import account_report_budget
import copy


class account_budget_quarter(report_rml, common_report_header):

    def _sort_filter(self, cr, uid, ids, context={}):
        res = []
        cr.execute('SELECT distinct account_id,sequence,acc.code \
                    FROM account_budget_classification_rel \
                         INNER JOIN account_budget_classification ON classification_id = id \
                         INNER JOIN account_budget_lines ON general_account_id = account_id \
                         INNER JOIN account_account acc ON acc.id = account_id \
                    WHERE account_id in %s \
                    ORDER BY sequence,acc.code', (tuple(ids),))
        return [acct[0] for acct in cr.fetchall()]

    def create_xml(self, cr, uid, ids, datas, context=None):
        self.pool = pooler.get_pool(cr.dbname)
        period_obj = self.pool.get('account.period')
        fiscal_year_obj = self.pool.get('account.fiscalyear')
        user_obj = self.pool.get('res.users')
        datas.get('form', {}).update({"fiscalyear_id": datas.get('form', {}).get('first_fiscalyear')})
        fiscalyear = datas.get('form', {}).get('first_fiscalyear')  
        period_from = datas.get('form', {}).get('period_from', False) and [datas.get('form', {}).get('period_from', False)] or period_obj.search(cr, uid, [('fiscalyear_id', '=', fiscalyear)], context=context, order='date_start', limit=1)
        period_start_date = period_obj.browse(cr, uid, period_from[0], context=context).date_start
        period_to = datas.get('form', {}).get('period_to', False) and [datas.get('form', {}).get('period_to', False)] or period_obj.search(cr, uid, [('fiscalyear_id', '=', fiscalyear)], context=context, order='date_start desc', limit=1)
        period_end_date = period_obj.browse(cr, uid, period_to[0], context=context).date_stop
        year = fiscal_year_obj.browse(cr, uid, fiscalyear, context=context).name 
        title = (u' تقرير الموازنة الربعي للعام‬ %s' % (year))
        period_from = period_from and period_obj.browse(cr, uid, period_from[0], context=context).name or ""
        period_to = period_to and period_obj.browse(cr, uid, period_to[0], context=context).name or ""
        self.accuracy = datas.get('form', {}).get('accuracy', 1)
        self.landscape = datas.get('form',{}).get('landscape',True)
        self.size = datas.get('form',{}).get('size','A4')
        self.columns = self.size == 'A4' and 1 or 2
        self.columns = self.landscape and self.columns or self.columns*0.66 
        self.size += (self.landscape and '_landscape' or '_portrait')
        self.rml_obj = report_sxw.rml_parse(cr, uid, "", context=context)
        self.type =  datas.get('form', {}).get('report_name')
        self.type_selection =  datas.get('form', {}).get('type_selection')
        usr_company = user_obj.browse(cr, uid, uid, context=context).company_id
        header_xml = '''
        <header>
        <date>%s</date>
        <company>%s</company>
        <accuracy>%s</accuracy>
        ''' % (str(self.rml_obj.formatLang(time.strftime("%Y-%m-%d"), date=True)) + ' ' + str(time.strftime("%H:%M")),
               usr_company.name, str(self.accuracy) + ' ' + (usr_company.currency_id.units_name or ' '))
        account_chart = datas.get('form', {}).get('chart_account_id', [])
        account_child_ids = self._get_children_and_consol(cr, uid, account_chart,
                                                          'account.account', context)
        general_account = self._sort_filter(cr, uid, account_child_ids, context=context)
        classification_ids = datas.get('form', {}).get('classification_ids', False)
        xml = ''
        xml += self.compare_budget(cr, uid, ids, datas, header_xml + '<title>%s</title></header>' % (title), context=context)
        return xml

    def compare_budget(self, cr, uid, ids, datas, header_xml, context=None):
        account_obj = self.pool.get('account.account')
        period_pool = self.pool.get('account.period')
        budget_pool = self.pool.get('account.budget')
        budget_line_pool = self.pool.get('account.budget.lines')
        classification_obj = self.pool.get('account.budget.classification')
        move_line_pool = self.pool.get('account.move.line')
        fiscal_year_obj = self.pool.get('account.fiscalyear')
        account_chart = datas.get('form', {}).get('chart_account_id', [])
        analytic_chart = datas.get('form', {}).get('chart_analytic_account_id', [])
        classification_ids = datas.get('form', {}).get('classification_ids', False)
        fiscalyear_id = datas.get('form', {}).get('first_fiscalyear', False)
        select_quarter = datas.get('form', {}).get('quarter', False)
        current_periods = period_pool.search(cr, uid, [('fiscalyear_id', '=', fiscalyear_id)],context=context)
        analytic_child_ids = self._get_children_and_consol(cr, uid, analytic_chart,
                                                         'account.analytic.account', context)
        account_child_ids = self._get_children_and_consol(cr, uid, account_chart,
                                                          'account.account', context)
        general_account = self._sort_filter(cr, uid, account_child_ids, context=context)
        dept_xml = '''<datas>'''
        dept_xml += ''' <header name="%s" split="False"/> ''' % (ustr(toxml('المتبقي')))
        dept_xml += ''' <header name="%s" split="False"/> ''' % (ustr(toxml('الإجمالي')))
        vals = ''
        xml = ''

        date_start_quar = ''
        date_endss_quar = ''

        date_start_quar1 = ''
        date_endss_quar1 = ''

        date_start_quar2 = ''
        date_endss_quar2 = ''

        date_start_quar3 = ''
        date_endss_quar3 = ''
        diff = 0
        length = 1
        year = fiscal_year_obj.browse(cr, uid, fiscalyear_id, context=context).name
        flag = True
        if select_quarter == 'first':
            february = monthrange(int(year),2)[1]
            date_start_quar1 = str(year) + "-" + '1' + "-"+"1" 
            date_endss_quar1 = str(year) + "-" + '1' + "-" +"31"
            
            date_start_quar2 = str(year) + "-" + '2' + "-"+"1" 
            date_endss_quar2 = str(year) + "-" + '2' + "-" + str(february)

            date_start_quar3 = str(year) + "-" + '3' + "-"+"1" 
            date_endss_quar3 = str(year) + "-" + '3' + "-" +"31"

            dept_xml += ''' <header name="%s"/> ''' % (ustr(toxml('مارس')))
            dept_xml += ''' <header name="%s"/> ''' % (ustr(toxml('فبراير')))
            dept_xml += ''' <header name="%s"/> ''' % (ustr(toxml('يناير')))
            flag = False
            length += 3
        if select_quarter == 'second':
            month_strats = 1
            month_end = 3
            date_start_quar = str(year) + "-" + str(month_strats) + "-"+"1" 
            date_endss_quar = str(year) + "-" + str(month_end) + "-" +"31"

            date_start_quar1 = str(year) + "-" + '4' + "-"+"1" 
            date_endss_quar1 = str(year) + "-" + '4' + "-" +"30"
            
            date_start_quar2 = str(year) + "-" + '5' + "-"+"1" 
            date_endss_quar2 = str(year) + "-" + '5' + "-" +"31"

            date_start_quar3 = str(year) + "-" + '6' + "-"+"1" 
            date_endss_quar3 = str(year) + "-" + '6' + "-" +"30"

            dept_xml += ''' <header name="%s"/> ''' % (ustr(toxml('يونيو')))
            dept_xml += ''' <header name="%s"/> ''' % (ustr(toxml('مايو')))
            dept_xml += ''' <header name="%s"/> ''' % (ustr(toxml('أبريل')))
            dept_xml += ''' <header name="%s"/> ''' % (ustr(toxml('الربع الأول')))
            
            length += 4
        if select_quarter == 'third':
            month_strats = 1
            month_end = 6
            date_start_quar = str(year) + "-" + str(month_strats) + "-"+"1" 
            date_endss_quar = str(year) + "-" + str(month_end) + "-" +"30"

            date_start_quar1 = str(year) + "-" + '7' + "-"+"1" 
            date_endss_quar1 = str(year) + "-" + '7' + "-" +"31"
            
            date_start_quar2 = str(year) + "-" + '8' + "-"+"1" 
            date_endss_quar2 = str(year) + "-" + '8' + "-" +"31"

            date_start_quar3 = str(year) + "-" + '9' + "-"+"1" 
            date_endss_quar3 = str(year) + "-" + '9' + "-" +"30"

            dept_xml += ''' <header name="%s"/> ''' % (ustr(toxml('سبتمبر')))
            dept_xml += ''' <header name="%s"/> ''' % (ustr(toxml('أغسطس')))
            dept_xml += ''' <header name="%s"/> ''' % (ustr(toxml('يوليو')))
            dept_xml += ''' <header name="%s"/> ''' % (ustr(toxml('الربع الثاني')))
                        
            length += 4
        if select_quarter == 'fourth':
            month_strats = 1
            month_end = 9
            date_start_quar = str(year) + "-" + str(month_strats) + "-"+"1" 
            date_endss_quar = str(year) + "-" + str(month_end) + "-" +"30"
            
            date_start_quar1 = str(year) + "-" + '10' + "-"+"1" 
            date_endss_quar1 = str(year) + "-" + '10' + "-" +"31"
            
            date_start_quar2 = str(year) + "-" + '11' + "-"+"1" 
            date_endss_quar2 = str(year) + "-" + '11' + "-" +"30"

            date_start_quar3 = str(year) + "-" + '12' + "-"+"1" 
            date_endss_quar3 = str(year) + "-" + '12' + "-" +"31"

            dept_xml += ''' <header name="%s"/> ''' % (ustr(toxml('ديسمبر')))
            dept_xml += ''' <header name="%s"/> ''' % (ustr(toxml('نوفمبر')))
            dept_xml += ''' <header name="%s"/> ''' % (ustr(toxml('أكتوبر')))
            dept_xml += ''' <header name="%s"/> ''' % (ustr(toxml('الربع الثالث')))
            
            length += 4
        dept_xml += ''' <header name="%s" split="False"/> ''' % (ustr(toxml("الإعتماد")))
        dept_xml += ''' <header name="%s" split="False"/> ''' % (ustr(toxml('البند')))
        dept_xml += ''' <header name="%s" split="False"/> ''' % (ustr(toxml('الرمز')))
        dept_xml += '''</datas>'''
        col = ((str((80*length) / length) + ',') * int(length-1))
        dept_xml += '''<cols>80,80,%s80,100,80</cols>''' % (str(col))
        result = []
        total = 0
        total_final = 0
        total_quarter = 0
        total_quarter1 = 0
        total_quarter2 = 0
        total_quarter3 = 0
        total_of_total_final = 0
        total_residual_final = 0
        content = ''
        for classification in classification_obj.browse(cr, uid, classification_ids, context=context):
            class_name = (u' %s' % (classification.name))
            account_total = 0
            account_balance = 0
            account_balance1 = 0
            account_balance2 = 0
            account_balance3 = 0
            total_of_total = 0
            total_residual = 0
            if self.type_selection == 'detail':
                content += ''' <row item="False"> '''
                for i in range(1,5+length):
                    if i == length+3:
                        content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml(class_name)))
                    elif i == length+4:
                        content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml(classification.code)))
                    else:
                        content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml(" ")))            
                content += ''' </row> '''
            #For order account by code
            account_ids = [account.id for account in classification.account_ids]
            account_ids  = account_obj.search(cr, uid, [('id','in', account_ids)], order = 'code')
            aggregate_budget = []
            for account in account_obj.browse(cr, uid, account_ids, context):
            #for account in classification.account_ids:
                total_class = 0
                residual = 0
                balance = 0
                balance1 = 0
                balance2 = 0
                balance3 = 0
                current_quarter_lines = budget_line_pool.search(cr, uid, [('period_id', 'in', current_periods),
                                ('analytic_account_id', 'in', analytic_child_ids),
                                ('general_account_id', '=', account.id)])
                if current_quarter_lines:
                    quarter_amount = 0
                    for line in budget_line_pool.browse(cr, uid, current_quarter_lines, context=context):
                        bl = 0
                        bl1 = 0
                        bl2 = 0
                        bl3 = 0
                        planed = line.planned_amount
                        sign = line.general_account_id.user_type.report_type in ('income','liability') and -1 or 1
                        if flag:
                            move = move_line_pool.search(cr, uid, [('analytic_account_id', 'in', analytic_child_ids),('date','>=',date_start_quar),('date','<=',date_endss_quar),('account_id', '=', line.general_account_id.id),('state','=','valid')], context=context)
                            for moves in move_line_pool.browse(cr, uid, move, context=context):
                                bl += moves.debit - moves.credit
                            balance = sign * bl
                        
                        move1 = move_line_pool.search(cr, uid, [('analytic_account_id', 'in', analytic_child_ids),('date','>=',date_start_quar1),('date','<=',date_endss_quar1),('account_id', '=', line.general_account_id.id),('state','=','valid')], context=context)
                        move2 = move_line_pool.search(cr, uid, [('analytic_account_id', 'in', analytic_child_ids),('date','>=',date_start_quar2),('date','<=',date_endss_quar2),('account_id', '=', line.general_account_id.id),('state','=','valid')], context=context)
                        move3 = move_line_pool.search(cr, uid, [('analytic_account_id', 'in', analytic_child_ids),('date','>=',date_start_quar3),('date','<=',date_endss_quar3),('account_id', '=', line.general_account_id.id),('state','=','valid')], context=context)
                        for moves1 in move_line_pool.browse(cr, uid, move1, context=context):
                            bl1 += moves1.debit - moves1.credit

                        for moves2 in move_line_pool.browse(cr, uid, move2, context=context):
                            bl2 += moves2.debit - moves2.credit

                        for moves3 in move_line_pool.browse(cr, uid, move3, context=context):
                            bl3 += moves3.debit - moves3.credit
                    
                        balance1 = sign * bl1
                        balance2 = sign * bl2
                        balance3 = sign * bl3
                        total_class += round(planed,2)
                total = balance + balance1 + balance2 + balance3
                residual = total_class - total
                if self.type_selection == 'detail':
                    content += ''' <row item="False"> '''
                    content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('detail',ustr(toxml('{:,.2f}'.format(residual))))
                    content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('detail',ustr(toxml('{:,.2f}'.format(total))))
                    content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('detail',ustr(toxml('{:,.2f}'.format(balance3))))
                    content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('detail',ustr(toxml('{:,.2f}'.format(balance2))))
                    content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('detail',ustr(toxml('{:,.2f}'.format(balance1))))
                    if flag:
                        content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('detail',ustr(toxml('{:,.2f}'.format(balance))))
                    content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('detail',ustr(toxml('{:,.2f}'.format(total_class))))
                    content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('detail',ustr(toxml(account.name)))
                    content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('detail',ustr(toxml(account.code)))
                    content += ''' </row> '''
                else:
                    aggregate_budget.append({ 'parent_code': account.parent_id.code,
                                              'parent_name':account.parent_id.name,
                                              'total_class':total_class,
                                              'balance':balance,
                                              'balance1':balance1,
                                              'balance2':balance2,
                                              'balance3':balance3,
                                              'total':total,
                                              'residual':residual,
                                            })
                #Total Classification
                account_total += total_class
                account_balance += balance
                account_balance1 += balance1
                account_balance2 += balance2
                account_balance3 += balance3
                total_of_total += total
                total_residual +=residual
            if self.type_selection == 'total':
                aggregate_budget.sort(key=itemgetter("parent_code"))
                aggregate_budget_temp =[]
                aggregate_budget_final =[]
                for key, group in itertools.groupby(aggregate_budget, lambda item: item["parent_code"]):
                    aggregate_budget_temp.append([item for item in group])
                for record in aggregate_budget_temp:
                    aggregate_budget_final.append({'parent_name':record[0]['parent_name'],
                        'parent_code':   record[0]['parent_code'],
                        'total_class':  sum([item["total_class"] for item in record]),
                        'balance':      sum([item["balance"] for item in record]),
                        'balance1':     sum([item["balance1"] for item in record]),
                        'balance2':     sum([item["balance2"] for item in record]),
                        'balance3':     sum([item["balance3"] for item in record]),
                        'total':        sum([item["total"] for item in record]),
                        'residual':     sum([item["residual"] for item in record]),})

                for record in aggregate_budget_final:
                    content += ''' <row item="False"> '''
                    content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('detail',ustr(toxml('{:,.2f}'.format(record['residual']))))
                    content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('detail',ustr(toxml('{:,.2f}'.format(record['total']))))
                    content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('detail',ustr(toxml('{:,.2f}'.format(record['balance3']))))
                    content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('detail',ustr(toxml('{:,.2f}'.format(record['balance2']))))
                    content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('detail',ustr(toxml('{:,.2f}'.format(record['balance1']))))
                    if flag:
                        content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('detail',ustr(toxml('{:,.2f}'.format(record['balance']))))
                    content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('detail',ustr(toxml('{:,.2f}'.format(record['total_class']))))
                    content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('detail',ustr(toxml(record['parent_name'])))
                    content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('detail',ustr(toxml(record['parent_code'])))
                    content += ''' </row> '''    

            #Totals Final
            total_final += account_total
            total_quarter += account_balance
            total_quarter1 += account_balance1
            total_quarter2 += account_balance2
            total_quarter3 += account_balance3
            total_of_total_final += total_of_total
            total_residual_final += total_residual
            extra = ' '
            tempural = "إجمالي " + extra 
            classes = u'' + tempural.decode('utf-8') + u'' + classification.name
            content += ''' <row> '''
            content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml('{:,.2f}'.format(total_residual))))
            content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml('{:,.2f}'.format(total_of_total))))
            content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml('{:,.2f}'.format(account_balance3))))
            content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml('{:,.2f}'.format(account_balance2))))
            content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml('{:,.2f}'.format(account_balance1))))
            if flag:
                content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml('{:,.2f}'.format(account_balance))))
            content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml('{:,.2f}'.format(account_total))))
            content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ("total",ustr(toxml(classes)))
            content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ("total",ustr(toxml('')))
            content += ''' </row> '''
        extra = 'الكلي'
        tempural = "الإجمالي " + extra 
        classes_totals = u'' + tempural.decode('utf-8') + u''
        content += ''' <row> '''
        content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml('{:,.2f}'.format(total_residual_final))))
        content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml('{:,.2f}'.format(total_of_total_final))))
        content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml('{:,.2f}'.format(total_quarter3))))
        content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml('{:,.2f}'.format(total_quarter2))))
        content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml('{:,.2f}'.format(total_quarter1))))
        if flag:
            content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml('{:,.2f}'.format(total_quarter))))
        content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml('{:,.2f}'.format(total_final))))
        content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ("total",ustr(toxml(classes_totals)))
        content += ''' <cols type="%s"> <val> %s </val></cols> ''' % ("total",ustr(toxml('')))
        content += ''' </row> '''

        xml += '''<?xml version="1.0" encoding="UTF-8" ?>
        <report><page size='%s' type='%s'>
        %s
        %s
        %s
        </page></report>
        ''' % (self.size, self.type, header_xml, dept_xml, content)
        return xml


account_budget_quarter('report.account.account.budget.quarter', "account.report.budget.quarter", '', 'addons/account_budget_custom/report/account_report_budget_quarter.xsl')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
