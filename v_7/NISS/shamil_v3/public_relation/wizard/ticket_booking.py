# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

#----------------------------------------
# Class Ticket Booking wizard
#----------------------------------------
class ticket_booking_wizard(osv.osv_memory):
    """
    To manage Ticket Booking wizard s"""

    _name = "ticket.booking.wizard"
    _description = "Ticket Booking wizard"

    STATE_SELECTION = [
    ('draft', 'Draft'),
    ('dept_confirm','Waiting for General Department Manager To approve'),
    ('admin_affiars_confirm','Waiting for GM To approve'),
    ('confirmed', 'Waiting for PRM Section Manager To approve'),
    ('approved', 'Waiting for PRM office To process'),
    ('done', 'Done'),
    ('cancel', 'Cancel'),  ]

    TRAVEL_PURPOSE_SELECTION = [
    ('training', 'Training'),
    ('mission', 'Mission'),
    ('treatment','Treatment'),
    ('other', 'Other'),
 				]

    TYPE_SELECTION = [
    ('internal', 'Internal'),
    ('external','External'),
    ]

    PROCEDURE_SELECTION = [
        ('sudanese', 'Sudanese'),
        ('foreigners', 'Foreigners'),
        ('both', 'Both'),]
    _columns = {
        'date_from': fields.date('From', required=True,), 
        'date_to': fields.date('To', required=True),
        'type': fields.selection(TYPE_SELECTION,'Ticket Type',selct=True),
        'state': fields.selection(STATE_SELECTION,'State',), 
        'department_id':  fields.many2one('hr.department', 'Department',),
        'employee_id':fields.many2one('hr.employee', 'Employee'),
	'foreigner_id':fields.many2one('public.relation.foreigners','Foreigner'),
        'procedure_for': fields.selection(PROCEDURE_SELECTION,'Procedure For',help="To decide The procedure is for sudanese of foreigner",),
	'company_id':fields.many2one('res.company','Company',readonly=True),
	'partner_id':fields.many2one('res.partner','Partner'),
        'travel_purpose':fields.selection(TRAVEL_PURPOSE_SELECTION,'Travel Purpose', select=True,),

    }
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'ticket.booking.wizard', context=c),
                }

    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'ticket.booking',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'ticket_booking.report',
            'datas': datas,
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:  
