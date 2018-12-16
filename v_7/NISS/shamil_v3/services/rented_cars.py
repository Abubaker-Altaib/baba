# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp.osv import osv, fields
import time
import datetime
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import netsvc
from admin_affairs.copy_attachments import copy_attachments as copy_attachments
from tools.amount_to_text_en import amount_to_text
from base_custom import amount_to_text_ar



#----------------------------------------
# Class rented cars
#----------------------------------------
class rented_cars(osv.osv):
    
    def create(self, cr, user, vals, context=None):
        """
        Create new entry sequence for every Rented Cars
        @param cr: cursor to database
        @param user: id of current user
        @param vals: list of record to be approved
        @param context: context arguments, like lang, time zone
        @return: return a result 
          """
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'rented.cars')
        return super(rented_cars, self).create(cr, user, vals, context)
    
    def copy(self, cr, uid, id, default=None, context=None):
        """ Override copy function to edit sequence """
        if default is None:
            default = {}
        if context is None:
            context = {}
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'rented.cars'),
            
        })
        return super(rented_cars, self).copy(cr, uid, id, default, context)    


    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        
        """ This Function compute the amount of line either with taxes or without taxes '''

        :param self : object pointer
        :param cr : database cursor
        :param total_with_tax :  Total with taxes
        :param total_without_taxes :  Total without taxes 
        :return returns: {
                'amount_untaxed': 0.0,                 
                'amount_tax': 0.0,                     
                'amount_total': 0.0,           
                 }
        """
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = {
                'amount_untaxed': 0.0, 
                'amount_tax': 0.0, 
                'amount_total': 0.0, 
            }
            total_with_tax = total_without_taxes = 0.0
            total_without_taxes += obj.cost_of_rent

            for tax in self.pool.get('account.tax').compute_all(cr, uid, obj.taxes_id, obj.cost_of_rent,1)['taxes']:
                    unit_tax= tax.get('amount', 0.0)
                    total_with_tax += unit_tax                
            res[obj.id] = {
                'amount_tax':total_with_tax, 
                'amount_untaxed':total_without_taxes, 
                'amount_total':total_with_tax + total_without_taxes
            }
        return res

    STATE_SELECTION = [
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('cancel', 'Cancel'), 
    ]
    COST_RATE = [
    ('per_day', 'Per Day'),
    ('per_month', 'Per Month'),
    ]
    _name = "rented.cars"
    _description = 'Rented Cars'
    _columns = {
    'name':fields.char('Reference', size=64, required=True, select=True, readonly=True  , help="unique number of the Rented Cars"),
    'date' :fields.date('Date of request',readonly=True),
    'department_id':  fields.related('car_id', 'department_id', type='many2one',readonly=True  , relation='hr.department',store=True, string='Department'),
    'employee_id': fields.many2one('hr.employee', 'Employee',),
    'partner_id':fields.many2one('res.partner', 'Partner',required=True,),
    'car_id': fields.many2one('fleet.vehicle', 'Car Name',required=True,domain="[('ownership','=','rented')]"),
    'car_number': fields.related('car_id', 'license_plate', type='char', relation='fleet.vehicle', string='Car Number', readonly=True,),    
    'date_of_rent':fields.date('Date of Rent',required=True ),
    'date_of_return':fields.date('Date of Retrieved',required=True ),
    'cost_of_rent': fields.float('Cost of Rent',digits=(16, 4)), 
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True , ),    
    'notes': fields.text('Notes', size=256 ),
    'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),    
    'cost_rate': fields.selection(COST_RATE,'Cost Rate'),        
    'rented_request_id': fields.many2one('rented.cars.request','Rent Details',invisible=1,readonly=1, help="It referes to Rented Cars Details from which Rented Request created."),
    'taxes_id': fields.many2many('account.tax', 'rented_car_tax', 'rented_id', 'tax_id', 'Taxes'), 
    'amount_untaxed': fields.function(_amount_all, method=True, string='Untaxed Amount',
        store={
            'rented.cars': (lambda self, cr, uid, ids, c={}: ids, ['taxes_id','cost_of_rent'], 10), 
            }, multi="sums", help="The amount without tax"), 
    'amount_tax': fields.function(_amount_all, method=True, string='Taxes', 
        store={
            'rented.cars': (lambda self, cr, uid, ids, c={}: ids, ['taxes_id','cost_of_rent'], 10), 
            }, multi="sums", help="The tax amount"), 
    'amount_total': fields.function(_amount_all, method=True, string='Total',
        store={
               'rented.cars': (lambda self, cr, uid, ids, c={}: ids, ['taxes_id','cost_of_rent'], 10), 
            }, multi="sums"), 

               
    }
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Rented Cars Reference must be unique !'), 
                        
        ]
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                'user_id': lambda self, cr, uid, context: uid,                
                'date': time.strftime('%Y-%m-%d'),
                'date_of_rent': time.strftime('%Y-%m-%d'),
                'date_of_return': time.strftime('%Y-%m-%d'),
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'rented.cars', context=c),
                'cost_of_rent':0.0,
                'amount_total':0.0,
                'state': 'draft',
                
                }
    
    
    def rewite_total(self,cr,uid,ids,context=None):
        
        for b in self.browse(cr,uid,ids,context=context):
             c=b.cost_of_rent
        self.write(cr, uid, ids, {'amount_total':c})
        return True

    def write_scheduler(self, cr, uid, ids=None, use_new_cursor=False, context=None):
        """Scheduler to check the status of car periodically 
        @return True
        """
        date=time.strftime('%Y-%m-%d')
        record = self.search(cr,uid,[('date_of_return','<',date),('state','=','confirmed')])
        if record:
            for car in self.browse(cr,uid,record):
                self.pool.get('fleet.vehicle').write(cr, uid,car.car_id.id ,{'status':'inactive'})
        return True

