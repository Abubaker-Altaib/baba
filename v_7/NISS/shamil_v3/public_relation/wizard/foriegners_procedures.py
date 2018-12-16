# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
import time
import datetime

procedures=[
           ('1','Foriegners Visa'),
	    ]

class foriegners_procedures_wiz(osv.osv_memory):
   """
   To manage foriegners procedures wizard """

   _name="foriegners.procedures.wiz"
   _columns = {
          'procedure':fields.selection(procedures,'Procedure',  required=True),
       }

   def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'foreigners.procedures.request',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            #'report_name': 'foriegners.procedures',
            'datas': datas,
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
 

