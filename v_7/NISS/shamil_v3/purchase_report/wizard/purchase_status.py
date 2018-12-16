# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class purchase_status(osv.osv_memory):
    _name = "purchase.status"
    _description = "Purchase Status wizard"
    _columns = {
        'from_date': fields.date('Date From', required=True,), 
        'to_date': fields.date('Date To', required=True), 
        'department': fields.many2one('hr.department', 'Department',required=True),
        'type' : fields.selection([('internal','Internal'),('foreign','Foreign')],'Type'),
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [])[0]
        datas = {
             'ids': [],
             'model': 'purchase.order',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'purchase_status.report',
            'datas': datas,
            }
purchase_status()