#workflow function
    def confirmed(self, cr, uid, ids, context=None):             
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True
    
    def cancel(self, cr, uid, ids, notes='', context=None):
        # Cancel the Rented car 
        notes = ""
        u = self.pool.get('res.users').browse(cr, uid,uid).name
        notes = notes +'\n'+'Rented Cars Request Cancelled at : '+time.strftime('%Y-%m-%d') + ' by ' +u  
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        # Reset the Monitoring Press to draft 
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
            self.write(cr, uid, s_id, {'state':'draft'})
            wf_service.trg_delete(uid, 'rented.cars', s_id, cr)            
            wf_service.trg_create(uid, 'rented.cars', s_id, cr)
        return True



   


#----------------------------------------
# Class rented cars allowances archive
#----------------------------------------
class rented_cars_allowances_archive(osv.osv):

    def create(self, cr, user, vals, context=None):
        """
        Create new entry sequence for every Rented Cars
        @param cr: cursor to database
        @param user: id of current user
        @param vals: list of record to be approved
        @param context: context arguments, like lang, time zone
        @return: return a result 
          """
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'rented.cars.allowances.archive')
        return super(rented_cars_allowances_archive, self).create(cr, user, vals, context)
    

    def _amount_all(self, cr, uid, ids,field_name, arg, context={}):
        """ Finds the the total of amount_untaxed,amount_tax  and amount_total.
        @param field_name: list contains name of fields that call this method
        @param arg: extra arguement
        @return: Dictionary of values
        """
        res={}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = { 'amount_untaxed': 0.0, 'amount_tax': 0.0, 'amount_total': 0.0}
            amount_untaxed = 0.0
            amount_tax = 0.0
            amount_total = 0.0
            for line in record.allowances_lines:
                amount_untaxed += line.amount_untaxed
                amount_tax += line.amount_tax
                amount_total += line.amount_total
            res[record.id]['amount_untaxed'] = amount_untaxed 
            res[record.id]['amount_tax'] = amount_tax 
            res[record.id]['amount_total'] = amount_total 
        return res
    

    def _get_months(self, cr, uid, context):
       months=[(str(n),str(n)) for n in range(1,13)]
       return months

    def _get_archive_ids(self, cr, uid, ids, context=None):
        result = {}
        allowances_lines_obj=self.pool.get('rented.cars.allowances.lines')
        for line in allowances_lines_obj.browse(cr, uid, ids, context=context):
            result[line.rented_cars_allow_id.id] = True
        return result.keys()

    _name = "rented.cars.allowances.archive"
    _description = 'Rented cars Allowances Archive'
    _columns = {
 	'name':fields.char('Reference', size=64, required=True, select=True, readonly=True  , help="unique number of the Rented Cars allowances archive"),
        'month': fields.selection(_get_months,'Month', readonly=True, select=True),
        'year': fields.integer('Year', size=64,readonly=True),
	    'partner_id':fields.many2one('res.partner', 'Partner',readonly=True),
	    'department_id': fields.related('allowances_lines', 'department_id',readonly=True, type='many2one', relation='hr.department', string='Department'),
        'dep': fields.many2one('hr.department','Dep'),
        'date' :fields.date('Archive date',readonly=True),
        'amount_untaxed': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string='Untaxed amount',
            store ={
                'rented.cars.allowances.archive': (lambda self, cr, uid, ids, c={}: ids, ['allowances_lines'], 10),
                'rented.cars.allowances.lines': (_get_archive_ids, ['amount_untaxed'], 10),  
                    }, multi='all'),

	    'amount_tax': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string='Taxes',
            store ={
                'rented.cars.allowances.archive': (lambda self, cr, uid, ids, c={}: ids, ['allowances_lines'], 10),
                'rented.cars.allowances.lines': (_get_archive_ids, ['amount_tax'], 10),  
                    }, multi='all'),
        'amount_total': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Account'), string='Total',
            store ={
                'rented.cars.allowances.archive': (lambda self, cr, uid, ids, c={}: ids, ['allowances_lines'], 10),
                'rented.cars.allowances.lines': (_get_archive_ids, ['amount_total'], 10),  
                    }, multi='all'),
        'company_id': fields.many2one('res.company','Company',required=True,readonly=True),
	    'allowances_lines': fields.one2many('rented.cars.allowances.lines', 'rented_cars_allow_id' , 'Archive line', readonly=True),
        'transfer': fields.boolean('Transfer',readonly=True),
               }
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                
                }

    def unlink(self, cr, uid, ids, context=None):
        """delete the rented cars allowances archive if record in draft or cancel state,
        and create log message to the deleted record
        @return: res,
        """
        allowances_archive = self.read(cr, uid, ids, ['transfer'], context=context)
        unlink_ids = []
        for record in allowances_archive:
            if record['transfer'] == False:
                unlink_ids.append(record['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('Sorry you can not Delete this record(s), Because It already Transtered To account Voucher!'))
        for id in unlink_ids:
            allowances_archive_name = self.browse(cr, uid, id, context=context).name
            message = _("allowances archive '%s' has been deleted.") % allowances_archive_name
            self.log(cr, uid, id, message)
        return super(rented_cars_allowances_archive, self).unlink(cr, uid, unlink_ids, context=context)



    def action_create_ratification(self,cr,uid,ids,context={}):
       """create ratification for Rented Cars allowances archive 
       @return: Dictionary 
       """
       
       
       rented_allowances_obj = self.pool.get('rented.cars.allowances.archive')
       account_journal_obj = self.pool.get('account.journal')   
       account_obj = self.pool.get('account.account')
       voucher_obj = self.pool.get('account.voucher')
       voucher_line_obj = self.pool.get('account.voucher.line')
       affairs_account_obj = self.pool.get('admin_affairs.account')
       affairs_model_obj = self.pool.get('admin.affairs.model')
       for record in self.browse(cr,uid,ids,context=context):

           affairs_model_ids = affairs_model_obj.search(cr, uid, [('model','=','rented.cars')], context=context)
           affairs_account_ids = affairs_account_obj.search(cr, uid, [('model_id','=',affairs_model_ids[0])], context=context)
           if not affairs_account_ids:
                	raise osv.except_osv(_('Error'), _("Please enter the Rented Car accounting configuration"))
           affairs_account = affairs_account_obj.browse(cr, uid, affairs_account_ids[0], context=context)
           accoun_model_ids = affairs_model_obj.search(cr, uid, [('model','=','rented.cars')], context=context)
           account_ids = account_obj.search(cr, uid, [('company_id','=',record.company_id.id),('code','=',str(affairs_account.code))], context=context)
           journal_ids =  account_journal_obj.search(cr, uid, [('company_id','=',record.company_id.id),('name','=',affairs_account.name_type.name)], context=context)
           journal_id = journal_ids and journal_ids[0] or affairs_account.journal_id.id
           account_id = account_ids and account_ids[0] or affairs_account.account_id.id
           analytic_id = affairs_account.analytic_id
           """@declar vir to count the project and non projct voucher"""
           ar_mount_manag=0.00
#           ar_mount_proj=0.00
           sum_list=0.00
           ar_total=0.00
#           ar_total_pro=0.00
           list1=[]
           if record.transfer:
             raise osv.except_osv(_('Warning'), _("This archive already transfered to the accounting"))
         
           """journal_id = affairs_account_record.journal_id
           analytic_id = affairs_account_record.analytic_id
           account_id = affairs_account_record.account_id"""
#           if not account_id:
#             raise osv.except_osv(_('Error'), _("Please enter the rented cars account"))

           cr.execute( 'SELECT sum(l.amount_total) as amount_total,a.name as analytic_name,a.id '\
                    'FROM rented_cars_allowances_lines l '\
                    'left join hr_department h on (h.id=l.department_id) '\
                    'left join account_analytic_account a on (h.analytic_account_id = a.id) '\
                    'where l.rented_cars_allow_id=%s '\
                    'GROUP BY a.id,a.name', (record.id,))
           res =  cr.dictfetchall()
           """@count the tow acount of towih project and non projct voucher"""
           for ar in res:
               """if ar['project']==True:
                  ar_mount_proj+=ar['amount_total']
                  list1.append(ar_mount_proj)
                  for lis2 in list1:
                      ar_total_pro=lis2
               else:"""
               ar_mount_manag+=ar['amount_total']
               ar_total=ar_mount_manag
           ##########################################################################
           voucher_dict={
                 'company_id':record.company_id.id,
                 'name': 'Rented/RCA/' + ' - ' + str(record.month) + ' - ' + str(record.year),
                 'type':'ratification',
                 'reference':'Rented/RCA/' ,
		 'amount':ar_total,
                 'partner_id' : record.partner_id.id,
                 'account_id' : record.partner_id.property_account_payable.id,
                 'narration' : 'Rented Cars Allowance No:  ' + record.name ,
                 #'amount_in_word':amount_to_text_ar(ar_total),
                 'department_id':record.dep.id,
                     }
           
           voucher_id = False
#           pro_voucher_id = False
           vouchers = []
           for line in res:
               """if line['project'] and not pro_voucher_id:
                   if not affairs_account_record.pro_account_id or not affairs_account_record.pro_journal_id:
                       raise osv.except_osv(_('Warning !'), _('Please insert Journal or Account For Rented Car'))
                   voucher_dict.update({'journal_id':affairs_account_record.pro_journal_id.id})
                   voucher_dict.update({'amount_in_word':amount_to_text_ar(ar_total_pro)})
                   pro_voucher_id = voucher_obj.create(cr, uid, voucher_dict, context=context)  
                   vouchers.append(pro_voucher_id)

               if not line['project'] and not voucher_id:
                   if not affairs_account_record.account_id or not affairs_account_record.journal_id:
                       raise osv.except_osv(_('Warning !'), _('Please insert Journal or Account For Rented Car'))"""
               voucher_dict.update({'journal_id':journal_id})
               #voucher_dict.update({'amount_in_word':amount_to_text_ar(ar_total)})
               voucher_id = voucher_obj.create(cr, uid, voucher_dict, context=context)    
               vouchers.append(voucher_id)               
               
               voucher_line_dict = {
                  'voucher_id': voucher_id,
                  'account_analytic_id':line['id'],
                  'account_id':account_id,
                  'amount':line['amount_total'],
                  'type':'dr',
                  'name':line['analytic_name'] or'/' ,
                  
                               }
               voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
           
           voucher_obj.compute_tax(cr, uid,vouchers, context)
           
           #################### update workflow state###############
           voucher_state = 'draft'
           if record.company_id.affairs_voucher_state : 
                voucher_state = record.company_id.affairs_voucher_state 
           if voucher_id:
           	wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'account.voucher',voucher_id, voucher_state, cr)
		voucher_obj.write(cr, uid, voucher_id, {'type':'ratification','ratification':True,'state':voucher_state}, context)
#           if pro_voucher_id: res = wf_service.trg_validate(uid, 'account.voucher',pro_voucher_id, 'preresource', cr)
           ##################            
           copy_attachments(self,cr,uid,[record.id],'rented.cars.allowances.archive',voucher_id,'account.voucher', context)
           rented_allowances_obj.write(cr, uid, record.id,{'transfer':True,} ,context=context)             
       return True




#----------------------------------------
# Class rented cars allowances lines
#----------------------------------------
class rented_cars_allowances_lines(osv.osv):
    _name = "rented.cars.allowances.lines"
    _description = 'Rented cars Allowances Lines'
    _columns = {
	    'rented_cars_allow_id':fields.many2one('rented.cars.allowances.archive', 'Allowances archive',readonly=True),
	    'partner_id': fields.many2one('res.partner','Executing Agency'),
        'cost_of_rent':fields.float('Cost Of Rent',digits=(18,2),readonly=True),
        'amount_untaxed':fields.float('Untaxed Amount',digits=(18,2),readonly=True),
        'amount_tax':fields.float('Taxes',digits=(18,2),readonly=True),
        'amount_total':fields.float('Total',digits=(18,2),readonly=True),
        'deduct_days':fields.float('Deduct days',digits=(18,0),readonly=True),
        'deduct_amount':fields.float('Deduct amount',digits=(18,2),readonly=True),
        'department_id': fields.many2one('hr.department', 'Department',readonly=True),
        'partner_id':  fields.related('rented_cars_allow_id', 'partner_id', type='many2one', relation='res.partner',readonly=True, string='Partner'),
        'rent_id': fields.many2one('rented.cars', 'Contract No',required=True,readonly=True),
        'car_id': fields.many2one('fleet.vehicle', 'Car Name',required=True,readonly=True),

                    }


