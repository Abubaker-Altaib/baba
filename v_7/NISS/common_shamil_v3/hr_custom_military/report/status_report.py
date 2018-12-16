# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw
import calendar
from datetime import datetime
import pooler
from openerp.tools.translate import _



def to_date(str_date):
    return datetime.strptime(str_date, '%Y-%m-%d').date()


class status_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.count = 0
        self.context = context
        super(status_report, self).__init__(cr, uid, name, context)
        self.h_deps_ids = []
        self.localcontext.update({
            'all_len': self._get_all_len,
            'lines': self._get_lines,
            'get_count': self._get_count,
            'to_arabic': self._to_arabic,
        })
    
    def _to_arabic(self, data):
        key = _(data)
        key = key == 'v_good' and 'very good' or key
        key = key == 'u_middle' and 'under middle' or key
        if self.context and 'lang' in self.context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                self.cr, self.uid, [('module','=', 'hr_custom_military'),('type','=', 'selection'),('src','ilike', key), ('lang', '=', self.context['lang'])], context=self.context)
            translation_recs = translation_obj.read(
                self.cr, self.uid, translation_ids, [], context=self.context)
            key = translation_recs and translation_recs[0]['value'] or key
        
        return key

    def _get_all_len(self, data):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        lines_ids = data['form']['lines_ids']

        line_obj = self.pool.get('status_report_line')
        self.all_data = []

        clouses = False

        if start_date:
            if clouses:
                clouses += " and create_date>='" + str(start_date) + "'"
            if not clouses:
                clouses = " create_date>='" + str(start_date) + "'"

        if end_date:
            if clouses:
                clouses += " and create_date<='" + str(end_date) + "'"
            if not clouses:
                clouses = " create_date<='" + str(end_date) + "'"

        for rec in line_obj.browse(self.cr, self.uid, lines_ids):
            try:
                name = rec.name
                tabel = rec.tabel
                state = rec.state
                done_res = all_res = 0
                if rec.state:
                    query = "select count(*) from "+tabel+" where state='"+state+"'"
                    if clouses:
                        query += " and " + clouses
                    
                    self.cr.execute(query)
                    done_res = self.cr.dictfetchall()
                    if done_res:
                        if 'count' in done_res[0]:
                            done_res = done_res[0]['count']

                query = "select count(*) from "+tabel
                if clouses:
                    query += " where " + clouses
                
                self.cr.execute(query)
                all_res = self.cr.dictfetchall()
                if all_res:
                    if 'count' in all_res[0]:
                        all_res = all_res[0]['count']

                
                self.all_data.append({
                    'name':name,
                    'all_res':all_res,
                    'done_res':done_res,
                })
            except:
                pass


        
        return len(self.all_data)

    def _get_lines(self):
        return self.all_data

    def _get_count(self):
        self.count = self.count + 1
        return self.count


report_sxw.report_sxw('report.sys_status.report', 'status_report',
                      'addons/hr_custom_military/report/status_report.mako', parser=status_report, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
