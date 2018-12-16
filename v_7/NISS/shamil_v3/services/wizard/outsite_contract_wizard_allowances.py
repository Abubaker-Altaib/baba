# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields
import time
import netsvc
from datetime import timedelta,date , datetime
from admin_affairs.copy_attachments import copy_attachments as copy_attachments
from openerp.tools.translate import _
from collections import defaultdict
from base_custom import amount_to_text_ar


#----------------------------------------
#outsite_contract allowances _archive_wiz
#----------------------------------------
class outsite_contract_allowances_archive_wiz(osv.osv_memory):
    def _get_months(sel, cr, uid, context):
       months=[(str(n),str(n)) for n in range(1,13)]
       return months
    _name = "outsite.contract.allowances.archive.wiz"
    _columns = {
	    'company_id' : fields.many2one('res.company', 'Company',required=True),
        'department_id':fields.many2one('hr.department', 'Department',required=True,store=True),
        'month': fields.selection(_get_months,'Month', required=True),
	'year' :fields.integer("Year", size=8, required= True),
        'action_type':fields.selection([('compute','Compute'),('transfer','Transfer')],'Action Type'),
       'transfer':fields.boolean("Transfer"),

   		 }
    _defaults = {
        'year': int(time.strftime('%Y')),
        'transfer':False,
		}

    def main_arch(self,cr,uid,ids,context={}):
       """Compute employees salary in specific month.
       @return: Dictionary 
       """
       main_archive_obj = self.pool.get('outsite.contract.main.archive')
       employee_obj = self.pool.get('outsite.contract')
       sp_allow_obj= self.pool.get('contract.payroll.amount')
       allowns_dectuct_obj=self.pool.get('overtime.contract')
       partner_dict = defaultdict(list)
       for m in self.browse(cr,uid,ids):   
        check_salary = main_archive_obj.search(cr,uid,[('month','=',m.month),('year','=',m.year),('company_id','=',m.company_id.id)])
        if check_salary:
           raise osv.except_osv('ERROR', 'The Payroll For This Month Already Computed')
        emp_ids=employee_obj.search(cr,uid,[('service_terminated','!=',True),('company_id','=',m.company_id.id)])
        partner_res = employee_obj.read(cr, uid,emp_ids, ['partner_id'], context=context)
        for partner in partner_res:
              partner_id = partner['partner_id'][0]
              emp_id = partner['id']
              partner_dict[partner_id].append(emp_id)    
        vals={} 
        for partner_id in partner_dict.keys():
            emp_part_serrch=employee_obj.search(cr,uid,[('partner_id','=',partner_id),('company_id','=',m.company_id.id)])
            emp_obj=employee_obj.browse(cr,uid,emp_part_serrch)   
            for emp in emp_obj:
                   days= 0
                   overtime_mount=0.0
                   mission_mount=0.0
                   appsent_amount=0.0
                   allow_emp=sp_allow_obj.search(cr,uid,[('employee.id','=',emp.id),('month','=',m.month),('year','=',m.year)])                    
                   for k in allow_emp:    
                       over_all=sp_allow_obj.browse(cr,uid,k).overtime_name.id     
                       if over_all==1:
                           overtime_mount=sp_allow_obj.browse(cr,uid,k).gross_amount
                       elif over_all==2 :
                           mission_mount=sp_allow_obj.browse(cr,uid,k).gross_amount
                       elif over_all==3 :
                           appsent_amount=sp_allow_obj.browse(cr,uid,k).gross_amount
                   gross_mount=float(emp.job_id.total_amount+mission_mount+overtime_mount-appsent_amount)
                   vals={
                 'employee_id':emp.id,
                 'month' :m.month,
                 'year' :m.year,
                 'company_id' : m.company_id.id,
                 'partner_id' : partner_id,
                 'job_id' : emp.job_id.id,
                 'department_id' :m.department_id.id,
                 'dep_name' :emp.department_id.id,
                'total_allowance':overtime_mount,
                'total_mission': mission_mount,
                'appsent_amount': appsent_amount,
                'net':emp.job_id.total_amount,
                'gross':gross_mount,
                          }
                   main_archive_obj.create(cr,uid,vals)
       return vals
    def create_ratification(self,cr,uid,ids,context={}):
       """create ratification for Outsite contract allowances archive 
       @return: Dictionary 
       """
       partner_dict = defaultdict(list)
       emp_payrol=self.pool.get('outsite.contract.main.archive') 
       account_journal_obj = self.pool.get('account.journal')   
       account_obj = self.pool.get('account.account')
       voucher_obj = self.pool.get('account.voucher')
       voucher_line_obj = self.pool.get('account.voucher.line')
       affairs_account_obj = self.pool.get('admin_affairs.account') 
       affairs_model_obj = self.pool.get('admin.affairs.model') 
       for record in self.browse(cr, uid, ids, context=context):
           affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=','outsite.contract.main.archive')], context=context)
           affairs_account_ids = affairs_account_obj.search(cr, uid, [('model_id','=',affairs_model_ids[0])], context=context)
           if not affairs_account_ids:
                raise osv.except_osv(_('Error'), _("Please enter the Contract Outsite accounting configuration"))
           affairs_account = affairs_account_obj.browse(cr, uid, affairs_account_ids[0], context=context)
           account_ids = account_obj.search(cr, uid, [('company_id','=',record.company_id.id),('code','=',str(affairs_account.code))], context=context)
           journal_ids =  account_journal_obj.search(cr, uid, [('company_id','=',record.company_id.id),('name','=',affairs_account.name_type.name)], context=context)
           journal_id = journal_ids[0]
           account_id = account_ids[0]
           analytic_id = affairs_account.analytic_id 
           check_transfer_salary = self.search(cr,uid,[('month','=',record.month),('year','=',record.year),('company_id','=',record.company_id.id),('transfer','=',True)])
           if check_transfer_salary:
                raise osv.except_osv('ERROR', 'The Payroll For This Month Already Trasfered')
           employ_main_archive=emp_payrol.search(cr, uid, [('company_id','=',record.company_id.id),('year','=',record.year),('month','=',record.month)], context=context)
           partner_pay_res=emp_payrol.read(cr, uid,employ_main_archive, ['partner_id'], context=context)
           for partner in partner_pay_res:
               partner_id = partner['partner_id'][0]
               emp_id = partner['id']
               partner_dict[partner_id].append(emp_id) 
           for partner_id in partner_dict.keys():
               cr.execute('''SELECT 
  sum(oute.gross) as gros
FROM 
  public.outsite_contract_main_archive as oute, 
  public.res_partner as part
WHERE 
  oute.partner_id = part.id and oute.month=%s and oute.year=%s and
  part.id=%s ''',(record.month,record.year,partner_id))
               mount_partner = cr.dictfetchall()
               voucher_dict={
                                 'company_id':record.company_id.id,
                                 'department_id':record.department_id.id,
                                 'journal_id':journal_id , 
                                 'name': 'outsiteCOntract/Emp/'  + ' - ' + ' - ' ,
                                 'type':'ratification',
                                 'amount':mount_partner[0]['gros'],
                                 'reference':'outsiteCOntract/Emp/' ,
                                 'partner_id' : partner_id,
                                 'narration' : 'Outsie Contract Data: ',
                                 'amount_in_word':amount_to_text_ar(mount_partner[0]['gros']),
                     }
           
               voucher_id = voucher_obj.create(cr, uid, voucher_dict, context=context)
               cr.execute('''SELECT distinct 
  a.id,a.name, 
  sum(outsite.gross) as total
FROM 
  public.outsite_contract_main_archive as outsite, 
  public.hr_department as hr, 
  public.account_analytic_account as a,
  res_partner as part
WHERE 
  outsite.dep_name = hr.id AND outsite.partner_id=part.id and 
  hr.analytic_account_id = a.id and outsite.month=%s
  and outsite.year=%s and outsite.company_id=%s and part.id =%s
  GROUP BY a.id,a.name''',(record.month,record.year,record.company_id.id,partner_id))
               res = cr.dictfetchall()
               for line_id in res:
                   voucher_line_dict = {
                   'voucher_id':voucher_id,
                   'account_analytic_id':line_id['id'],
                   'amount':line_id['total'],
                   'type':'dr',
                   'name':line_id['name'],

                                 }
                   if account_id:
                      voucher_line_dict.update({'account_id':account_id })
                   voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
                   self.write(cr,uid,record.id,{'transfer':True},context=context)
           wf_service = netsvc.LocalService("workflow")
           wf_service.trg_validate(uid,'account.voucher',voucher_id, 'approve', cr)
           #voucher_obj.compute_tax(cr, uid,vouchers, context)
           copy_attachments(self,cr,uid,ids,'outsite.contract.main.archive',voucher_id,'account.voucher', context)
       return {}
 

