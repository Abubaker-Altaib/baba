# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw

class vehicles_maintenances_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        self.context = context
        super(vehicles_maintenances_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'line': self._getdata,
            'get_names': self.get_names,
        })

    def _getdata(self, data):
        
        start_date = str(data['form']['start_date'])
        end_date = str(data['form']['end_date'])
        type = str(data['form']['type'])
        departments_ids = data['form']['departments_ids']
        vehicles_ids = data['form']['vehicles_ids']
        vehicle_maint_obj = self.pool.get('maintenance.spare')
        domain = [('job_state', '=', 'done'),
        ('start_datetime', '>=', start_date),
        ('start_datetime', '<=', end_date), ]

        v_domain = [('state','=','confirm')]
        vehicles_ids and v_domain.append(('id', 'in', vehicles_ids))
        departments_ids and v_domain.append(('department_id', 'in', departments_ids))
        vehicle_obj = self.pool.get('fleet.vehicle')
        dep_v_ids = vehicle_obj.search(self.cr, self.uid, v_domain)

        dep_v_ids and domain.append(('vehicle_id', 'in', dep_v_ids))
        
        

        basic_ids= vehicle_maint_obj.search(self.cr, self.uid, domain)
        basic= vehicle_maint_obj.browse(self.cr, self.uid, basic_ids)
        return basic

    def get_names(self, data):
        try:
            data = data.read([])[0]['damages_ids']
            data = data[0]
            data = data[2]
            st = ""
            for x in self.pool.get('maintenance.damage').browse(self.cr, self.uid, data):
                name = (x.name)
                st = st +","+name
            if st != '':st = st[1:]
            return st
        except:
            return ""


report_sxw.report_sxw('report.vehicles_maintes_report.report', 'fleet.vehicle',
                      'addons/vehicles_maintenance/reports/vehicles_maintenances_report.rml', parser=vehicles_maintenances_report, header=True)
