# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw

# fuel monthly compare         -------------------------------------------


class maintenance_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        self.context = context
        super(maintenance_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'line': self._getdata,
            'trans': self.trans,
            'get_names': self.get_names,
        })

    def _getdata(self, data):
        state = str(data['form']['state'])
        start_date = str(data['form']['start_date'])
        end_date = str(data['form']['end_date'])
        departments_ids = data['form']['departments_ids']

        maintenance_obj = self.pool.get('maintenance.job')
        domain = []
        departments_ids and domain.append(
            ('maintenance_department_id', 'in', departments_ids))
        if state:
            if state == 'done':
                start_date != 'False' and domain.append(
                    ('start_datetime', '>=', start_date))
                end_date != 'False' and domain.append(
                    ('end_datetime', '<=', end_date))
                domain.append(('state', '=', 'done'))
            if state == 'not_done':
                start_date != 'False' and domain.append(
		            ('start_datetime', '>=', start_date))
                domain.append(('state', '!=', 'done'))
            if  state == False:
                start_date != 'False' and domain.append(('start_datetime', '>=', start_date))
                end_date != 'False' and domain.append(('end_datetime', '<=', end_date))
        basic_ids = maintenance_obj.search(self.cr, self.uid, domain)
        basic = maintenance_obj.browse(self.cr, self.uid, basic_ids)
        return basic

    def trans(self, data):
        key = data
        try:
            maintenance_job = self.pool.get('maintenance.job')
            selection = maintenance_job._columns['state'].selection
            selection = filter(lambda x : x[0] == key, selection)
            if selection:
                key = selection[0][1]
            if self.context and 'lang' in self.context:
                translation_obj = self.pool.get('ir.translation')
                translation_ids = translation_obj.search(
                    self.cr, self.uid, [('src', '=', key), ('lang', '=', self.context['lang']), ('module','=','vehicles_maintenance')], context=self.context)
                translation_recs = translation_obj.read(
                    self.cr, self.uid, translation_ids, [], context=self.context)
                key = translation_recs and translation_recs[0]['value'] or key
        except:
            pass
        return key

    def get_names(self, data):
        st = ""
        for x in data:
            name = (x.name)
            st = st +","+name
        if st != '':st = st[1:]    
        return st

         


report_sxw.report_sxw('report.maintenance_report.report', 'maintenance.job',
                      'addons/vehicles_maintenance/reports/maintenance_report.rml', parser=maintenance_report, header=True)
