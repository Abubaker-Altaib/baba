# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

#----------------------------------------
# Class building maintenance wizard
#----------------------------------------
class building_maintenance_wizard(osv.osv_memory):

    _name = "building.maintenance.wizard"
    _description = "Building maintenance wizard"

    STATE_SELECTION = [
        ('completed', 'Completed orders'),
        ('incomplete', 'Incomplete orders'), ]

    _columns = {
        'date_from': fields.date('From', required=True,), 
        'date_to': fields.date('To', required=True),
        'wizard_type': fields.selection([('by_building','By building'),('by_partner','By partner')],'Wizard type'),
        'maintenance_type':  fields.many2one('building.maintenance.type', 'Maintenance type'),
        'state': fields.selection(STATE_SELECTION,'State',), 
        'building_id':  fields.many2one('building.manager', 'Building',),
        'partner_id':fields.many2one('res.partner', 'Partner'),
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'building.maintenance',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'building_maintenance.report',
            'datas': datas,
            }
building_maintenance_wizard()
    
