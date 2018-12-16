# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

#----------------------------------------
# Class building insurance wizard
#----------------------------------------
class building_insurance_wizard(osv.osv_memory):

    _name = "building.insurance.wizard"
    _description = "Building insurance wizard"

    STATE_SELECTION = [
        ('completed', 'Completed orders'),
        ('incomplete', 'Incomplete orders'), ]

    _columns = {
        'date_from': fields.date('From', required=True,), 
        'date_to': fields.date('To', required=True),
        'building_id':fields.many2one('building.manager', 'Building'),
        'state': fields.selection(STATE_SELECTION,'State',), 
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'building.insurance',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'building_insurance.report',
            'datas': datas,
            }
building_insurance_wizard()
    
