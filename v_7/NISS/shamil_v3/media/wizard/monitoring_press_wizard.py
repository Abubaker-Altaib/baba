# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv


class monitoring_press_report(osv.osv_memory):
    """
    To manage monitoring press report """

    _name = "monitoring.press.report"
    _description = "Monitoring press report"
    TYPE_SELECTION = [
        ('positive', 'Positive'),
	('negative', 'Negative'),
	('info', 'Information'),
	 ]

    _columns = {
        'Date_from': fields.date('Date From', required=True,), 
        'Date_to': fields.date('Date To', required=True),
        'paper_id':fields.many2one('news.papers', 'Paper',),
        'evaluation': fields.selection(TYPE_SELECTION,'Evaluation', select=True),
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'monitoring.press',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'monitoring_press.report',
            'datas': datas,
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
