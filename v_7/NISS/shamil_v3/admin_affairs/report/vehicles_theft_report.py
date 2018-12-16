# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw

class vehicles_theft_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        self.context = context
        super(vehicles_theft_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'line': self._get_data,
            'lines': self._get_lines,
        })

    def _get_data(self, data):
        res=[]
        res_ids=[]
        vehicle_theft_obj = self.pool.get('vehicle.theft')
        model_obj=self.pool.get('fleet.vehicle.model')
        type_obj=self.pool.get('vehicle.category')
        emp_obj=self.pool.get('hr.employee')

        ttype=str(data['form']['type'])
        if ttype == 'model':
            model_ids=data['form']['model_ids']
            models=[]
            for model in model_ids:
                res_ids= vehicle_theft_obj.search(self.cr, self.uid, [('state', '!=', 'draft'),('model_id', '=', model)])
                if res_ids:
                    models.append(model)
            res= model_obj.browse(self.cr, self.uid, models)

        elif ttype == 'type':
            type_ids=data['form']['type_ids']
            types=[]
            for ttype in type_ids:
                res_ids= vehicle_theft_obj.search(self.cr, self.uid, [('state', '!=', 'draft'),('vehicle_type', '=', ttype)])
                if res_ids:
                    types.append(ttype)
            res= type_obj.browse(self.cr, self.uid, types)

        elif ttype == 'employee':
            employee_ids=data['form']['employee_ids']
            emps=[]
            for emp in employee_ids:
                res_ids= vehicle_theft_obj.search(self.cr, self.uid, [('state', '!=', 'draft'),('employee_id', '=', emp)])
                if res_ids:
                    emps.append(emp)
            res= emp_obj.browse(self.cr, self.uid,emps)

        elif ttype == 'period':
            start_date = str(data['form']['start_date'])
            end_date = str(data['form']['end_date'])
            res_ids= vehicle_theft_obj.search(self.cr, self.uid, [('state', '!=', 'draft'),('theft_date', '>=', start_date),('theft_date', '<=', end_date)])
            if res_ids:
                res= vehicle_theft_obj.browse(self.cr, self.uid, res_ids)

        elif ttype == 'place':
            place = str(data['form']['place'])
            res_ids= vehicle_theft_obj.search(self.cr, self.uid, [('state', '!=', 'draft'),('place', '=', place)])
            if res_ids:
                res= place
        return res

    def _get_lines(self,data,type_id):
        res=[]
        vehicle_theft_obj = self.pool.get('vehicle.theft')
        ttype=str(data['form']['type'])
        if ttype == 'model':
            model_ids=data['form']['model_ids']
            res_ids= vehicle_theft_obj.search(self.cr, self.uid, [('state', '!=', 'draft'),('model_id', '=', type_id)])
            res= vehicle_theft_obj.browse(self.cr, self.uid, res_ids)


        elif ttype == 'type':
            type_ids=data['form']['type_ids']
            res_ids= vehicle_theft_obj.search(self.cr, self.uid, [('state', '!=', 'draft'),('vehicle_type', 'in', type_ids)])
            res= vehicle_theft_obj.browse(self.cr, self.uid, res_ids)

        elif ttype == 'employee':
            employee_ids=data['form']['employee_ids']
            res_ids= vehicle_theft_obj.search(self.cr, self.uid, [('state', '!=', 'draft'),('employee_id', 'in', employee_ids)])
            res= vehicle_theft_obj.browse(self.cr, self.uid, res_ids)


        elif ttype == 'period':
            start_date = str(data['form']['start_date'])
            end_date = str(data['form']['end_date'])
            res_ids= vehicle_theft_obj.search(self.cr, self.uid, [('state', '!=', 'draft'),('theft_date', '>=', start_date),('theft_date', '<=', end_date)])
            res= vehicle_theft_obj.browse(self.cr, self.uid, res_ids)

        elif ttype == 'place':
            place = str(data['form']['place'])
            res_ids= vehicle_theft_obj.search(self.cr, self.uid, [('state', '!=', 'draft'),('place', '=', place)])
            res= vehicle_theft_obj.browse(self.cr, self.uid, res_ids)

        return res


report_sxw.report_sxw('report.vehicles_theft_report.report', 'fleet.vehicle',
                      'addons/admin_affairs/report/vehicles_theft_report.rml', parser=vehicles_theft_report, header=True)
