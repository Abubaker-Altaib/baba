# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class foreigners_procedures_wiz_specific_time(osv.osv_memory):
    """
    To manage foreigners Procedures wizard report for Specific period of  Time """

    _name = "foreigners.procedures.wiz.specific.time"
    _description = "foreigners procedures wizard for specific time"

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('requested', 'Waiting for DM To Confirm'),
        ('confirmed', 'Waiting for Genral DM To Confirm'),
        ('second_confirmed', 'Waiting for GM To Approve'),
	('approved', 'Waiting for PRM Manager To Process'),
	('second_approved', 'Waiting for PRM office Process'),
	('done', 'Done'),
        ('cancel', 'Cancel'), ]

    TYPE_SELECTION = [
        ('sudanese', 'Sudanese'),
        ('foreigners', 'Foreigners'),]

    _columns = {
        'Date_from': fields.date('Date From', required=True,), 
        'Date_to': fields.date('Date To', required=True),
    	'state': fields.selection(STATE_SELECTION,'State',),
    	'department_id':fields.many2one('hr.department', 'Department',),
   	'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
	'procedure_for': fields.selection(TYPE_SELECTION,'Procedure For',)
    }
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'foreigners.procedures.wiz.specific.time', context=c),
                }


    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'foreigners.procedures.request',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'foreigners.procedures.specific.report',
            'datas': datas,
            }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
    
