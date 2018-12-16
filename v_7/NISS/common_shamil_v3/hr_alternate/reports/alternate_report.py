# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from openerp import tools
from itertools import groupby
from operator import itemgetter
import math


class alternate_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        self.context = context
        super(alternate_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'lines': self.lines,
            'get_weekday' : self.get_weekday,
        })

    def get_weekday(self, str):
        key = str
        if self.context and 'lang' in self.context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                self.cr, self.uid, [('src', '=', key), ('lang', '=', self.context['lang'])], context=self.context)
            translation_recs = translation_obj.read(
                self.cr, self.uid, translation_ids, [], context=self.context)
            
            key = translation_recs and translation_recs[0]['value'] or key
        return key
    def get_date(self, str):
        return datetime.strptime(str, "%Y-%m-%d")


    def lines(self, data):
        lines = []
        process_obj = self.pool.get('hr.alternative.process')
        #print form the processes tree view
        process_ids = self.context.get('active_ids', [])

        start_date = end_date = categories_ids = False
        #print form the report menu

        if data.get('form', []):
            start_date = data['form']['start_date']
            categories_ids = data['form']['alternative_setting_ids']
            process_ids = process_obj.search(self.cr, self.uid, [ (start_date and ('date_from','=',start_date)) or ('date_from','!=',start_date), ('alternative_setting_id','in',categories_ids)], context=self.context)
        
        lines = process_obj.browse(self.cr, self.uid, process_ids, context=self.context)
        
        return lines


report_sxw.report_sxw('report.alternate_report.report', 'hr.alternative.process',
                      'addons/hr_alternate/reports/alternate_report.mako', parser=alternate_report)
