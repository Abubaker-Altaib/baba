# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from openerp.osv import fields, osv, orm


class building_accident_wiz(osv.osv_memory):
    """
    To manage accident Report Class""" 

    _name = "building.accident.wiz"
    _description = "Building Accident Report"

    
    STATE_SELECTION = [('draft', 'Draft'),
			       ('confirm', 'Confirm '),
			       ('done', 'Done'),
			       ('cancel', 'Cancel'), ] 

    _columns = {
        'Date_from': fields.date('Date From', required=True,), 
        'Date_to': fields.date('Date To', required=True),
    	'building_id': fields.many2one('building.building','Building',),
    	'accident_type_id': fields.many2one('accident.type','Accident Type',),
        'state': fields.selection(STATE_SELECTION,'State',select=True),
	'partner_id':fields.many2one('res.partner','Partner'),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
    }
    _defaults = {
 		'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).company_id.id,
                }

    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'building.accident',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'building_accident.report',
            'datas': datas,
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
