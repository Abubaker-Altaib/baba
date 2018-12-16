# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw


class spares_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        self.context = context
        super(spares_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'line': self._getdata,
        })

    def _getdata(self, data):
        start_date = str(data['form']['start_date'])
        end_date = str(data['form']['end_date'])
        vehicles_ids = data['form']['vehicles_ids']
        products_ids = data['form']['products_ids']

        spares_obj = self.pool.get('maintenance.spare')
        domain = []
        vehicles_ids and domain.append(
            ('vehicle_id', 'in', vehicles_ids))
        
        products_ids and domain.append(
            ('product_id', 'in', products_ids))
        
        start_date != 'False' and domain.append(('end_datetime', '>=', start_date))
        end_date != 'False' and domain.append(('end_datetime', '<=', end_date))
        

        basic_ids = spares_obj.search(self.cr, self.uid, domain)
        basic = spares_obj.browse(self.cr, self.uid, basic_ids)
        return basic


report_sxw.report_sxw('report.spares_report.report', 'maintenance.spare',
                      'addons/vehicles_maintenance/reports/spares_report.rml', parser=spares_report, header=True)
