# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
import time
from openerp.tools.translate import _
from openerp import netsvc



class custody_report(osv.osv_memory):
    """ 
    Class to Print Custodies From wizard """

    _description='Print Custodies From wizard'
    _name = 'custody.report'
    _columns = {
                'department_id' : fields.many2one('hr.department','Department',),
                'type' : fields.selection([('in_stock','Custody In stock'),('in_user','Custody In User')],  'Type' , required=True,),
                'with_childern' : fields.boolean('With Childern') ,         

                }
    
    
    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'custody.custody',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'custody_report',
            'datas': datas,
            }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
