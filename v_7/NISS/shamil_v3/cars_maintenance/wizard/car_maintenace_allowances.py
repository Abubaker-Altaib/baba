# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from osv import fields, osv
import time
from tools.translate import _
from collections import defaultdict

#----------------------------------------
#car maintenance allowances archive wiz
#----------------------------------------
class car_maint_allowances_archive_wiz(osv.osv_memory):

    _name = "car.maint.allowances.wiz"
    _description = "Car Maintenance Allowances Wizard"

    _columns = {
	    'company_id' : fields.many2one('res.company', 'Company',required=True),
            'dep':fields.many2one('hr.department', 'Department',required=True),
	    'date_from': fields.date("From", required= True),
	    'date_to' : fields.date("To" , required= True),
            'action_type':fields.selection([('compute','Compute'),('transfer','Transfer')],'Action Type'),
   		 }

    def compuete_allowances(self,cr,uid,ids,context={}):
       """
          Method that computes car Maintenace allowances per partner in specific company during  specific period of time.
          @return: Dictionary of values
       """
       maintenance_obj = self.pool.get('car.maintenance.request')
       maintenance_allowances_obj = self.pool.get('car.maintenance.allowances.archive')
       allowances_lines_obj = self.pool.get('car.maintenance.allowances.lines')
       sequence_obj = self.pool.get('ir.sequence')
       allow_archive_line_dict = {}  
       partner_dict = defaultdict(list)
       for record in self.browse(cr,uid,ids,context=context):
          maintenance_ids = maintenance_obj.search(cr,uid,[('company_id','=',record.company_id.id),('date','>=',record.date_from),('date','<=',record.date_to),('allowance_computed','=',False),('state','=','done')])
          if not maintenance_ids:
             raise osv.except_osv(_('Warning'), _("No Car Maintenance Request to compute in this period or already computed "))
          partner_res = maintenance_obj.read(cr, uid, maintenance_ids, ['partner_id'], context=context)
          for partner in partner_res:
              partner_id = partner['partner_id'][0]
              maitenance_id = partner['id']
              #This dictionary will contains partner_is as key and list of maitenance ids related with this partner as value
              partner_dict[partner_id].append(maitenance_id)
          for partner_id in partner_dict.keys():
               archive_name = sequence_obj.get(cr, uid, 'car.maintenance.archive')
               allow_archive_dict = {
                   'name' : archive_name,
                   'company_id' : record.company_id.id,
                   'partner_id' : partner_id,
                   'date' :time.strftime('%Y-%m-%d'),
                   'date_from': record.date_from,
                   'date_to': record.date_to,
                   'dep': record.dep.id,
                           }
               allow_archive_id = maintenance_allowances_obj.create(cr, uid, allow_archive_dict,context=context)
               maintenance_partner_ids = partner_dict[partner_id]
               for maintenance_record in maintenance_obj.browse(cr,uid,maintenance_partner_ids,context):
                    allow_archive_line_dict = {
                        'car_maintenance_allow_id' : allow_archive_id,
                        'department_id' :maintenance_record.department_id.id,
                        'request_id':maintenance_record.id,
                        'cost':maintenance_record.total_amount,
                        }
                    allowances_lines_obj.create(cr, uid, allow_archive_line_dict,context=context)
          maintenance_obj.write(cr,uid,maintenance_ids,{'allowance_computed':True,},context=context)
       return {}

    def create_ratification(self,cr,uid,ids,context={}):
       """
          Method that transfers company's untransfered car's maintenance allowance to account voucher during spesafic period of time.
          @return: Dictionary 
       """
       maintenance_allowances_obj = self.pool.get('car.maintenance.allowances.archive')
       allowances_ids = maintenance_allowances_obj.search(cr,uid,[('transfer','=',False)])
       if not allowances_ids:
           raise osv.except_osv(_('Warning'), _("No hospitality allowances to transfer, or already transfered "))
       maintenance_allowances_obj.action_create_ratification(cr,uid,allowances_ids,context)
       return {}



