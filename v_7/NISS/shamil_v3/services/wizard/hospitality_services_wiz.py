# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from openerp.osv import osv, fields


# Hospitality Service wizard report for Specific period of  Time & Department & State

class hospitality_service_wiz(osv.osv_memory):

    _name = "hospitality.service.wiz"
    _description = "Hospitality Service wizard"

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
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'hospitality.service',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hospitality_service.report',
            'datas': datas,
            }
hospitality_service_wiz()
    
