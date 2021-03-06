# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class building_maintenance_wizard(osv.osv_memory):
    """
     To manage building maintenance wizard """

    _name = "building.maintenance.wizard"
    _description = "Building maintenance wizard"

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done')]

    _columns = {
        'date_from': fields.date('From', required=True,), 
        'date_to': fields.date('To', required=True),
        'wizard_type': fields.selection([('by_building','By building'),('by_partner','By partner')],'Wizard type'),
        'maintenance_type':  fields.many2one('building.maintenance.type', 'Maintenance type'),
        'state': fields.selection(STATE_SELECTION,'State',), 
        'building_id':  fields.many2one('building.building', 'Building',),
        'partner_id':fields.many2one('res.partner', 'Partner'),
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
    
