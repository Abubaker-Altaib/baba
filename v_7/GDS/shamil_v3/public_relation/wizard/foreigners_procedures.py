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
copies=[
           ('1','GM'),
           ('2','GM agent'),
           ('3','PRM Section Manager'),
           ('4','genral Manager for human resource and finical'),
           ('5','genral Manager for human resource and finical - Ministry'),
	    ]

class foreigners_procedures_wiz(osv.osv_memory):
   """
   To manage foreigners procedures wizard """

   _name="foreigners.procedures.wiz"
   _columns = {
          'procedure':fields.many2one('foreigners.procedures','Procedure', readonly=True),
          'copy_to':fields.selection(copies,'Copy To',  required=True),
       }

   def default_get(self, cr, uid, fields, context=None):
        """ 
        To get default values for the object.

        @param fields: List of fields for which we want default values
        @param context: A standard dictionary
        @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}
        res ={}
        result = []
	fore_req = self.pool.get('foreigners.procedures.request').browse(cr,uid,context['active_id'])
        res.update({'procedure': fore_req.procedure_id.id})
        return res

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
            'report_name': 'foreigners.procedures',
            'datas': datas,
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
