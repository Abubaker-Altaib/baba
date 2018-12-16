# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from datetime import datetime
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

class account_compare_budget_custom(report_rml, common_report_header):

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
        title = datas.get('form', {}).get('report_name') == 'compare' and ((u' مقترح موازنة‬ للعام المالي %s' % (year)))
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
        usr_company = user_obj.browse(cr, uid, uid, context=context).company_id
        period_start_month = datetime.strptime(period_start_date, "%Y-%m-%d").month
        period_end_month = datetime.strptime(period_end_date, "%Y-%m-%d").month
        periods = []
        for i in range(period_start_month,period_end_month+2):
            periods += [i]
        self.periods = periods
        header_xml = '''
        <header>
        <date>%s</date>
        <accuracy>%s</accuracy>
        <period_from>%s</period_from>
        <period_to>%s</period_to>
        <period_start_date>%s</period_start_date>
        <period_end_date>%s</period_end_date>
        ''' % (str(self.rml_obj.formatLang(time.strftime("%Y-%m-%d"), date=True)) + ' ' + str(time.strftime("%H:%M")),
               str(self.accuracy) + ' ' + (usr_company.currency_id.units_name or ' '), period_from, period_to, period_start_date, period_end_date)
        account_chart = datas.get('form', {}).get('chart_account_id', [])
        account_child_ids = self._get_children_and_consol(cr, uid, account_chart,
                                                          'account.account', context)
        general_account = self._sort_filter(cr, uid, account_child_ids, context=context)
        classification_ids = datas.get('form', {}).get('classification_ids', False)
        xml = ''
        if general_account == [] or classification_ids == []:
            xml += self.generate_empty(cr, uid, ids, datas, header_xml + '<title>%s</title></header>' % (title), context=context)
        else:
            xml += self.compare_budget(cr, uid, ids, datas, header_xml + '<title>%s</title></header>' % (title), context=context)
        return xml

    def create_xml_cols(self, cr, uid, ids, col_value, flag, planed_amount, context=None):
        content = ''
        col_type = 'total'
        vals = ''
        extra = flag == 1 and 'للصنف ' or 'الكلي'
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        result = 0.0
        temp = 0.0
        for year in fiscalyear_obj.browse(cr, uid, col_value['fiscalyear_ids'], context=context):
            temp += planed_amount['next_planned_amount'][year.name]
        result = temp != 0.0 and (planed_amount['planned_amount']-temp)*100/temp
        
        vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % (col_type,self.rml_obj.formatLang(result))
        vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % (col_type,self.rml_obj.formatLang(result))
        vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % (col_type,self.rml_obj.formatLang(planed_amount['planned_amount']))
        if  col_value['num_year'] != 0:
            for year in fiscalyear_obj.browse(cr, uid, col_value['fiscalyear_ids'], context=context):
                temp = planed_amount['next_planned_amount'][year.name]
                result = 0.0
                result = temp != 0.0 and (planed_amount['balance']/planed_amount['next_planned_amount'][year.name])*100

                vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % (col_type,self.rml_obj.formatLang(result))
                vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % (col_type,self.rml_obj.formatLang(planed_amount['balance']))
                vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % (col_type,self.rml_obj.formatLang(planed_amount['next_planned_amount'][year.name]))
        if flag == 1:
            tempural = "الإجمالي " + extra 
            class_name = u'' + tempural.decode('utf-8') + u'' + col_value['name']
            vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % (col_type,ustr(toxml(class_name)))
        else:
            vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % (col_type,ustr(toxml('الإجمالي')))
        content += vals 
        return content

    def generate_empty(self, cr, uid, ids, datas, header_xml, context=None):
        num_year = datas.get('form', {}).get('num_year', False)
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalyear_id = datas.get('form', {}).get('first_fiscalyear', False)
        fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('id', '!=', fiscalyear_id),('date_stop', '<', fiscalyear_obj.browse(cr, uid, fiscalyear_id,
                                                          context=context).date_start)], limit=num_year, order='date_start desc', context=context)
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        dept_xml = '''<datas>'''
        dept_xml += ''' <header name="%s" split="False"/> ''' % (ustr(toxml('التوصيات')))
        dept_xml += ''' <header name="%s" split="False"/> ''' % (ustr(toxml('نسبة التغيير')))
        dept_xml += ''' <header name="%s" split="False"/> ''' % (ustr(toxml("المصدق الحالي " + str(fiscalyear_obj.browse(cr, uid, fiscalyear_id, context=context).name))))
        fiscalyear_ids.reverse()
        if num_year != 0 and fiscalyear_ids != []:
            dept_xml += ''' <header2 name=" " split="False"/> '''
            for year in fiscalyear_obj.browse(cr, uid, fiscalyear_ids, context=context):
                dept_xml += ''' <header name="%s" split="True"/> ''' % (ustr(toxml("المقترح للعام " + str(year.name))))
                dept_xml += ''' <header2 name=" " split="True"/> '''
            dept_xml += ''' <header2 name=" " split="False"/> '''
        else:
            dept_xml += ''' <header2 name=" " split="False"/> '''
        dept_xml += ''' <header name="%s" split="False"/> ''' % (ustr(toxml('بند الخصم')))
        dept_xml += '''</datas>'''
        length = len(fiscalyear_ids)
        if length == 0: length = 1
        factor = num_year
        page_size = 0
        if self.size == 'A3_landscape':
            page_size = 1572
        else:
            page_size = 786
        if num_year == 0 or fiscalyear_ids ==[]:
            row_width = page_size / 4
            dept_xml += '''<cols>160,70,80,90</cols>'''
            dept_xml += '''<splitcols>160,70,80,90</splitcols>'''
            dept_xml += '''<extracols>400</extracols>'''
            dept_xml += '''<cols2>%s%s</cols2>''' % (((str((page_size) / (4)) + ',') * int(3)),row_width)
            dept_xml += '''<headercols>%s%s</headercols>''' % (((str((page_size) / (4)) + ',') * int(3)),row_width)
            factor = 1
        elif num_year <= length:
            row_width = page_size / (4+(num_year*3))
            dept_xml += '''<cols>160,70,80,%s90</cols>''' % ((str((3*70*num_year) / num_year) + ',') * int(num_year))
            dept_xml += '''<splitcols>160,70,80,%s90</splitcols>''' % ((str((3*70*num_year) / (num_year*3)) + ',') * int(num_year*3))
            dept_xml += '''<extracols>310,%s90</extracols>''' % ((str((3*70*num_year) / (num_year*3)) + ',') * int(num_year*3))
            dept_xml += '''<cols2>%s%s%s</cols2>''' % (((str(round(((page_size) / (4+(num_year*3))),2)) + ',') * int(3)),((str(round(((page_size) / (4+(num_year*3)))*(3))) + ',') * int(num_year)),row_width)
            dept_xml += '''<headercols>%s,%s%s</headercols>''' % ((row_width*3),((str(round((page_size) / (4+(num_year*3)))) + ',') * int(num_year*3)),row_width)
        else :
            row_width = page_size / (4+(length*3))
            dept_xml += '''<cols>160,70,80,%s90</cols>''' % ((str((3*70*length) / length) + ',') * int(length))
            dept_xml += '''<splitcols>160,70,80,%s90</splitcols>''' % ((str((3*70*length) / (length*3)) + ',') * int(length*3))
            dept_xml += '''<extracols>310,%s90</extracols>''' % ((str((3*70*length) / (length*3)) + ',') * int(length*3))
            dept_xml += '''<cols2>%s%s%s</cols2>''' % (((str(round(((page_size) / (4+(length*3))),2)) + ',') * int(3)),((str(round(((page_size) / (4+(length*3)))*(3))) + ',') * int(length)),row_width)
            dept_xml += '''<headercols>%s,%s%s</headercols>''' % ((row_width*3),((str(round((page_size) / (4+(length*3)))) + ',') * int(length*3)),row_width)
            factor = length

        content = ''' <row name="%s" count="1" class="True" item="True"> ''' % (ustr(toxml("صنف")))
        if num_year == 0 or fiscalyear_ids ==[]:
            for i in range(1,5):
                if i == 1: content += ''' <cols note="True" type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml(" ")))
                else: content += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml(" ")))
        else:
            for i in range(1,(factor*3)+5):
                if i == 1: content += ''' <cols note="True" type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml(" ")))
                else: content += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml(" ")))
        content += '''  <val>  </val></row> '''
        extra = False
        if num_year != 0: extra = True
        xml = '''<?xml version="1.0" encoding="UTF-8" ?>
        <report><page size='%s' type='%s' extra='%s'>
        %s
        %s
        %s
        </page></report>
        ''' % (self.size, self.type, extra, header_xml, dept_xml, content)
        return xml

    def compare_budget(self, cr, uid, ids, datas, header_xml, context=None):
        period_pool = self.pool.get('account.period')
        account_pool = self.pool.get('account.account')
        budget_line_pool = self.pool.get('account.budget.lines')
        fisc_budget_line_pool = self.pool.get('account.fiscalyear.budget.lines')
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        classification_obj = self.pool.get('account.budget.classification')
        account_chart = datas.get('form', {}).get('chart_account_id', [])
        analytic_chart = datas.get('form', {}).get('chart_analytic_account_id', [])
        period_from = datas.get('form', {}).get('period_from', False)
        period_to = datas.get('form', {}).get('period_to', False)
        classification_ids = datas.get('form', {}).get('classification_ids', False)
        num_year = datas.get('form', {}).get('num_year', False)
        fiscalyear_id = datas.get('form', {}).get('first_fiscalyear', False)
        fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('id', '!=', fiscalyear_id),('date_stop', '<', fiscalyear_obj.browse(cr, uid, fiscalyear_id,
                                                          context=context).date_start)], limit=num_year, order='date_start desc', context=context)
        period_from_start = period_from and period_pool.browse(cr, uid, period_from,
                                                                                   context=context).date_start or ''
        period_stop = period_to and period_pool.browse(cr, uid, period_to,
                                                                              context=context).date_stop or ''
        current_periods = period_pool.search(cr, uid, [('fiscalyear_id', '=', fiscalyear_id)],
                                                                 context=context)
        analytic_child_ids = self._get_children_and_consol(cr, uid, analytic_chart,
                                                         'account.analytic.account', context)
        account_child_ids = self._get_children_and_consol(cr, uid, account_chart,
                                                          'account.account', context)
        general_account = self._sort_filter(cr, uid, account_child_ids, context=context)
        budget_class = {'id':False, 'name':'', 'class':''}
        years_planned_amount = {'planned_amount':0.0, 'next_planned_amount':{}, 'balance':0.0}
        class_planed_amount = {'planned_amount':0.0, 'next_planned_amount':{}, 'balance':0.0}
        next_fiscalyear_ids = []
        account_budget = {'code':'', 'name':'', 'planned_amount':0.0, 'next_planned_amount':{}, 'balance':0.0}
        count = 0
        flag = False
        temp = ''
        classenametemp = classification_obj.browse(cr, uid, classification_ids[0], context=context).name
        class_name = (u' الصنف %s' % (classification_obj.browse(cr, uid, classification_ids[0], context=context).name))
        content = ''' <row name="%s" count="1" class="True" item="False"> ''' % (ustr(toxml(class_name)))
        dept_xml = '''<datas>'''
        dept_xml += ''' <header name="%s" split="False"/> ''' % (ustr(toxml('التوصيات')))
        dept_xml += ''' <header name="%s" split="False"/> ''' % (ustr(toxml('نسبة التغيير')))
        note = ''
        vals = ''
        xml = ''
        if fiscalyear_ids == []:
            num_year = 0
        if classification_ids == []:
            xml += self.generate_empty(cr, uid, ids, datas, header_xml, context=context)
            return xml
        for classification in classification_obj.browse(cr, uid, classification_ids, context=context):
            for account in classification.account_ids:
                vals = ''
                if count == 0:
                    dept_xml += ''' <header name="%s" split="False"/> ''' % (ustr(toxml("المصدق الحالي " + str(fiscalyear_obj.browse(cr, uid, fiscalyear_id, context=context).name))))
                    if num_year != 0:
                        dept_xml += ''' <header2 name=" " split="False"/> '''
                for year in fiscalyear_obj.browse(cr, uid, fiscalyear_ids, context=context):
                    account_budget['next_planned_amount'][year.name] = 0.0
                    if count == 0:
                        flag = True
                        years_planned_amount['next_planned_amount'][year.name] = 0.0
                        class_planed_amount['next_planned_amount'][year.name] = 0.0
                        if num_year != 0:
                            dept_xml += ''' <header name="%s" split="True"/> ''' % (ustr(toxml("المقترح للعام " + str(year.name))))
                            dept_xml += ''' <header2 name=" " split="True"/> '''
                if count == 0:
                    dept_xml += ''' <header name="%s" split="False"/> ''' % (ustr(toxml('بند الخصم')))
                    if num_year != 0:
                        dept_xml += ''' <header2 name=" " split="False"/> '''
                    else:
                        dept_xml += ''' <header2 name=" " split="True"/> '''
                    dept_xml += '''</datas>'''
                    length = len(fiscalyear_ids)
                    if length == 0: length = 1
                    factor = num_year
                    page_size = 0
                    if self.size == 'A3_landscape':
                        page_size = 1572
                    else:
                        page_size = 786
                    if num_year == 0 or fiscalyear_ids ==[]:
                        row_width = page_size / 4
                        dept_xml += '''<cols>160,70,80,90</cols>'''
                        dept_xml += '''<splitcols>160,70,80,90</splitcols>'''
                        dept_xml += '''<extracols>400</extracols>'''
                        dept_xml += '''<cols2>%s%s</cols2>''' % (((str((page_size) / (4)) + ',') * int(3)),row_width)
                        dept_xml += '''<headercols>%s%s</headercols>''' % (((str((page_size) / (4)) + ',') * int(3)),row_width)
                        factor = 1
                    elif num_year <= length:
                        row_width = page_size / (4+(num_year*3))
                        dept_xml += '''<cols>160,70,80,%s90</cols>''' % ((str((3*70*num_year) / num_year) + ',') * int(num_year))
                        dept_xml += '''<splitcols>160,70,80,%s90</splitcols>''' % ((str((3*70*num_year) / (num_year*3)) + ',') * int(num_year*3))
                        dept_xml += '''<extracols>310,%s90</extracols>''' % ((str((3*70*num_year) / (num_year*3)) + ',') * int(num_year*3))
                        dept_xml += '''<cols2>%s%s%s</cols2>''' % (((str(round(((page_size) / (4+(num_year*3))),2)) + ',') * int(3)),((str(round(((page_size) / (4+(num_year*3)))*(3))) + ',') * int(num_year)),row_width)
                        dept_xml += '''<headercols>%s,%s%s</headercols>''' % ((row_width*3),((str(round((page_size) / (4+(num_year*3)))) + ',') * int(num_year*3)),row_width)
                    else :
                        row_width = page_size / (4+(length*3))
                        dept_xml += '''<cols>160,70,80,%s90</cols>''' % ((str((3*70*length) / length) + ',') * int(length))
                        dept_xml += '''<splitcols>160,70,80,%s90</splitcols>''' % ((str((3*70*length) / (length*3)) + ',') * int(length*3))
                        dept_xml += '''<extracols>310,%s90</extracols>''' % ((str((3*70*length) / (length*3)) + ',') * int(length*3))
                        dept_xml += '''<cols2>%s%s%s</cols2>''' % (((str(round(((page_size) / (4+(length*3))),2)) + ',') * int(3)),((str(round(((page_size) / (4+(length*3)))*(3))) + ',') * int(length)),row_width)
                        dept_xml += '''<headercols>%s,%s%s</headercols>''' % ((row_width*3),((str(round((page_size) / (4+(length*3)))) + ',') * int(length*3)),row_width)
                        factor = length
                if count > 0 and budget_class['id'] != classification.id and budget_class['id'] != False : content += ''' <row name="None" count="2" class="False" item="False"> '''
                elif count > 0 and budget_class['id'] != classification.id : content += ''' <row name="None" count="2" class="False" item="False"> '''
                elif count > 0: content += ''' <row name="None" count="2" class="False" item="True"> '''
                if budget_class['id'] != classification.id:
                    class_name = (u' الصنف %s' % (classification.name))
                    if budget_class['id'] != False:
                        temp = {'name': budget_class['name'], 'fiscalyear_ids':fiscalyear_ids, 'num_year':num_year,}
                        vals += self.create_xml_cols(cr, uid, ids, temp, 1, class_planed_amount, context=context) + '''  <val>  </val></row> '''
                        vals += '''<row name="%s" count="2" class="True" item="False"> '''  % (ustr(toxml(class_name)))
                        vals +=  ''' <val> %s </val> '''  % (ustr(toxml(note)))
                        note = ''
                        if num_year != 0:
                            for year in fiscalyear_obj.browse(cr, uid, fiscalyear_ids, context=context):
                                class_planed_amount['next_planned_amount'][year.name] = 0.0
                        class_planed_amount['planned_amount'] = 0.0
                        class_planed_amount['balance'] = 0.0
                    if num_year == 0 or fiscalyear_ids ==[]:
                        for i in range(1,5):
                            if i == 1: vals += ''' <cols note="True" type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml(" ")))
                            elif i == 4: vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml(class_name)))
                            else: vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml(" ")))
                    else:
                        for i in range(1,(factor*3)+5):
                            if i == 1: vals += ''' <cols note="True" type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml(" ")))
                            elif i == ((factor*3)+4): vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml(class_name)))
                            else: vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % ('total',ustr(toxml(" ")))
                    vals += '''  <val>  </val></row> <row name="None" count="2" class="False" item="True"> '''
                    budget_class['id'] = classification.id
                account_budget = {'code':account.code, 'name':account.name, 'planned_amount':0.0, 'next_planned_amount':{} ,'balance':0.0}
                if  num_year != 0:
                    for year in fiscalyear_obj.browse(cr, uid, fiscalyear_ids, context=context):
                        account_budget['next_planned_amount'][year.name] = 0.0
                current_lines = budget_line_pool.search(cr, uid, [('period_id', 'in', current_periods),
                                    ('analytic_account_id', 'in', analytic_child_ids),
                                    ('general_account_id', '=', account.id)], context=context)
                current_lines2 = fisc_budget_line_pool.search(cr, uid, [('fiscalyear_id', '=', fiscalyear_id),
                                        ('analytic_account_id', 'in', analytic_child_ids),
                                        ('general_account_id', '=', account.id)], context=context)
                next_lines = []
                if  num_year != 0:
                    next_lines = fisc_budget_line_pool.search(cr, uid, [('fiscalyear_id', 'in', fiscalyear_ids),
                                        ('analytic_account_id', 'in', analytic_child_ids),
                                        ('general_account_id', '=', account.id)], context=context)
                period_ids = period_pool.search(cr, uid, [('fiscalyear_id','in', fiscalyear_ids)],  context=context)
                bal_lines = budget_line_pool.search(cr, uid, [('period_id', 'in', period_ids),
                                    ('analytic_account_id', 'in', analytic_child_ids),
                                    ('general_account_id', '=', account.id)], context=context)
                if current_lines:
                    for line in budget_line_pool.browse(cr, uid, current_lines, context=context):
                        account_budget['planned_amount'] += line.planned_amount
                        class_planed_amount['planned_amount'] += line.planned_amount
                        years_planned_amount['planned_amount'] += line.planned_amount
                        flag = True
                    
                    for line in fisc_budget_line_pool.browse(cr, uid, current_lines2, context=context):
                        if line.note != False:
                            note += "\n" + line.note + " -"

                if bal_lines:
                    for line in budget_line_pool.browse(cr, uid, bal_lines, context=context):
                        account_budget['balance'] += line.balance
                        class_planed_amount['balance'] += line.balance
                        years_planned_amount['balance'] += line.balance
                temp = 0.0
                if next_lines:
                    for line in fisc_budget_line_pool.browse(cr, uid, next_lines, context=context):
                        account_budget['next_planned_amount'][line.fiscalyear_id.name] += line.planned_amount
                        class_planed_amount['next_planned_amount'][line.fiscalyear_id.name] += line.planned_amount
                        years_planned_amount['next_planned_amount'][line.fiscalyear_id.name] += line.planned_amount
                    for year in fiscalyear_obj.browse(cr, uid, fiscalyear_ids, context=context):
                        temp += account_budget['next_planned_amount'][year.name]
                    flag = True
                vals += ''' <cols note="True" type="%s"> <val> %s </val></cols> ''' % ('detail',ustr(toxml(note)))
                result = 0.0
                result = temp != 0 and (account_budget['planned_amount']-temp)*100/temp
                vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % ('detail',self.rml_obj.formatLang(result))
                result = 0.0
                if current_lines:
                    vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % ('detail',self.rml_obj.formatLang(account_budget['planned_amount']))              
                else:
                    vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % ('detail',self.rml_obj.formatLang(0.0))
                if next_lines:
                    for year in fiscalyear_obj.browse(cr, uid, fiscalyear_ids, context=context):
                        result = 0.0
                        if account_budget['next_planned_amount'][year.name] != 0.0:
                            result = (account_budget['balance']/account_budget['next_planned_amount'][year.name])*100
                        vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % ('detail',self.rml_obj.formatLang(result))
                        vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % ('detail',self.rml_obj.formatLang(account_budget['balance']))
                        vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % ('detail',self.rml_obj.formatLang(account_budget['next_planned_amount'][year.name]))
                elif num_year != 0 and num_year <= len(fiscalyear_ids):
                    for i in range(1, num_year+1):
                        for j in range(1,4):
                            vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % ('detail',self.rml_obj.formatLang(0.0))
                elif num_year != 0 and num_year > len(fiscalyear_ids):
                    for i in range(1, len(fiscalyear_ids)+1):
                        for j in range(1,4):
                            vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % ('detail',self.rml_obj.formatLang(0.0))
                vals += ''' <cols note="False" type="%s"> <val> %s </val></cols> ''' % ('detail',ustr(toxml(account.name)))
                budget_class['name'] = classification.name
                budget_class['class'] = classification.code
                count += 1
                content += vals + '''  <val>  </val></row> '''
        temp = {'name':budget_class['name'], 'fiscalyear_ids':fiscalyear_ids, 'num_year':num_year,}
        content += '''<row name="None" count="2" class="None" item="False"> ''' + self.create_xml_cols(cr, uid, ids, temp, 1, class_planed_amount, context=context)
        content += '''  <val> %s </val></row> ''' % (ustr(toxml(note)))
        temp = {'name':'', 'fiscalyear_ids':fiscalyear_ids, 'num_year':num_year,}
        content += '''<row name="None" count="2" class="False" item="False"> ''' + self.create_xml_cols(cr, uid, ids, temp, 2, years_planned_amount, context=context)
        content += '''  <val> %s </val></row> ''' % (ustr(toxml(note)))
        if flag == False:
            xml += self.generate_empty(cr, uid, ids, datas, header_xml, context=context)
        else:
            extra = False
            if num_year != 0: extra = True
            xml += '''<?xml version="1.0" encoding="UTF-8" ?>
            <report><page size='%s' type='%s' extra='%s'>
            %s
            %s
            %s
            </page></report>
            ''' % (self.size, self.type, extra, header_xml, dept_xml, content)
        return xml


account_compare_budget_custom('report.account.account.compare.budget.custom', "account.report.compare.budget.custom", '', 'addons/account_budget_custom/report/account_report_compare_budget_custom.xsl')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
