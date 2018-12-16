# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw

class vehicles_accidents_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        self.context = context
        super(vehicles_accidents_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'line': self._getdata,
        })

    def _getdata(self, data):
        
        start_date = str(data['form']['start_date'])
        end_date = str(data['form']['end_date'])
        type = str(data['form']['type'])
        departments_ids = data['form']['departments_ids']
        vehicles_ids = data['form']['vehicles_ids']
        vehicle_accident_obj = self.pool.get('vehicle.accident')
        domain = [('state', '=', 'done'),
        ('accident_date', '>=', start_date),
        ('accident_date', '<=', end_date), ]

        v_domain = [('state','=','confirm')]
        vehicles_ids and v_domain.append(('id', 'in', vehicles_ids))
        departments_ids and v_domain.append(('department_id', 'in', departments_ids))
        vehicle_obj = self.pool.get('fleet.vehicle')
        dep_v_ids = vehicle_obj.search(self.cr, self.uid, v_domain)

        dep_v_ids and domain.append(('vehicle_id', 'in', dep_v_ids))
        
        

        basic_ids= vehicle_accident_obj.search(self.cr, self.uid, domain)
        basic= vehicle_accident_obj.browse(self.cr, self.uid, basic_ids)
        return basic


report_sxw.report_sxw('report.vehicles_accidents_report.report', 'fleet.vehicle',
                      'addons/vehicles_maintenance/reports/vehicles_accidents_report.rml', parser=vehicles_accidents_report, header=True)
