# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv

class foreigner_details_wiz(osv.osv_memory):
    """
    To manage Details Report """

    _name = "foreigner.details.wiz"
    _description = "Foreigner Details Report Class"


    _columns = {
        'Date_from': fields.date('Date From', required=True,), 
        'Date_to': fields.date('Date To', required=True),
    	'company_id':fields.many2one('res.partner', 'Company',),
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'public.relation.foreigners',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'foreigner_details.report',
            'datas': datas,
            }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
    
