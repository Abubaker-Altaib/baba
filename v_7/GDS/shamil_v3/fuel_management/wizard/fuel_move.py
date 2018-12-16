# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from osv import fields, osv


# fuel Fuel Move  wizard report for Specific period of  Time

class fuel_move_wizard(osv.osv_memory):
    """
    To manage fule move """

    _name = "fuel.move.wiz"

    _columns = {
        'Date_from': fields.date('Date From', required=True,), 
        'Date_to': fields.date('Date To', required=True),
        'location_id':fields.many2one('stock.location', 'Location',required=True),
       
           }

    def print_report(self, cr, uid, ids, context=None):
        """
        To print the report.

        @return: print the report
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'stock.move',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'fuel_move.report',
            'datas': datas,
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
