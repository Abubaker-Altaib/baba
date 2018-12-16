# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from osv import fields, osv


# building accident Report Class

class building_accident_wiz(osv.osv_memory):

    _name = "building.accident.wiz"
    _description = "Building Accident Report"

    CATEGORY_SELECTION = [
    ('car', 'Cars'),
    ('building', 'Building '),
    ('station', 'Station'),
    ('other', 'Other'), ]

    STATE_SELECTION = [
    ('draft', 'Draft'),
    ('section', 'Waiting for service section manager to confirm '),
    ('approve', 'Waiting for Insurance section manager to confirm '),
    ('done', 'Done'),
    ('cancel', 'Cancel'), 
    ]    

    _columns = {
        'Date_from': fields.date('Date From', required=True,), 
        'Date_to': fields.date('Date To', required=True),
    	'building_id': fields.many2one('building.manager','Building',),
        'station_id': fields.many2one('building.manager','Station',),
        'car_id': fields.many2one('fleet.vehicles','Car'),
    	'accident_type_id': fields.many2one('accident.type','Accident Type',),
        'accident_category': fields.selection(CATEGORY_SELECTION,'Category', select=True),
        'state': fields.selection(STATE_SELECTION,'State',select=True),
	'partner_id':fields.many2one('res.partner','Partner'),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
    }
    _defaults = {
 		'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).company_id.id,
                }

    def print_report(self, cr, uid, ids, context=None):
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
building_accident_wiz()
    
