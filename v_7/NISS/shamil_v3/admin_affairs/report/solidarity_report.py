# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw


class solidarity_report(report_sxw.rml_parse):
    """ To manage solidarity report """

    def __init__(self, cr, uid, name, context):
        self.cr = cr
        self.uid = uid
        self.context = context
        self.counter = 0
        super(solidarity_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'lines': self._getdata,
            'get_line_details': self.get_line_details
        })

    def get_category_lines(self, date_from, date_to):
        enrich_obj = self.pool.get('payment.enrich')
        basic_ids = enrich_obj.search(self.cr, self.uid, [('employee_id', 'in', self.employees_ids),
                                                          ('enrich_category', 'in', self.categories_ids), ('date', '>=', date_from), ('date', '<=', date_to)])
        basic = enrich_obj.browse(
            self.cr, self.uid, basic_ids, context=self.context)
        temp = {}
        temp_names = {}
        for line in basic:
            temp[line.enrich_category.id] = temp.get(
                line.enrich_category.id, [])
            temp[line.enrich_category.id].append(line)

            temp_names[line.enrich_category.id] = temp_names.get(
                line.enrich_category.id, {'sum': 0})
            temp_names[line.enrich_category.id][
                'name'] = line.enrich_category.name
            temp_names[line.enrich_category.id][
                'type'] = line.enrich_category.operation_type
            temp_names[line.enrich_category.id]['sum'] += line.amount

        self.category_lines = [x for x in temp.values()]

        self.category_names = [x for x in temp_names.values()]

    def get_line_details(self):
        if self.category_names:
            current_category = self.category_names[self.counter]
            if str(current_category['type']) == 'deposit':
                current_category['type'] = 'إيداع'
            else:
                current_category['type'] = 'سحب'
            self.counter += 1
            return [current_category]
        return []

    def _getdata(self, data):

        date_from = str(data['form']['date_from'])
        date_to = str(data['form']['date_to'])
        self.employees_ids = data['form']['employees_ids']
        self.categories_ids = data['form']['categories_ids']

        employee_obj = self.pool.get('hr.employee')
        category_obj = self.pool.get('enrich.category')

        if not self.employees_ids:
            self.employees_ids = employee_obj.search(
                self.cr, self.uid, [], context=self.context)
        if not self.categories_ids:
            self.categories_ids = category_obj.search(
                self.cr, self.uid, [('type', '=', 'solidarity')], context=self.context)

        self.get_category_lines(date_from, date_to)

        return self.category_lines

report_sxw.report_sxw('report.solidarity_report.report', 'payment.enrich',
                      'addons/admin_affairs/report/solidarity_report.rml', parser=solidarity_report, header=True)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
