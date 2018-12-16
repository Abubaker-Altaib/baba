# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from osv import fields, osv



class media_service_report(osv.osv_memory):
    """
    To mamnage media service report"""
    _name = "media.service.report"
    _description = "Media Service"

    STATE_SELECTION = [
        ('done', 'All completed Requests'),
	('notdone', 'All Requests incomplete'), ]

    _columns = {
        'Date_from': fields.date('Date From', required=True,), 
        'Date_to': fields.date('Date To', required=True),
    	'state': fields.selection(STATE_SELECTION,'State',),
    	'department_id':fields.many2one('hr.department', 'Department',),
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'media.order',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'media_service.report',
            'datas': datas,
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
