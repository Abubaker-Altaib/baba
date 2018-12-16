# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class clearance_report(osv.osv_memory):
    _name = "clearance.report"
    _description = "clearance Report"

    Ship_SELECTION=[
	('sea_freight','By Sea'),
	('air_freight','By Airport'),
	('free_zone','By Free Zone'),
        ('land_freight', 'Land Freight'),
		]
    PURPOSE_SELECTION=[
	('pro','Project'),
	('po','Purchase'),
		]

    CLEARANCE_SELECTION = [
        ('income', 'income'),
        ('outcome', 'outcome'),
    ]
    REPORT_TYPE = [
        ('done', 'Done'),
        ('all', 'All'),
    ]

    _columns = {
        'Date_from': fields.date('Date From', required=True,), 
        'Date_to': fields.date('Date To', required=True),
	'report_type': fields.selection(REPORT_TYPE,'Report Type', select=True),
	'clearance_type': fields.selection(CLEARANCE_SELECTION,'Clearance Type', select=True),
	'Shipment':fields.selection(Ship_SELECTION, 'Shipment',select=True),
	'purpose':fields.selection(PURPOSE_SELECTION, 'Purpose',select=True),
    	'project_id':fields.many2one('hr.department', 'Projects', ),
    }
        
    _defaults = {
        'report_type' :'all',
                }  

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['Date_from','Date_to','report_type','clearance_type', 'Shipment','purpose', 'project_id'])[0]        
        if data['form']['report_type'] == 'all':
            print "llllllllllllllllllllllllllll"
            return { 'type': 'ir.actions.report.xml', 'report_name': 'clearance_report.report', 'datas': data}
        return { 'type': 'ir.actions.report.xml','report_name': 'clearance_report_done.report','datas': data }
clearance_report()
    
