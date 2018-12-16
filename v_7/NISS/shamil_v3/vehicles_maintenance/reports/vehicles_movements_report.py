# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw

class vehicles_movements_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        self.context = context
        super(vehicles_movements_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'line': self._getdata,
        })

    def _getdata(self, data):
        
        start_date = str(data['form']['start_date'])
        end_date = str(data['form']['end_date'])
        type = str(data['form']['type'])
        departments_ids = data['form']['departments_ids']
        vehicles_ids = data['form']['vehicles_ids']
        vehicle_move_obj = self.pool.get('vehicle.move')
        domain = [('state', '=', 'done'),
        ('move_date', '>=', start_date),
        ('move_date', '<=', end_date), ]
        departments_ids and domain.append(('department_id', 'in', departments_ids))
        vehicles_ids and domain.append(('vehicle_id', 'in', vehicles_ids))

        basic_ids= vehicle_move_obj.search(self.cr, self.uid, domain)
        basic= vehicle_move_obj.browse(self.cr, self.uid, basic_ids)
        return basic


report_sxw.report_sxw('report.vehicles_movements_report.report', 'fleet.vehicle',
                      'addons/vehicles_maintenance/reports/vehicles_movements_report.rml', parser=vehicles_movements_report, header=True)
