# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2013-2014 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
import netsvc
import time
import datetime
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from admin_affairs.copy_attachments import copy_attachments as copy_attachments
from openerp.tools.amount_to_text_en import amount_to_text
from base_custom.amount_to_text_ar import amount_to_text as amount_to_text_ar

#----------------------------------------
# Class car maintenance allowances archive
#----------------------------------------
class car_maintenance_allowances_archive(osv.Model):

    def create(self, cr, user, vals, context=None):
        """
           Create new sequence for every car maintenance as a name.
           @param cr: Cursor to database
           @param user: Id of current user
           @param vals: Dictionary of the entered data
           @param context: Context arguments, like lang, time zone
           @return: Super create method
        """
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'car.maintenance.archive')
        return super(car_maintenance_allowances_archive, self).create(cr, user, vals, context)
    
    def _amount_all(self, cr, uid, ids,field_name, arg, context={}):
        """ 
           Functional field function to computes the total cost of maintenance.
           @param field_name: list contains name of fields that call this method
           @param arg: extra arguement
           @return: Dictionary of values
        """
        res={}
        for record in self.browse(cr, uid, ids, context=context):
            val = 0.0
            for line in record.allowances_lines:
                val += line.cost
            res[record.id] = val 
        return res
    

    def _get_months(self, cr, uid, context):
        """ 
           Functional field function to read and returns monthes as list of tuple.
           @return: List of tuple
        """
        months=[(str(n),str(n)) for n in range(1,13)]
        return months

    def _get_archive_ids(self, cr, uid, ids, context=None):
        """ 
           Method that returns ids of car.maintenance.allowances.lines (if changing happend to them) to the associated
           car.maintenance.allowances.archive in order to re-calculate maintenance cost.
           @return: List of ids
        """
        result = {}
        allowances_lines_obj=self.pool.get('car.maintenance.allowances.lines')
        for line in allowances_lines_obj.browse(cr, uid, ids, context=context):
            result[line.car_maintenance_allow_id.id] = True
        return result.keys()

    _name = "car.maintenance.allowances.archive"
    _description = 'Car maintenance allowances archive'
    _columns = {
        'name':fields.char('Reference', size=64, required=True, select=True, readonly=True  , help="unique number of the car maintenance allowances archive"),
        'date_from' :fields.date('From date',readonly=True),
        'dep': fields.many2one('hr.department','Dep'),
        'date_to' :fields.date('To date',readonly=True),
        'partner_id':fields.many2one('res.partner', 'Partner',readonly=True),
        'department_id': fields.related('allowances_lines', 'department_id',readonly=True, type='many2one', relation='hr.department', string='Department'),
        'date' :fields.date('Date',readonly=True),
        'total_amount': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string='Total amount',
            store ={
                'car.maintenance.allowances.archive': (lambda self, cr, uid, ids, c={}: ids, ['allowances_lines'], 10),
                'car.maintenance.allowances.lines': (_get_archive_ids, ['cost'], 10),  
                    }),
        'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
        'allowances_lines': fields.one2many('car.maintenance.allowances.lines', 'car_maintenance_allow_id' , 'Archive line', readonly=True),
        'transfer': fields.boolean('Transfer',readonly=True),
        #'voucher_no': fields.many2one('account.voucher', 'Voucher Number',readonly=True),
        'account_voucher_ids': fields.many2many('account.voucher', 'maitenance_voucher', 'maintain_id', 'voucher_id', 'Account voucher',readonly=True),
               }
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                }

    def unlink(self, cr, uid, ids, context=None):
        """ 
           Method that overwrites unlink method to prevent the deletion of transfered maintenance records 
           and creates log message to the deleted record.
           @return: Super unlink method.
        """
        allowances_archive = self.read(cr, uid, ids, ['transfer'], context=context)
        unlink_ids = []
        for record in allowances_archive:
            if record['transfer'] == False:
                unlink_ids.append(record['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('Sorry you can not Delete this record(s), Because it already transfered to account voucher!'))
        for id in unlink_ids:
            allowances_archive_name = self.browse(cr, uid, id, context=context).name
            message = _("Car maintenance allowances archive '%s' has been deleted.") % allowances_archive_name
            self.log(cr, uid, id, message)
        return super(car_maintenance_allowances_archive, self).unlink(cr, uid, unlink_ids, context=context)


    def action_create_ratification(self,cr,uid,ids,context={}):
       """ 
           Method to create account voucher ratification for maintenance amount.
           @return: Boolean True.
       """

       maitenance_allowances_obj = self.pool.get('car.maintenance.allowances.archive')
       voucher_obj = self.pool.get('account.voucher')
       voucher_line_obj = self.pool.get('account.voucher.line')
       affairs_account_obj = self.pool.get('admin_affairs.account')
       affairs_model_obj = self.pool.get('admin.affairs.model') 
       for record in self.browse(cr,uid,ids,context=context):
           ar_mount_manag=0.00
           ar_mount_proj=0.00
           sum_list=0.00
           ar_total_pro=0.00
           list1=[]
           if record.transfer:
             raise osv.except_osv(_('Warning'), _("This archive already transfered to the accounting"))
           model_id = affairs_model_obj.search(cr, uid, [('model','=','car.maintenance')], context=context)[0]          
           affairs_account = affairs_account_obj.search(cr, uid, [('model_id','=',model_id)], context=context) 
           if not affairs_account:
              raise osv.except_osv(_('Error'), _("Please enter the Car Maitenance accounting configuration"))
           affairs_account = affairs_account_obj.browse(cr, uid,affairs_account[0] ,context=context)
           journal_id = affairs_account.journal_id
           account_id = affairs_account.account_id and affairs_account.account_id.id
           analytic_id = affairs_account.analytic_id and affairs_account.analytic_id.id
           
	   cr.execute( 'SELECT sum(l.cost) as cost, a.project,a.id '\
                    'FROM car_maintenance_allowances_lines l '\
                    'left join hr_department h on (h.id=l.department_id) '\
                    'left join account_analytic_account a on (h.analytic_account_id = a.id) '\
                    'where l.car_maintenance_allow_id=%s '\
                    'GROUP BY a.id, a.project', (record.id,))
           res =  cr.dictfetchall()
	   ar_mount=0
           for ar in res:
               
               if ar['project']==True:
                  ar_mount_proj+=ar['cost']
                  list1.append(ar_mount_proj)
                  for lis2 in list1:
                      ar_total_pro=lis2
               else:
                  ar_mount_manag+=ar['cost']
                  ar_total=ar_mount_manag
           voucher_dict={
                                 'company_id':record.company_id.id,
                                 'name': 'Maintenance/CMA/' + ' - ' + str(record.date_from) + ' - ' + str(record.date_to),
                                 'type':'ratification',
                                 'reference':'Maintenance/CMA/' ,
                                 'partner_id' : record.partner_id.id,
                                 'account_id' : record.partner_id.property_account_payable.id,
                                 'narration' : 'Car Maintenace Allowances No:  ' + record.name ,
                                 #'amount_in_word':amount_to_text_ar(ar_total),
				 'department_id':record.dep.id,
                     }
	   voucher_id = False
           pro_voucher_id = False
           vouchers = []
           #voucher_id = voucher_obj.create(cr, uid, voucher_dict, context=context)
           for line in res:
               if not account_id and not line.request_id.category_id.account_id:
                  raise osv.except_osv(_('Error'), _("Please enter the Car Maitenance accounting configuration"))

               if line['project'] and not pro_voucher_id:
                   if not affairs_account.pro_account_id or not affairs_account.pro_journal_id:
                       raise osv.except_osv(_('Warning !'), _('Please insert Journal or Account For Car Maitenance'))
                   voucher_dict.update({'journal_id':affairs_account.pro_journal_id.id})
                   voucher_dict.update({'amount_in_word':amount_to_text_ar(ar_total_pro)})
                   pro_voucher_id = voucher_obj.create(cr, uid, voucher_dict, context=context)  
                   vouchers.append(pro_voucher_id)

               if not line['project'] and not voucher_id:
                   if not affairs_account.account_id or not affairs_account.journal_id:
                       raise osv.except_osv(_('Warning !'), _('Please insert Journal or Account For Car Maitenance'))
                   voucher_dict.update({'journal_id':affairs_account.journal_id.id})
                   voucher_dict.update({'amount_in_word':amount_to_text_ar(ar_total)})
                   voucher_id = voucher_obj.create(cr, uid, voucher_dict, context=context)    
                   vouchers.append(voucher_id)
               voucher_line_dict = {
                   'voucher_id':line['project'] and pro_voucher_id or voucher_id,
                   'account_analytic_id':line['id'],
                   'account_id':line['project'] and affairs_account.pro_account_id.id or affairs_account.account_id.id,    
                   'amount':line['cost'],
                   'type':'dr',
                   'name':'Name',
                   
                               }
               voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
		
		# Selecting Voucher Number / Refernece 

               #voucher_number = self.pool.get('account.voucher').browse(cr,uid,voucher_id)
           
           voucher_obj.compute_tax(cr, uid,vouchers, context)
           ####################workflow state###############
           voucher_state = 'draft'
           if record.company_id.affairs_voucher_state : 
                voucher_state = record.company_id.affairs_voucher_state 
           if voucher_id:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'account.voucher',voucher_id, voucher_state, cr)
                voucher_obj.write(cr, uid, voucher_id, {'type':'ratification','ratification':True,'state':voucher_state}, context)
           if pro_voucher_id:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'account.voucher',pro_voucher_id, voucher_state, cr)
                voucher_obj.write(cr, uid, pro_voucher_id, {'type':'ratification','ratification':True,'state':voucher_state}, context) 
           ####################################3           
           copy_attachments(self,cr,uid,[record.id],'car.maintenance.allowances.archive',voucher_id,'account.voucher', context)
           cr.execute('insert into maitenance_voucher (maintain_id,voucher_id) values(%s,%s)',(record.id,voucher_id))
           maitenance_allowances_obj.write(cr, uid, record.id,{'transfer':True} ,context=context)
       return True



#----------------------------------------
# Class car_maintenance allowances lines
#----------------------------------------
class car_maintenance_allowances_lines(osv.Model):
    _name = "car.maintenance.allowances.lines"
    _description = 'Car Maintenance Allowances Lines'
    _columns = {
        'car_maintenance_allow_id':fields.many2one('car.maintenance.allowances.archive', 'Allowances archive',readonly=True),
        'cost':fields.float('cost',digits=(18,2),readonly=True),
        'department_id': fields.many2one('hr.department', 'Department',readonly=True),
        'partner_id':  fields.related('car_maintenance_allow_id', 'partner_id', type='many2one', relation='res.partner',readonly=True, string='Partner'),
        'request_id': fields.many2one('car.maintenance.request', 'Request No',required=True,readonly=True),
        'car_id': fields.related('request_id', 'car_id', type='many2one', relation='fleet.vehicle',readonly=True, string='Car'),
        'name': fields.text('Note', size=256),
                    }


