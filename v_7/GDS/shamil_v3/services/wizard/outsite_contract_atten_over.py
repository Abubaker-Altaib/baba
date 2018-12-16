# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from openerp.osv import osv, fields
import time

class out_attent_over_wiz(osv.osv_memory):

    _name = "out.attent.over.wiz"
    _description = "Outsite Contract Attent Over Report"

    def _get_months(self, cr, uid, context):
       months=[(str(n),str(n)) for n in range(1,13)]
       return months

    _columns = {
        'month': fields.selection(_get_months,'Month', select=True,required=True),
        'year': fields.integer('Year', size=32,required=True),
        'partner_id':fields.many2one('res.partner','Partner',required=True),
        'select_type':fields.selection([('attent','الحضور والغياب'),('over_time','الاجر الاضافى و المامؤريات'),('all_ratfi','مطالبات شركة المتعاقد معها ')],'Select Type',required=True),
        'all_company':fields.many2many('res.company','out_company_rel' ,'comp_id' ,'out_id','All Company Contarct',),
        'ref':fields.reference(selection=[('res.company', 'Company'), ('hr.department', 'Department')], string="Reference", size=32),
        'amount_print':fields.boolean('Amout Print'),

        
    }
    _defaults = {
        'year': int(time.strftime('%Y')),
        'amount_print':False
                }

    def print_report(self, cr, uid, ids, data, context=None):
        wiz_data =self.read(cr, uid, ids[0], context={})
        datas = {
            'ids': [],
            'model':'outsite.contract',
            'form':wiz_data
                }
        if wiz_data['select_type']=='attent' :
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name':'print.emps.names.attent',
                    'datas':datas,
                     }
        elif wiz_data['select_type']=='over_time' :
               return {
                    'type': 'ir.actions.report.xml',
                    'report_name':'print.emps.names.overtime',
                    'datas':datas,
                     }
        elif wiz_data['select_type']=='all_ratfi':
               return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'print.out.multi.company',
                    'datas':datas,
                     }

out_attent_over_wiz()
    
