# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv

class search_and_inform_report(osv.osv_memory):
    _name = "search.and.inform"
    _description = "Search And Inform Report"
    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
                     ]
    report_type = [
            ('init_request', 'Init Request'),
            ('quotes', 'Quotes'),
            ('fin_ratif_request', 'Finanicial Ratification Request'),
            ('purchase_order', 'Purchase Order'),

                      ]
    STATE = [
            ('in_progress','In Progress'),
            ('completed','Completed'),
            ('closed','Closed'),
            

                      ]
    _columns = {
        'from_date': fields.date('From', required=True,), 
        'to_date': fields.date('To', required=True),
        'department_id' : fields.many2one('hr.department','Department' ),
        'state' : fields.selection(STATE ,'State',select=True ),
        'company_id' : fields.many2one('res.company','Company' ,readonly=True),
        'with_childern' : fields.boolean( 'With Childern' , ),
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', readonly=True, select=True,help='Department Which this request will executed it'),
        'report_type' : fields.selection(report_type ,'Report Type ',select=True,required=True),


    }



    _defaults = {
                
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'search.and.inform', context=c),
                'executing_agency' : lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).belong_to ,
              }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'purchase.order',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'search_and_inform_report',
            'datas': datas,
            }

    
