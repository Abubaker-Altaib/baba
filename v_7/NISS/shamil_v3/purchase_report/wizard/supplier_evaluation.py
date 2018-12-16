# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class supplier_evaluation(osv.osv_memory):
    _name = "supplier.evaluation"
    _description = "Suppliers evaluation"
    _columns = {

    'from_date' : fields.date('From' , required = True),
    'to_date' : fields.date('To' , required = True),

               }
    
    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'purchase.order',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'supplier_eval.report',
            'datas': datas,
            }
supplier_evaluation()


