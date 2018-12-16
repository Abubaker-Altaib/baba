# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class clearance_report_niss_all(osv.osv_memory):
    _name = "clearance.report.niss.all"
    _description = "Clearance Report Niss All"
    DELIVERY_SELECTION = [
        ('air_freight', 'Air Freight'),
        ('sea_freight', 'Sea Freight'),
        ('free_zone','Free Zone'),
        ('land_freight', 'Land Freight'),
        ('halfa','Halfa'),
                         ]
                     
    
    _columns = {
        'from_date': fields.date('From', required=True,), 
        'to_date': fields.date('To', required=True),
        'category_id' : fields.many2one('items.category','Category' ),
        'transporter_id' : fields.many2one('transporter.companies','Transporter' ),
        'department_id' : fields.many2one('hr.department','Department' ),
        'ship_method':fields.selection(DELIVERY_SELECTION,'Bill By' ),
        'company_id' : fields.many2one('res.company','Company' ,readonly=True),
        

    }



    _defaults = {
                
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'clearance.report.niss.all', context=c),
                
              }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'purchase.clearance',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'clearance_report_niss_all',
            'datas': datas,
            }

    
