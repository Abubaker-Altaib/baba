# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv, fields
import time
from openerp.tools.translate import _
from collections import defaultdict

#----------------------------------------
#hospitality_allowances_archive_wiz
#----------------------------------------
class hospitality_allowances_archive_wiz(osv.osv_memory):

    _name = "hospitality.allowances.archive.wiz"
    _description = "Hospitality Allowances Archive Wizard"

    _columns = {
	    'company_id' : fields.many2one('res.company', 'Company',required=True),
            'departments':fields.many2one('hr.department', 'Department',required=True),
	    'date_from': fields.date("From", required= True),
	    'date_to' : fields.date("To" , required= True),
            'action_type':fields.selection([('compute','Compute'),('transfer','Transfer')],'Action Type'),
   		 }

    def compuete_allowances(self,cr,uid,ids,context={}):
       """Compute hospitality service allowances per partner in specific company during specific period of time .
       @return: Dictionary 
       """
       dept = ""
       service_type = ""
       total_cost = ""
       hospitality_obj = self.pool.get('hospitality.service')
       hospitality_allowances_obj = self.pool.get('hospitality.allowances.archive')
       allowances_lines_obj = self.pool.get('hospitality.allowances.lines')
       sequence_obj = self.pool.get('ir.sequence')
       allow_archive_line_dict = {}  
       partner_dict = defaultdict(list)
       for record in self.browse(cr,uid,ids,context=context):
          hospitality_ids = hospitality_obj.search(cr,uid,[('company_id','=',record.company_id.id),('date_of_execution','>=',record.date_from),('date_of_execution','<=',record.date_to),('allowance_computed','=',False),('state','=','done')])
          if not hospitality_ids:
             raise osv.except_osv(_('Warning'), _("No hospitality services to compute in this period or already computed "))
          partner_res = hospitality_obj.read(cr, uid, hospitality_ids, ['partner_id'], context=context)
          for partner in partner_res:
              partner_id = partner['partner_id'][0]
              hospitality_id = partner['id']
              #This dictionary will contains partner_is as key and list of hospitality ids related with this partner as value
              partner_dict[partner_id].append(hospitality_id)
          for partner_id in partner_dict.keys():
               archive_name = sequence_obj.get(cr, uid, 'hospitality.allowances.archive')
               allow_archive_dict = {
                   'name' : archive_name,
                   'company_id' : record.company_id.id,
                   'departments' : record.departments.id,
                   'partner_id' : partner_id,
                   'date' :time.strftime('%Y-%m-%d'),
                   'date_from': record.date_from,
                   'date_to': record.date_to,
                           }
               allow_archive_id = hospitality_allowances_obj.create(cr, uid, allow_archive_dict,context=context)
               hospitality_partner_ids = partner_dict[partner_id]
	       cr.execute("""SELECT distinct s.department_id as dept from hospitality_service s  where s.partner_id =%s and (s.date_of_execution >= %s and date_of_execution <= %s) """,(partner_id,record.date_from,record.date_to))
	       dept_res=cr.dictfetchall()
	       for service in dept_res :
		cr.execute("""SELECT distinct s.department_id as dept , o.service_type as service_type , sum(o.service_cost * 1) as total from order_lines o left join hospitality_service s on (o.order_id = s.id) where s.partner_id =%s and s.department_id=%s and (s.date_of_execution >= %s and date_of_execution <= %s) GROUP BY s.department_id,o.service_type""",(partner_id,service['dept'],record.date_from,record.date_to))
	       	service_res=cr.dictfetchall()
	        for line in service_res :
			allow_archive_line_dict = {
                        		'hospitality_allow_id' : allow_archive_id,
                        		'department_id' :line['dept'],
                        		'hospitality_service_type':line['service_type'],
                        		'amount':line['total'],
                        }
                	allowances_lines_obj.create(cr, uid, allow_archive_line_dict,context=context)
          #hospitality_obj.write(cr,uid,hospitality_ids,{'allowance_computed':True,},context=context)


       return {}

    def create_ratification(self,cr,uid,ids,context={}):
       """Transfers hospitality  service allowances amount to account voucher.
       @return: Dictionary 
       """
       hospitality_obj = self.pool.get('hospitality.service')
       for record in self.browse(cr,uid,ids,context=context):
           hospitality_ids = hospitality_obj.search(cr,uid,[('company_id','=',record.company_id.id),('date','>=',record.date_from),('date','<=',record.date_to),('allowance_computed','=',False),('state','=','done')])
       hospitality_allowances_obj = self.pool.get('hospitality.allowances.archive')
       allowances_ids = hospitality_allowances_obj.search(cr,uid,[('transfer','=',False)])
       if not allowances_ids:
           raise osv.except_osv(_('Warning'), _("No hospitality allowances to transfer, or already transfered "))
       hospitality_allowances_obj.action_create_ratification(cr,uid,allowances_ids,context)
       hospitality_obj.write(cr,uid,hospitality_ids,{'allowance_computed':True,},context=context)

       return {}

hospitality_allowances_archive_wiz()

