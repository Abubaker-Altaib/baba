# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv, orm
import time
from datetime import datetime
import pooler
from report.interface import report_rml, toxml
from report import report_sxw
from openerp.tools import ustr
from openerp.tools.translate import _
from account_budget_custom.report import account_report_budget

class report_custom(report_rml):

    def _get_fiscalyear_company_detail_total(self, cr, uid, ids, datas, analytic_acc=False, context={}):
        account_obj = self.pool.get('account.account')
        fiscalyear_pool = self.pool.get('account.fiscalyear')
        budget_class_obj = self.pool.get('account.budget.classification')
        fisc_budget_line_obj = self.pool.get('account.fiscalyear.budget.lines')
        form = datas.get('form', {})
        budget_report = account_report_budget.account_budget(cr, uid, "", context=context)
        budget_report.set_context([], datas, ids)
        res = []	
        account_chart = form.get('chart_account_id', [])
        analytic_chart = analytic_acc and analytic_acc or form.get('chart_analytic_account_id', [])
        fiscalyear_id = form.get('fiscalyear_id', False) and [form.get('fiscalyear_id', False)] or []
        chart_analytic_account = self.pool.get('account.analytic.account').browse(cr, uid, analytic_chart, context=context)
        FY = fiscalyear_pool.browse(cr, uid, fiscalyear_id, context=context)
        fiscalyear_id = FY and fiscalyear_pool.search(cr, uid, [('date_start', '>=', FY[0].date_start),('date_stop', '<=', FY[0].date_stop),
                                                                ('company_id', '=', chart_analytic_account.company_id.id)], context=context)
        total = {'planned_amount':0.0}
        analytic_child_ids = budget_report._get_children_and_consol(cr, uid, analytic_chart, 'account.analytic.account', context=context)
        account_child_ids = budget_report._get_children_and_consol(cr, uid, account_chart, 'account.account', context=context)
        class_ids = budget_class_obj.search(cr, uid, [], context=context)
        class_objs = budget_class_obj.browse(cr, uid, class_ids, context=context)
        total_budget = {'name':'Total', 'planned_amount':0.0}
        for  class_obj in class_objs:
	        account_budget = {'code':class_obj.code, 'name':class_obj.name, 'planned_amount':0.0}
	        acc_ids = account_obj.search(cr, uid, [('id', 'in', account_child_ids), ('budget_classification', '=', class_obj.id)], context=context)
	        lines = fisc_budget_line_obj.search(cr, uid, [('account_fiscalyear_budget_id.fiscalyear_id', 'in', fiscalyear_id), ('account_fiscalyear_budget_id.analytic_account_id', 'in', analytic_child_ids), ('general_account_id', 'in', acc_ids)], context=context)
	        for line in fisc_budget_line_obj.browse(cr, uid, lines, context=context):
		       account_budget['planned_amount'] += line.planned_amount
	        res.append(account_budget)
	        total_budget['planned_amount'] += account_budget['planned_amount']
        res.append(total_budget)
        return res

    def _get_fiscalyear_company_detail(self, cr, uid, ids, datas, analytic_acc=False, context={}):
        account_obj = self.pool.get('account.account')
        fiscalyear_pool = self.pool.get('account.fiscalyear')
        fisc_budget_line_obj = self.pool.get('account.fiscalyear.budget.lines')
        form = datas.get('form', {})
        budget_report = account_report_budget.account_budget(cr, uid, "", context=context)
        budget_report.set_context([], datas, ids)
        res = []	
        account_chart = form.get('chart_account_id', [])
        analytic_chart = analytic_acc and analytic_acc or form.get('chart_analytic_account_id', [])
        fiscalyear_id = form.get('fiscalyear_id', False) and [form.get('fiscalyear_id', False)] or []
        chart_analytic_account = self.pool.get('account.analytic.account').browse(cr, uid, analytic_chart, context=context)
        FY = fiscalyear_pool.browse(cr, uid, fiscalyear_id, context=context)
        fiscalyear_id = FY and fiscalyear_pool.search(cr, uid, [('date_start', '>=', FY[0].date_start),('date_stop', '<=', FY[0].date_stop),
                                                                ('company_id', '=', chart_analytic_account.company_id.id)], context=context)
        total = {'planned_amount':0.0}
        analytic_child_ids = budget_report._get_children_and_consol(cr, uid, analytic_chart, 'account.analytic.account', context=context)
        account_child_ids = budget_report._get_children_and_consol(cr, uid, account_chart, 'account.account', context=context)
        general_account = budget_report._sort_filter(cr, uid, account_child_ids, context=context)
        budget_class = {'id':False, 'name':''}
        class_total = {'planned_amount':0.0}

        for account in account_obj.browse(cr, uid, general_account, context=context):
            classification = account.budget_classification and account.budget_classification[0] or False
            if budget_class['id'] != classification.id:
                if budget_class['id'] != False:
                    res.append({'code':'*', 'name':budget_class['name'], 'planned_amount':class_total['planned_amount']})
                    class_total = {'planned_amount':0.0}
                budget_class['id'] = classification.id
            account_budget = {'code':account.code, 'name':account.name, 'planned_amount':0.0}
            lines = fisc_budget_line_obj.search(cr, uid, [('account_fiscalyear_budget_id.fiscalyear_id', 'in', fiscalyear_id), ('account_fiscalyear_budget_id.analytic_account_id', 'in', analytic_child_ids), ('general_account_id', '=', account.id)], context=context)
            if lines:
                for line in fisc_budget_line_obj.browse(cr, uid, lines, context=context):
                    account_budget['planned_amount'] += line.planned_amount
                total['planned_amount'] += account_budget['planned_amount']
                class_total['planned_amount'] += account_budget['planned_amount']
                if res and res[len(res) - 1]['code'] == account_budget['code'] and account_budget['code'] != '*':
                    res[len(res) - 1]['planned_amount'] += account_budget['planned_amount']
                else:
                   res.append(account_budget)
            else:
                res.append(account_budget)
            budget_class['name'] = classification.name
        res.append({
            'code':'*',
            'name':budget_class['name'],
            'planned_amount':class_total['planned_amount'],
        })
        res.append({
            'code': '*',
            'name': _('Total'),
            'planned_amount': total['planned_amount'],
        })
        return res

    def create_xml(self, cr, uid, ids, datas, context=None):
        self.pool = pooler.get_pool(cr.dbname)
        period_obj = self.pool.get('account.period')
        fiscal_year_obj = self.pool.get('account.fiscalyear')
        user_obj = self.pool.get('res.users')
        analytic_obj = self.pool.get('account.analytic.account')
        datas.get('form', {}).update({"fiscalyear_id": datas.get('form', {}).get('first_fiscalyear')})
        fiscalyear = datas.get('form', {}).get('first_fiscalyear')
        analytic_account_ids = datas.get('form', {}).get('analytic_account_ids', [])  or [datas.get('form', {}).get('chart_analytic_account_id')] or []    
        period_from = datas.get('form', {}).get('period_from', False) and [datas.get('form', {}).get('period_from', False)] or period_obj.search(cr, uid, [('fiscalyear_id', '=', fiscalyear)], context=context, order='date_start', limit=1)
        period_to = datas.get('form', {}).get('period_to', False) and [datas.get('form', {}).get('period_to', False)] or period_obj.search(cr, uid, [('fiscalyear_id', '=', fiscalyear)], context=context, order='date_start desc', limit=1)
        year = fiscal_year_obj.browse(cr, uid, fiscalyear, context=context).name
        title = datas.get('form', {}).get('report_name') == 'summary' and u'تقرير ملخص الموازنة للعام %s' % (year) or \
                datas.get('form', {}).get('report_name') == 'flow' and u'التدفقــات النقديـة'
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
        header_xml = '''
        <header>
        <date>%s</date>
        <company>%s</company>
        <accuracy>%s</accuracy>
        <period_from>%s</period_from>
        <period_to>%s</period_to>
        ''' % (str(self.rml_obj.formatLang(time.strftime("%Y-%m-%d"), date=True)) + ' ' + str(time.strftime("%H:%M")),
               usr_company.name, str(self.accuracy) + ' ' + (usr_company.currency_id.units_name or ' '), period_from, period_to)

        if datas.get('form', {}).get('report_name') == 'summary':
            return self.dept_compare_fiscalyear_budget_xml(cr, uid, ids, datas, header_xml + '<title>%s</title></header>' % (title), context=context)
        elif datas.get('form', {}).get('report_name') == 'flow':
            xml = ''
            for analytic_acc in analytic_account_ids:
                full_title = title + ' - ' + analytic_obj.browse(cr, uid, analytic_acc, context=context).name
                xml += self.period_compare_budget_xml(cr, uid, ids, datas, header_xml + '<title>%s</title></header>' % (full_title), analytic_acc, context=context)
            return '''<?xml version="1.0" encoding="UTF-8" ?><report>%s</report>''' % (xml)


    def dept_compare_fiscalyear_budget_xml(self, cr, uid, ids, datas, header_xml, context=None):
        analytic_account_obj = self.pool.get('account.analytic.account')
        dept_xml = '''<datas>'''
        main_dept = analytic_account_obj.search(cr, uid, [('main_dept', '=', True),('company_id', '=', datas['form']['company_id'])], context=context, order='code desc')
        analytic_accounts = analytic_account_obj.browse(cr, uid, main_dept, context=context)
        if not analytic_accounts:
            raise orm.except_orm(_('Error!'), _('There is no Data to Display ' )) 
        for analytic in analytic_accounts:
            dept_xml += ''' <header name="%s"/> ''' % (ustr(toxml(analytic.name)))
        dept_xml += '''</datas>'''
        length = len(main_dept) + 1
        dept_xml += '''<cols>%s120,60</cols>''' % ((str((800*self.columns-180) / length) + ',') * int(length))
        content = ''
        result = []
        for analytic in analytic_accounts:
            if datas.get('form', {}).get('type_selection', 'detail') == 'detail':
                result.append(self._get_fiscalyear_company_detail(cr, uid, ids, datas, analytic.id, context=context))
            else:
                result.append(self._get_fiscalyear_company_detail_total(cr, uid, ids, datas, analytic.id, context=context))
        if result:
            for i in range(len(result[0])):
                content += ''' <row> '''
                total = 0
                vals = ''
                for j in range(len(result)):
                    total += i < len(result[j]) and result[j][i]['planned_amount'] / self.accuracy or 0.0
                    row_type = i < len(result[j]) and result[j][i].get('code', '*') == '*' and 'total' or 'detail'
                    vals += ''' <cols type="%s">  <val> ''' % (row_type)
                    vals += ''' %s ''' % (self.rml_obj.formatLang(i< len(result[j]) and result[j][i]['planned_amount'] / self.accuracy or 0.0))
                    vals += ''' </val> </cols> '''
                code = i < len(result[j]) and (result[0][i].get('code', '*') == '*' and ' ' or result[0][i].get('code', '*')) or ' ' 
                content += ''' <cols type="%s"> <val> %s </val></cols> ''' % (row_type,self.rml_obj.formatLang(total))
                content += vals + ''' <cols type="%s"> <val> %s </val> </cols> <cols type="%s"> <val> %s </val> </cols>''' % (row_type,ustr(toxml(result[0][i]['name'])),row_type,ustr(toxml(code)))
                content += ''' </row> '''

        xml = '''<?xml version="1.0" encoding="UTF-8" ?>
        <report><page size='%s' type='%s'>
        %s
        %s
        %s
        </page></report>
        ''' % (self.size, self.type, header_xml, dept_xml, content)
        return xml


    def period_compare_budget_xml(self, cr, uid, ids, datas, header_xml, analytic_acc=False, context={}):
        period_obj = self.pool.get('account.period')
        fiscal_year_obj = self.pool.get('account.fiscalyear')
        form = datas.get('form', {})
        dept_xml = '''<datas>'''
        fiscalyear = fiscal_year_obj.browse(cr, uid, form.get('fiscalyear_id', []), context=context)
        period_objs = fiscalyear and fiscalyear.period_ids
        period_objs.reverse()
        period_from = form.get('period_from', False)
        period_to = form.get('period_to', False)
	
        period_from_start = period_from and period_obj.browse(cr, uid, period_from, context=context).date_start or ''
        period_stop = period_to and period_obj.browse(cr, uid, period_to, context=context).date_stop or ''

        periods = not (period_from or period_to) and period_objs or []
        if not periods:
            for period in period_objs:
                if datetime.strptime(period.date_start, '%Y-%m-%d').date() >= datetime.strptime(period_from_start, '%Y-%m-%d').date() and datetime.strptime(period.date_stop, '%Y-%m-%d').date() <= datetime.strptime(period_stop, '%Y-%m-%d').date():
                    periods.append(period)
        length = 1
        for period in periods:
            if not period.special:
                dept_xml += ''' <header name="%s"/> ''' % (ustr(toxml(period.name)))
                length += 1
        dept_xml += '''</datas>'''
        dept_xml += '''<cols>%s120,60</cols>''' % ((str((800*self.columns-180) / length) + ',') * int(length))
        content = ''
        result = []
        for period in periods:
            if not period.special:
                budget_report = account_report_budget.account_budget(cr, uid, "", context=context)
                budget_report.set_context([], datas, ids)
                form.update({'period_from':period.id, 'period_to':period.id})
                if form.get('type_selection', 'detail') == 'detail':
                    result.append(budget_report._get_company_detail(form, analytic_acc))
                else:
                    result.append(budget_report._get_company_detail_total(form, analytic_acc))
        if result:
            for i in range(len(result[0])):
                content += ''' <row> '''
                total = 0
                vals = ''
                for j in range(len(result)):
                    total += result[j][i]['planned_amount'] / self.accuracy
                    row_type = result[j][i].get('code', '*') == '*' and 'total' or 'detail'
                    vals += ''' <cols type="%s">  <val> ''' % (row_type)
                    vals += ''' %s ''' % (self.rml_obj.formatLang(result[j][i]['planned_amount'] / self.accuracy))
                    vals += ''' </val> </cols> '''
                code = result[0][i].get('code', '*') == '*' and ' ' or result[0][i].get('code', '*')
                content += ''' <cols type="%s"> <val> %s </val></cols> '''% (row_type,self.rml_obj.formatLang(total))
                content += vals + ''' <cols type="%s"> <val> %s </val> </cols> <cols type="%s"> <val> %s </val> </cols>'''% (row_type,ustr(toxml(result[0][i]['name'])),row_type,ustr(toxml(code)))
                content += ''' </row> '''
        xml = '''
        <page size='%s' type='%s'>
        %s
        %s
        %s
        </page>
        ''' % (self.size, self.type, header_xml, dept_xml, content)
        return xml

    def dept_compare_period_budget_xml(self, cr, uid, ids, datas, header_xml, context=None):
        analytic_account_obj = self.pool.get('account.analytic.account')
        dept_xml = '''<datas>'''
        main_dept = analytic_account_obj.search(cr, uid, [('main_dept', '=', True)], context=context, order='code desc')
        analytic_accounts = analytic_account_obj.browse(cr, uid, main_dept, context=context)
        for analytic in analytic_accounts:
            dept_xml += ''' <header name="%s"/> ''' % (ustr(toxml(analytic.name)))
        dept_xml += '''</datas>'''
        length = len(main_dept) + 1
        dept_xml += '''<cols>%s120,60</cols>''' % ((str((800*self.columns-180) / length) + ',') * int(length))
        content = ''
        result = []
        for analytic in analytic_accounts:
            budget_report = account_report_budget.account_budget(cr, uid, "", context=context)
            budget_report.set_context([], datas, ids)
            if datas.get('form', {}).get('type_selection', 'detail') == 'detail':
                result.append(budget_report._get_company_detail(datas.get('form', {}), analytic.id))
            else:
                result.append(budget_report._get_company_detail_total(datas.get('form', {}), analytic.id))
        if result:
            for i in range(len(result[0])):
                content += ''' <row> '''
                total = 0
                vals = ''
                for j in range(len(result)):
                    total += result[j][i]['planned_amount'] / self.accuracy
                    row_type = result[j][i].get('code', '*') == '*' and 'total' or 'detail'
                    vals += ''' <cols type="%s">  <val> ''' % (row_type)
                    vals += ''' %s ''' % (self.rml_obj.formatLang(result[j][i]['planned_amount'] / self.accuracy))
                    vals += ''' </val> </cols> '''
                code = result[0][i].get('code', '*') == '*' and ' ' or result[0][i].get('code', '*')
                content += ''' <cols type="%s"> <val> %s </val></cols> '''% (row_type,self.rml_obj.formatLang(total))
                content += vals + ''' <cols type="%s"> <val> %s </val> </cols> <cols type="%s"> <val> %s </val> </cols>'''% (row_type,ustr(toxml(result[0][i]['name'])),row_type,ustr(toxml(code)))
                content += ''' </row> '''

        xml = '''<?xml version="1.0" encoding="UTF-8" ?>
        <report><page size='%s' type='%s'>
        %s
        %s
        %s
        </page></report>
        ''' % (self.size, self.type, header_xml, dept_xml, content)
        return xml
report_custom('report.account.compare.dept.budget', "account.report.compare.budget", '', 'account_budget_custom/report/account_compare_dept_budget_report.xsl')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
