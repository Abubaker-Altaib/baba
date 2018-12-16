# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw

# fuel monthly compare         ----------------------------------------------------------------------------------------------------------------
class compare_fuel(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        self.context = context
        self.total={'month1':0, 'month2':0}
        super(compare_fuel, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'line':self._getdata,
            'sums':self._getdata2,
        })

    def _getdata(self,data):
        """
        Select the first and the second month and the plan type of each department.

        @return: dictionary of report data
        """
        lines = {}
        month = str(data['form']['first_month'])
        year = str(data['form']['first_year'])
        month1 = str(data['form']['second_month'])
        year1 = str(data['form']['second_year'])
        fuel_quantity = self.pool.get('fuel.quantity')
        #get all plan with first date
        lines_ids = fuel_quantity.search(self.cr, self.uid, ['&','|','&',('month','=',month),('year','=',year), ('month','=',month1), ('year','=',year1)], context=self.context)
        for quantity in fuel_quantity.browse(self.cr, self.uid,lines_ids, context=self.context):
            department = quantity.department_id and quantity.department_id.name or ''
            plan_type = quantity.plan_type
            q = lines.get(department+'|'+plan_type, {'department':department, 'plan_type':plan_type, 'month1':0, 'month2':0})
            if quantity.month==month and quantity.year==year:
                q['month1']+=quantity.fuel_qty
                self.total['month1']+=quantity.fuel_qty
            if quantity.month==month1 and quantity.year==year1:
                q['month2']+=quantity.fuel_qty
                self.total['month2']+=quantity.fuel_qty
            lines[department+'|'+plan_type]=q
        return sorted(lines.values(), key=lambda k: k['department'])

    def _getdata2(self,data):
        """
        Compute the total of fuel in specific month.

        @return: dictionary of fuel data
        """
        return [self.total]


report_sxw.report_sxw('report.compare_fuel.report', 'fuel.plan', 'addons/fuel_management/report/compare_fuel.rml' ,parser=compare_fuel,header=True )
