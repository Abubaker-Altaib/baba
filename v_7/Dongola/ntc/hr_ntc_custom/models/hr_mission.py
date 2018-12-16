# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
import datetime
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from admin_affairs.model.email_serivce import send_mail
from datetime import timedelta
from tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

'''name_states = [
    ('1', 'الولاية الشمالية'),
    ('2', 'ولاية نهر النيل'),
    ('3', 'ولاية البحر الأحمر'),
    ('4', 'ولاية القضارف'),
    ('5', 'ولاية كسلا'),
    ('6', 'ولاية سنار'),
    ('7', 'ولاية الخرطوم'),
    ('8', 'ولاية الجزيرة'),
    ('9', 'ولاية شمال كردفان'),
    ('10', 'ولاية النيل الأزرق'),
    ('11', 'ولاية النيل الأبيض'),
    ('12', 'ولاية جنوب كردفان'),
    ('13', 'ولاية غرب كردفان'),
    ('14', 'ولاية شرق دارفور'),
    ('15', 'ولاية جنوب دارفور'),
    ('16', 'ولاية وسط دارفور'),
    ('17', 'ولاية شمال دارفور'),
    ('18', 'ولاية غرب دارفور'),
]'''


name_states = [('1','الولايات')]
class mission_category(osv.osv):
    
    _inherit = "hr.mission.category"

    _columns = {
        'name_state': fields.selection(name_states ,'Destination'),
        'type_miss': fields.selection([('internal','Internal Mission'),('external','Participation External')], 'Mission Type'),
        'country':fields.many2many('res.country','country_mission_rel', 'mission_categry','country_id',"Destination"),
    }
    
    def change_name(self, cr, uid, ids, name_state, country, context=None):
        names= ""
        if name_state:
            name2= dict(name_states).get(name_state)
            names+=name2
        if country:
            names= ""
            name2 = self.pool.get('res.country').browse(cr, uid, country).name
            names+=name2
        return {'value': {'name':names,}}
        
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if 'country' in vals :
            names = ""
            name2 = ""
            for coun in self.browse(cr,uid,ids,context=context):
                name2 = coun.country
                if vals['country'] != False:
                    names = vals['country']
                    name2 = self.pool.get('res.country').browse(cr, uid, names).name
                    vals['name'] = name2
        if 'name_state' in vals:
            names = ""
            name2 = ""
            for coun in self.browse(cr,uid,ids,context=context):
                name2 = coun.name_state
                if vals['name_state']:
                    names = vals['name_state']
                    name2= dict(name_states).get(names)
                    vals['name'] = name2
        super(mission_category,self).write(cr, uid, ids, vals, context)
        return True
        
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        names = ""
        name2 = ""
        if 'country' in vals:
            if vals['country'] != False:
                names = vals['country']
                name2 = self.pool.get('res.country').browse(cr, uid, names).name
        if 'name_state' in vals:
            if vals['name_state']:
                names = vals['name_state']
                name2= dict(name_states).get(names)
        vals['name'] = name2
        return super(mission_category, self).create(cr, uid, vals, context=context)
        
    def _default_currency(self, cr, uid, context=None):
        if context is None:
            context = {}
        model_data = self.pool.get('ir.model.data')
        res = False
        try:
            res = model_data.get_object_reference(cr, uid, 'hr_ntc_custom', 'SDG')[1]
        except ValueError:
            res = False
        return res
    
    
    def onchange_currancy(self, cr, uid, ids, type_miss, context=None):
        if ids:
            model_data = self.pool.get('ir.model.data')
            res = False
            if type_miss == 'internal':
                res = model_data.get_object_reference(cr, uid, 'hr_ntc_custom', 'SDG')[1]
                
            if type_miss == 'external':
                res = model_data.get_object_reference(cr, uid, 'base', 'USD')[1]
                
            return {
                    'value':{'fees_currency_id':res,'name_state':False,'country':False}
                }
        return {}
        
    _defaults = {
        'type' : '',
        'type_miss':'internal',
        'fees_currency_id':_default_currency,
    }
    
class hr_allowance_deduction(osv.Model):
    
    _inherit = "hr.allowance.deduction"

    _columns = {
        'mission': fields.selection([('mission','Mission'),('loan','Loan'),('train','Training')], 'Allowance State'),
    }

    _defaults = {
        'mission':'mission',
    }
    
class allowance_account(osv.Model):
    
    _name = "allowance.account"

    _columns = {
        'name': fields.char('Name',size=64),
        'day_allow': fields.float("Day Allowance"),
    }
    
class allowance_states(osv.Model):
    
    globals()['total_days'] = 0
    globals()['total_sum'] = 0
    _name = "allowance.states"
    _rec_name = "alloww_idss"
    _columns = {
        'mission_line_ids': fields.many2one('hr.employee.mission.line', 'Mission Lisne' , invisible='1' ,ondelete='cascade'),
        'alloww_idss': fields.many2one('allowance.account', 'Allowance State' , required=True ),
        'day_state': fields.integer("Day Allowance", required=True),
    }
    
    def on_change_day(self, cr, uid, ids, day_state, days, day_diff, context=None):
	    if day_diff :
		    globals()['total_sum'] = day_diff
	    if globals()['total_sum'] == 0:
		    globals()['total_days'] += day_state
	    if globals()['total_sum']:
		    globals()['total_days'] = globals()['total_sum'] + day_state 
	    if globals()['total_days'] <= days:
		    globals()['total_sum'] = globals()['total_days']
            if globals()['total_days'] > days:
                globals()['total_days'] = 0
                #raise osv.except_osv(_('Error!'),_("The number of day allowance greater than days"))
	    return True
        
        
class employee_mission(osv.osv):

    _inherit = "hr.employee.mission"

    mission_state = [
    ('draft', 'Draft'),
    ('completed','Waiting General Department Manager Approve'),
    #('confirmed', 'Waiting HR and Financial Manager Approval'),
    ('validated','Waiting HR and Financial Manager Approval'),
    ('approved', 'Enrich was Transfered'),
    ('hr_approved', 'Waiting Reviewer Approval'),
    ('reviewed', 'Waiting Transferring'),
    ('done', 'Done'),
    ('rejected', 'Rejected'),
    ]

    def get_default_allow(self, cr, uid, context=None):
        """
            Method to get default allow state
        """
        data_obj = self.pool.get('ir.model.data')
        allow_state_id = data_obj.get_object_reference(cr, uid,'hr_ntc_custom', 'ration_esta')
        result = allow_state_id[1]
        
        return result

    _columns = {
        'type_mission': fields.selection([('internal','Internal Mission'),('external','External Mission')], 'Mission Type', required=True),
        'allow_state': fields.many2one('allowance.account', 'Allowance State' ),
        'purpose': fields.text("Mission Purposes"),
        'state': fields.selection(mission_state, 'State', readonly=True),
        'external_mission_type' : fields.selection([('external_training','External Training'),('external_particip','External Participation')], 'External Mission Type'),
        'country_id':fields.many2one('res.country',"Destination"),
        'mission_id': fields.many2one('hr.mission.category', "Destination", required=False),
        #'voucher_number' :fields.many2one('account.voucher','Accounting Number', size=64 , readonly=True),
        }


    _defaults = {
            'type_mission': 'internal',
            'external_mission_type': 'external_particip',
            'allow_state' : get_default_allow,
              } 

    def _check_limit(self, cr, uid, ids, context=None):
        for m in self.browse(cr, uid, ids, context=context):
            if m.type_mission == 'internal':
                if m.state != 'draft' and not m.mission_id.limit_exceed and m.days > m.mission_id.limit:
                    raise osv.except_osv(_('Error!'), _('You can not exceed the maximum days number for this mission'))
                    return False
        return True

    _constraints = [
        (_check_limit, ' ', []),
    ]
    
    def onchange_mission(self, cr, uid, ids, context=None):
        return {'value':{'mission_id':False}}

    def create(self, cr, uid, vals, context=None):
        """
        Method thats overwrite the create method and naming the mission by adding its sequence to the name.

        @param vals: Values that have been entered
        @return: super create method
        """
        flag = self.pool.get('res.users').has_group(cr, uid, 'base.group_hr_user')
        if vals['type_mission'] == 'external' and not flag:
            raise osv.except_osv(_('Warning!'),_('Only HR Employee can deal with external missions'))

        #if vals.get('mission_id'):
        if vals['type_mission'] == 'internal':
            mission = self.pool.get('hr.mission.category').browse(cr, uid, vals.get('mission_id'), context=context)
            vals.update({'name': mission.name + '/' + self.pool.get('ir.sequence').get(cr, uid, 'hr.employee.mission')})
            globals()['total_days'] = 0
            globals()['total_sum'] = 0

        #if vals.get('country_id'):
        if vals['type_mission'] == 'external':
            country = self.pool.get('res.country').browse(cr, uid, vals.get('country_id'), context=context)
            vals.update({'name': country.name + '/' + self.pool.get('ir.sequence').get(cr, uid, 'hr.employee.mission')})

        return super(employee_mission, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        Method thats overwrite the write method and updates the mission name by adding its sequence to the it.

        @param vals: Values that have been entered
        @return: Supper copy Method 
        """
        emp_mission = self.browse(cr, uid, ids, context=context)[0]
        if emp_mission.state != 'draft' or ('type_mission' in vals.keys()):
            flag = self.pool.get('res.users').has_group(cr, uid, 'base.group_hr_user')
            flag1 = self.pool.get('res.users').has_group(cr, uid, 'base.group_department_manager')
            if not flag and emp_mission.state == 'approved':
                raise osv.except_osv(_('Warning!'),_('Only HR Employee can write in the current state of the mission'))
            if 'type_mission' in vals.keys() and vals['type_mission'] == 'external' and not flag:
                raise osv.except_osv(_('Warning!'),_('Only HR Employee can deal with external missions'))


        if vals.get('mission_id'):
            mission = self.pool.get('hr.mission.category').browse(cr, uid, vals.get('mission_id'), context=context)
            vals.update({'name': mission.name + '/' + emp_mission.name.split('/',1)[1]})
            globals()['total_days'] = 0
            globals()['total_sum'] = 0

        if vals.get('country_id'):
            country = self.pool.get('res.country').browse(cr, uid, vals.get('country_id'), context=context)
            vals.update({'name': country.name + '/' + emp_mission.name.split('/',1)[1]})

        if vals.get('department_id') and emp_mission.department_id.id != vals['department_id']:
            now_line_ids = []
            line_obj = self.pool.get('hr.employee.mission.line')
            line_ids_to_delete = line_obj.search(cr,uid,[('emp_mission_id','=',ids[0])])
            line_obj.unlink(cr,uid,line_ids_to_delete)


        write_boolean = super(employee_mission, self).write(cr, uid, ids, vals, context=context)
        emp_mission = self.browse(cr, uid, ids, context=context)[0]
        for line in emp_mission.mission_line:
            if not line.employee_id:
                raise osv.except_osv(_('Warning!'),_('Please enter employee name'))
        
        ## to send notification
        if vals.has_key('state'):
            result = self.check_manager_email(cr,uid,ids,context)
            
        return write_boolean

    def mission_approved(self, cr, uid, ids, context=None):
        """
        Workflow method change record state to 'approved' and 
        Transfer Mission mission's fee to voucher

        @return: Boolean True
        """
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        account_period_obj = self.pool.get('account.period')
        for mission in self.browse(cr, uid, ids, context=context):
            mission_amount = mission.mission_fee
            if mission_amount <= 0:
                raise osv.except_osv(_('Warning!'),_('Mission fee should be more than zero'))
            
            if mission.mission_id.fees_account_id and mission.mission_id.journal_id and mission.mission_id.account_analytic_id:
                date = time.strftime('%Y-%m-%d')
                period = account_period_obj.find(cr, uid, dt=date, context={'company_id':mission.company_id.id})[0]
                voucher_dict = {
                    'company_id':mission.company_id.id,
                    'journal_id':mission.mission_id.journal_id.id,
                    'account_id':mission.mission_id.fees_account_id.id,
                    'period_id': period,
                    'name': mission.name + ' - ' + mission.start_date,
                    'amount':mission_amount,
                    'type':'purchase',
                    'date': date,
                    'reference':'HR/Mission Fees/' + mission.name + ' - ' + mission.start_date,
 					'department_id': mission.department_id.id,
					'currency': mission.mission_id.fees_currency_id.id,
               }
                voucher = voucher_obj.create(cr, uid, voucher_dict, context=context)
                voucher_line_dict = {
                     'voucher_id':voucher,
                     'account_id':mission.mission_id.fees_account_id.id,
                     'account_analytic_id':mission.mission_id.account_analytic_id.id,
                     'amount':mission_amount,
                     'type':'dr',
                }
                voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
                
                vouch = voucher_obj.browse(cr, uid, voucher, context=context)
                self.create_grant_rights(cr,uid,ids,context=context)
                return self.write(cr, uid, ids, {'state':'approved', 'voucher_number': vouch.number, })
            else:
                raise osv.except_osv(_('Error!'),_("Please enter mission accounting details at the configuration of the mission destination"))
        
        self.create_grant_rights(cr,uid,ids,context=context)
        return self.write(cr, uid, ids, {'state':'approved'}, context=context)
    
    def mission_done(self, cr, uid, ids, context=None):
        """
        Workflow method change record state to 'done' and 
        @return: Boolean True
        """
        self.mission_approved_old(cr, uid, ids, context)
        return self.write(cr, uid, ids, {'state':'done'}, context=context)

    def mission_approved_old(self, cr, uid, ids, context=None):
        """
        Method that calculate mission,s allowance and 
        Transfer Mission's lines into voucher

        @return: Boolean True
        """
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        account_period_obj = self.pool.get('account.period')
        emp_obj = self.pool.get('hr.employee')
        payroll_obj = self.pool.get('payroll')
        user = self.pool.get('res.users').browse(cr, uid, uid, context = context)
    	journal_id = user.company_id.hr_journal_id and user.company_id.hr_journal_id.id or False
        analytic_id = user.company_id.hr_analytic_account_id and user.company_id.hr_analytic_account_id.id or False
        for mission in self.browse(cr, uid, ids, context=context):
            employees_dic = {}
            note = ' \n' + u'الموظفين:' 
            total_amount = tax_amount = stamp_amount = 0.0
            for line in mission.mission_line:
                total_amount += line.mission_amounts
                tax_amount += line.tax
                stamp_amount += line.stamp
                employees_dic[line.employee_id] = line.mission_amounts
                note += ' \n' + line.employee_id.name 

            lines = emp_obj.get_emp_analytic(cr, uid, employees_dic,  {'allow_deduct_id': mission.mission_id.allowance_id.id})
            
            print "--------------------note", note
            for line in lines:
                line['allow_deduct_id'] = mission.mission_id.allowance_id.id
            reference = 'HR/Mission Allowance/' + mission.name + ' - ' + mission.start_date
            narration = 'HR/Mission Allowance/' + mission.name + ' - ' + mission.start_date
            narration += note
            ## if total amount more than 0 then create voucher or continue
            if total_amount > 0:
                voucher = payroll_obj.create_payment(cr, uid, ids, {'reference':reference, 'lines':lines,
                                                                    'tax_amount':tax_amount, 'stamp_amount':stamp_amount,
                                                                     'narration':narration,'department_id':mission.department_id.id,
                                                                     'model':'account.voucher'}, context=context)
                if voucher:
                    vouch = voucher_obj.browse(cr, uid, voucher, context=context)
                    return self.write(cr, uid, ids, {'voucher_number': voucher})
            '''mission_amount = 0.0
            stamp = 0.0
            for emp_mission_amount in mission.mission_line:
                mission_amount += emp_mission_amount.mission_amounts
                stamp += emp_mission_amount.stamp
            if mission.mission_id.allowance_id.account_id and journal_id and analytic_id:
                date = time.strftime('%Y-%m-%d')
                period = account_period_obj.find(cr, uid, dt=date, context={'company_id':mission.company_id.id})[0]
                voucher_dict = {
                    'company_id':mission.company_id.id,
                    'journal_id':journal_id,
                    'account_id':mission.mission_id.allowance_id.account_id.id,
                    'period_id': period,
                    'name': mission.name + ' - ' + mission.start_date,
                    'amount':mission_amount-stamp,
                    'type':'purchase',
                    'date': date,
                    'reference':'HR/Mission/' + mission.name + ' - ' + mission.start_date,
 					'department_id': mission.department_id.id,
					'currency': mission.mission_id.fees_currency_id.id,
               }
                voucher = voucher_obj.create(cr, uid, voucher_dict, context=context)

                voucher_line_dict = {
                     'voucher_id':voucher,
                     'account_id':mission.mission_id.allowance_id.account_id.id,
                     'account_analytic_id':analytic_id,
                     'amount':mission_amount,
                     'type':'dr',
                }
                voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
                if stamp:
                    if mission.company_id.stamp_account_id.id:
                        fees_voucher_line = {
                            'voucher_id':voucher,
                            'account_id':mission.mission_id.allowance_id.account_id.id,
                            'amount':-stamp,
                            'type':'dr',
                        }
                        voucher_line_obj.create(cr, uid, fees_voucher_line, context=context)
                    else:
                        raise osv.except_osv(_('Error!'),_("Please enter stamp account in HR settings"))
                vouch = voucher_obj.browse(cr, uid, voucher, context=context)
                return self.write(cr, uid, ids, {'state':'approved', 'voucher_number': vouch.number, })
            else:
                raise osv.except_osv(_('Error!'),_("Please enter mission accounting details"))'''
        return True

    def create_grant_rights(self, cr, uid, ids, context=None):
          """ function to create grant rights record for each employee in the mission line in 
              order to give access rigts to the alternative employee 
          """
          grant_order_obj = self.pool.get("granted.rights.order")
          grant_order_lines_obj = self.pool.get("granted.rights.order.lines") 
          department_obj = self.pool.get('hr.department')
          
          
          manager = False
          mission = self.browse(cr,uid,ids[0])
          line_ids = [x.id for x in mission.mission_line]
          if mission.end_date >=  time.strftime('%Y-%m-%d'):
              for rec in mission.mission_line:
                  dep_ids = department_obj.search(cr,uid,[('manager_id','=',rec.employee_id.id)])
                  #if rec.employee_id.id == department_obj.browse(cr,uid,rec.employee_id.department_id.id).manager_id.id :
                  if dep_ids:
                     manager = True

                  end_grant_date =  datetime.datetime.strptime(mission.end_date, '%Y-%m-%d')
                  
                  end_grant_date = end_grant_date + timedelta(days=1)
                                                
                  order_id = grant_order_obj.create( cr, uid,{
                                            
                                            'delegation_type' : 'mission',
                                            'mission_order_id' :mission.id,
                                            'employee_donor' : rec.employee_id.id,
                                            'employee_candidate' : rec.alternative_emp_id.id,
                                            'start_grant_date'  : mission.start_date,                      
                                            'end_grant_date'  :end_grant_date,
                                            'department_id' : rec.employee_id.department_id.id,
                                            'is_a_amanger' :  manager,

                                                              })
                  res = grant_order_obj.on_change_donor_employee(cr, uid, order_id , rec.employee_id.id , context=context)
                  for rec in res['value']['donor_groups_ids']:
                      rec.update({ 'order_id' : order_id})
                      grant_order_lines_obj.create( cr, uid,rec )
              
          return True
    
    def recalcuate_days(self, cr, uid, ids, context=None):
        """
        Recalculate amount of mission if number of days changed.

        @return: True
        """
        employee_mission_line_obj = self.pool.get('hr.employee.mission.line')
        for rec in self.browse(cr, uid, ids, context=context):
            for line in rec.mission_line:
                new_amount = employee_mission_line_obj.onchange_days(cr, uid, ids, line.days, line.employee_id.id, line.allow_state, rec.mission_id.id, rec.allow_state.id, rec.type_mission)
                employee_mission_line_obj.write(cr, uid, [line.id], new_amount['value'], context=context)
        return True


    def create_lines(self, cr, uid, ids, context=None):
        """ 
        Method that Create the mission lines 
        @return: boolean True
        """
        line_pool = self.pool.get('hr.employee.mission.line')
        for r in self.browse(cr, uid, ids, context=context):
            lines = line_pool.create(cr, uid, {'allow_account': r.allow_state.id,
                                                'department_id': r.department_id.id,
                                                'emp_mission_id': r.id,
                                                'days':r.days}, context=context)
            
        return True

    def onchange_department(self, cr, uid, ids, department_id, context=None):
        """
            Method returns the mission lines False when department change.
            @param department_id: department_id of the Mission
            @return: Dictionary contains the value of the mission lines
        """
        vals = {}
        if ids:
            emp_mission = self.browse(cr, uid, ids[0], context=context)
            if emp_mission.department_id.id != department_id:
                vals = {'mission_line':False}

        return {'value':vals,'domain':{}}

    def check_external_mission(self, cr, uid, ids, context=None):
        """
        Method used in workflow as conditon to check if it is external mission or not.
        @return: True if it is external and False otherwise
        """
        for h in self.browse(cr, uid, ids, context=context):
            if h.type_mission == 'external':
                  return True
            else:
                  return False

    def complete(self, cr, uid, ids, context=None):
        """
            Workflow method check if mission's fee whether 0 or not also 
            check if there is alternative employee for everey employee in the missin 
            and change record state to 'completed'
            @return: Boolean True
        """
        emp_mission = self.browse(cr, uid, ids[0], context=context)
        if emp_mission.mission_fee <= 0:
            raise osv.except_osv(_('Warning!'),_('Mission fee should be more than zero'))

        for line in emp_mission.mission_line:
            if not line.alternative_emp_id:
                raise osv.except_osv(_('Warning!'),_('Please enter the alternative employee for the employee %s') % (line.employee_id.name))

        return self.write(cr, uid, ids, {'state':'completed'}, context=context)


    def mission_external(self, cr, uid, ids, context=None):
        """
            Workflow method that used when mission type is external where is no mission allowance
            and create rights recrod for the alternative employee and then write state done 
            @return: Boolean True
        """
        emp_mission = self.browse(cr, uid, ids[0], context=context)
        
        for line in emp_mission.mission_line:
            if not line.alternative_emp_id:
                raise osv.except_osv(_('Warning!'),_('Please enter the alternative employee for the employee %s') % (line.employee_id.name))

        write_bool = self.write(cr, uid, ids, {'state':'done'}, context=context)
        self.create_grant_rights(cr,uid,ids,context=context)
        return write_bool

    def mission_allowance_calcu(self, cr, uid, ids, context=None):
        """
            Workflow method that used when mission type is external where is no mission allowance
            and create rights recrod for the alternative employee and then write state done 
            @return: Boolean True
        """
        emp_mission = self.browse(cr, uid, ids[0], context=context)
        
        for line in emp_mission.mission_line:
            if not line.alternative_emp_id:
                raise osv.except_osv(_('Warning!'),_('Please enter the alternative employee for the employee %s') % (line.employee_id.name))

        write_bool = self.write(cr, uid, ids, {'state':'approved'}, context=context)
        self.create_grant_rights(cr,uid,ids,context=context)
        return write_bool

    def check_manager_email(self, cr, uid, ids, context=None):
        """
            Method that send mail notification
        """
        # just to use the common method dep_manager_user() in model the 'hr.employee.substitution' to get manager user_id
        emp_sub_obj = self.pool.get('hr.employee.substitution')
        for h in self.browse(cr, uid, ids, context=context):
            if h.state == 'completed' :
                group = False
                dep_cat = h.department_id.cat_id
                if dep_cat.category_type == 'section':
                    department_id = h.department_id.parent_id.parent_id.id
                else:
                    department_id =  h.department_id.parent_id.id

                manager_user_id = emp_sub_obj.dep_manager_user(cr, uid, ids, {'department_id':department_id}, context=context)
                send_mail(self, cr, uid, ids[0], group,u'تصديق مأمورية'.encode('utf-8'), 
                    u'هناك سجل مأمورية في انتظار تصديق مدير الادارة العامة'.encode('utf-8'), 
                    [manager_user_id[0]['user_id']] ,context=context)
            if h.state == 'validated' :
                send_mail(self, cr, uid, ids[0], 'base_custom.group_general_hr_manager',
                    u'تصديق مأمورية و نثرية'.encode('utf-8'), u'هناك سجل مأمورية في انتظار تصديق مدير الادارة العامة للموارد البشرية و المالية'.encode('utf-8'),
                     context=context)
            if h.state == 'hr_approved' :
                send_mail(self, cr, uid, ids[0], 'purchase_ntc.group_internal_auditor',u'تصديق بدل مأمورية'.encode('utf-8'), u'هناك سجل مأمورية في انتظار تصديق المراجع لحساب بدل المأمورية'.encode('utf-8'), context=context)
            if h.state == 'reviewed' :
                send_mail(self, cr, uid, ids[0], 'base.group_hr_manager',u'تصديق و ترحيل بدل المامورية'.encode('utf-8'), u'هناك سجل مأمورية في انتظار تصديق مدير الموارد البشرية'.encode('utf-8'), context=context)

    def onchange_date_from(self, cr, uid, ids, date_from, date_to, days_no, field, context=None):
        """
        Retrieves number of remaining days for employee in specific holiday as holiday number of days and end date.

        @param date_to: End date
        @param date_from: Start date
        @param days_no: Number of days
        @param field: Changed field
        @return: Dictionary of values 
        """
        # Use days_no is not None instead of days_no != False because Zero is False but not None
        if date_from and (' ' not in date_from):
            date_from = date_from + ' ' + '00:00:00'

        if date_to and (' ' not in date_to):
            date_to = date_to + ' ' + '00:00:00'
        vals = {}
        dt_from = date_from and datetime.datetime.strptime(date_from, DEFAULT_SERVER_DATETIME_FORMAT)
        dt_to = date_to and datetime.datetime.strptime(date_to, DEFAULT_SERVER_DATETIME_FORMAT)
        
        if field == 'date_from':
            if dt_from and days_no is not None:
                vals.update({'end_date':str((dt_from + datetime.timedelta(days_no - 1)).date())})
            elif dt_from and dt_to:
                vals.update({'days':round(self.pool.get('hr.holidays')._get_number_of_days(date_from, date_to) + 1)})
        if field == 'date_to':
            if dt_from and dt_to:
                vals.update({'days':round(self.pool.get('hr.holidays')._get_number_of_days(date_from, date_to) + 1)})
            elif days_no is not None and dt_to:
                vals.update({'start_date':str((dt_to - datetime.timedelta(days_no - 1)).date())})
        if field == 'days':
            if dt_from and days_no is not None:
                vals.update({'end_date':str((dt_from + datetime.timedelta(days_no - 1)).date())})
            elif days_no is not None and dt_to:
                vals.update({'start_date':str((dt_to - datetime.timedelta(days_no - 1)).date())})
        return {'value':vals}

class employee_mission_line(osv.osv):

    _inherit = "hr.employee.mission.line"


    def _calculate(self, cr, uid, ids, field_name, arg=None, context=None):
        """
        Method that calculate the mission days, gross amount, tax, stamp and the net.

        @return: dictionary that contains mission_amounts,tax,stamp,gross_amount
        """
        payroll_obj = self.pool.get('payroll')
        result = {}
        date = time.strftime('%Y-%m-%d')
        #total_payroll=payroll_obj.allowances_deductions_calculation(cr,uid,date,emp,{}, [allowance_id.id],False,[allowance_id.id])
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id] = {
                            'tax': 0.0,
                            'stamp': 0.0,
                            'amount':0.0,
                            'gross_amount': 0.0,
                            'mission_amounts': 0.0,
            }

            if rec.emp_mission_id.type_mission == 'external':
                return result
            perant_allow_state = rec.emp_mission_id.allow_state.id
            parent_mission_id = rec.emp_mission_id.mission_id.id
            type_mission = rec.emp_mission_id.type_mission
            #on_result = self.onchange_days(cr, uid, ids, rec.days, rec.employee_id.id, rec.allow_state, parent_mission_id, perant_allow_state, context=context)
            
            if rec.emp_mission_id and rec.employee_id:
                on_result = self.onchange_days(cr, uid, ids, rec.days, rec.employee_id.id, rec.allow_state, parent_mission_id, perant_allow_state, type_mission, context=context)
                '''allow = rec.emp_mission_id.mission_id.allowance_id
                allow_dict= self.pool.get('payroll').allowances_deductions_calculation(cr,uid,date,rec.employee_id,{}, [allow.id],False,[allow.id])
                no_days = rec.days 
                exceeding = False
                if not allow.days and allow.maximum and no_days > allow.maximum and rec.allow_exceeding == False:
                    no_days = allow.maximum
                    exceeding = True
                res = allow_dict.get('result',[])
                
                amount = tax = stamp = mission_amounts = gross_amount = 0
                amount += res and round(res[0].get('amount',0),2 or 0) 
                tax += res and round(res[0].get('tax',0) * no_days ,2) or 0
                stamp += res and res[0].get('imprint',0) or 0
                mission_amounts += amount * no_days
                gross = mission_amounts - tax - stamp

                result[rec.id] = {
                                'tax': tax,
                                'stamp': stamp,
                                'amount':amount,
                                'mission_amounts': mission_amounts,
                                'gross_amount': gross,
                }'''
                result[rec.id] = on_result['value']
        return result

    def _get_line_ids(self, cr, uid, ids, context=None, args=None):
        """
        Method that gets the id of mission line.

        @return: list that contains mission lines ids
        """
        return self.pool.get('hr.employee.mission.line').search(cr, uid, [('emp_mission_id', 'in', ids)], context=context)
    
    _columns = {
        'allow_account': fields.many2one('allowance.account', 'Allowance' ,),
        'allow_state':fields.one2many('allowance.states', 'mission_line_ids', string="Allowance State"),
        'day_diff':fields.integer("Day Allowance Diff"),
        'mission_amounts': fields.function(_calculate, string='Mission Amount', method=True, type='float',
                                         digits_compute=dp.get_precision('Payroll'), multi='amount',
                                         store={'hr.employee.mission': (_get_line_ids, ['mission_id','allow_state'], 10),
                                                'hr.employee.mission.line': (lambda self, cr, uid, ids, c=None:ids, [], 10)}),
        'stamp': fields.function(_calculate, string='Stamp', method=True, type='float',
                                         digits_compute=dp.get_precision('Payroll'), multi='amount',
                                         store={'hr.employee.mission': (_get_line_ids, ['mission_id','allow_state'], 10),
                                                'hr.employee.mission.line': (lambda self, cr, uid, ids, c=None:ids, [], 10)}),
        'tax': fields.function(_calculate, string='Tax', method=True, type='float',
                                         digits_compute=dp.get_precision('Payroll'), multi='amount',
                                         store={'hr.employee.mission': (_get_line_ids, ['mission_id','allow_state'], 10),
                                                'hr.employee.mission.line': (lambda self, cr, uid, ids, c=None:ids, [], 10)}),
        'gross_amount': fields.function(_calculate, string='Gross Amount', method=True, type='float',
                                         digits_compute=dp.get_precision('Payroll'), multi='amount',
                                         store={'hr.employee.mission': (_get_line_ids, ['mission_id','allow_state'], 10),
                                                'hr.employee.mission.line': (lambda self, cr, uid, ids, c=None:ids, [], 10)}),
        'amount': fields.function(_calculate, string='Amount/Day', method=True, type='float',
                                         digits_compute=dp.get_precision('Payroll'), multi='amount',
                                         store={'hr.employee.mission': (_get_line_ids, ['mission_id','allow_state'], 10),
                                                'hr.employee.mission.line': (lambda self, cr, uid, ids, c=None:ids, [], 10)}),
        'department_id':fields.many2one('hr.department', "Department"),
        'employee_id' : fields.many2one('hr.employee', "Employee", required=False),
        'alternative_emp_id' : fields.many2one('hr.employee', "Alternative Employee"),
    }

    _sql_constraints = [
       ('employee_mission_uniqe', 'unique (employee_id,emp_mission_id)', 'You can not duplicate employee for the same mission!'),
    ]
    
    def onchange_days(self, cr, uid, ids, days, employee_id, allow_state, mission_id, allow_pernt,type_mission, context=None):
        """
        Compute missions amount for(Internal/External missions),mission days, gross amount, tax, stamp and the net
        with each change in days number or employee or allowance state of mission line 
        @param days: integer no of days entered by user
        @param employee_id: ID of employee
        @param mission_id: ID of mission
        @return: Dictionary of mission amount to be updated
        """
        if not employee_id or type_mission == 'external': 
            return {'value':{'mission_amounts':0,'amount':0,'stamp':0,'tax':0,'gross_amount':0}}
        payroll_obj = self.pool.get('payroll')
        mission_obj = self.pool.get('hr.mission.category')
        emp_obj = self.pool.get('hr.employee')
        allowance_id = mission_obj.browse(cr, uid, mission_id).allowance_id
        emp = emp_obj.browse(cr, uid, employee_id, context=context)
        date = time.strftime('%Y-%m-%d')
        days_num = 0
        final = 0
        days_const = 0
        if not allow_state:
            if not allow_pernt:
                raise osv.except_osv(_('Warning!'),_("please Enter Allowance State"))
            allow = self.pool.get('allowance.account').browse(cr, uid, allow_pernt)
            
            day = allow.day_allow
            days_num = day * days
            final +=days_num
        else:
            if isinstance(allow_state[0], list):
                for allow in allow_state:
                    if allow[2]!=False:
                        day_allowance = self.pool.get('allowance.account').browse(cr, uid, allow[2]['alloww_idss']).day_allow
                        days_num = day_allowance * allow[2]['day_state']
                        final +=days_num
                    else:
                        allow_id = self.pool.get('allowance.states').browse(cr, uid, allow[1]).alloww_idss
                        day_allowance = self.pool.get('allowance.account').browse(cr, uid, allow_id.id).day_allow
                        dayss = self.pool.get('allowance.states').browse(cr, uid, allow[1]).day_state
                        days_num = day_allowance * dayss
                        final +=days_num
            else:
                for allow in allow_state:
                    allowance = allow.alloww_idss.day_allow
                    day_allowance = allow.day_state
                    day_num = allowance * day_allowance
                    final+=day_num 
        total_payroll = payroll_obj.allowances_deductions_calculation(cr,uid,date,emp,{}, [allowance_id.id],False,[allowance_id.id])
        #amount = total_payroll['total_allow'] * final
        result = total_payroll['result']
        amount = tax = stamp = mission_amounts = gross_amount = 0
        amount += result and round(result[0].get('amount',0),2 or 0) 
        tax += result and round(result[0].get('tax',0) * final ,2) or 0
        stamp += result and result[0].get('imprint',0) or 0
        mission_amounts += amount * final
        gross = mission_amounts - tax - stamp
        emp_mission_dict = {
            'mission_amounts':mission_amounts,
            'amount':amount,
            'stamp':stamp,
	        'day_diff':globals()['total_sum'],
            'tax': tax,
            'gross_amount': gross
        }        
        return {'value': emp_mission_dict}

    def onchange_employee(self, cr, uid, ids, emp_id, days, allow_state, mission_id, department_id, allow_pernt,type_mission, context=None):
        """
        Method returns the employee_type that missions is enabled for them.
        @param emp_id: ID of the employee
        @return: Dictionary contains the domain of the employee_type
        """
        #employee_type domain
        emp_obj = self.pool.get('hr.employee')
        company_obj = self.pool.get('res.users').browse(cr, uid, uid).company_id
        contractors = company_obj.mission_contractors
        employee = company_obj.mission_employee
        recruit = company_obj.mission_recruit
        trainee = company_obj.mission_trainee
        employee_domain = emp_obj._get_default_employee_domain(cr, uid, ids, contractors, employee, recruit, trainee)
        #employee_domain['employee_id'] += [('state', '=', 'approved'),('department_id','=',department_id)]
        #domain = {'employee_id':employee_domain['employee_id']}
        res = self.onchange_days(cr, uid, ids, days, emp_id, allow_state, mission_id, allow_pernt,type_mission, context=context)
        #res.update({'domain': domain})
        #####################################
        rec = self.browse(cr, uid, ids[0])
        holidays_obj = self.pool.get('hr.holidays')
        holidays_status_obj = self.pool.get('hr.holidays.status')
        emp_ids = []
        if rec.emp_mission_id.start_date and rec.emp_mission_id.end_date:
            date_from = rec.emp_mission_id.start_date + ' ' + '00:00:00'
            date_to = rec.emp_mission_id.end_date + ' ' + '00:00:00'
            state = ['draft','confirm','validate']
            emp_ids = []
            holiday_status_id = holidays_status_obj.search(cr,uid,['|',('absence', '=', False),('absence', '!=', True)])
            cr.execute('SELECT Distinct  employee_id '\
                  'FROM public.hr_holidays '\
                  'where date_from <= %s '\
                  'AND date_to >= %s '\
                  'AND holiday_status_id in %s',(date_from,date_to,tuple(holiday_status_id)))
            res1 = cr.dictfetchall()
            for h in res1:
                if h['employee_id'] not in emp_ids:
                    emp_ids.append(h['employee_id'])
        employee_domain['employee_id'] += [('state', '=', 'approved'),('department_id','child_of',department_id),]
        #employee_domain['employee_id'] += [('state', '=', 'approved'),('department_id','=',department_id),('id','not in',emp_ids)]
        domain_alternative = employee_domain['employee_id']
        if emp_ids:
            domain_alternative += [('id','not in',emp_ids)]
        domain = {'employee_id':employee_domain['employee_id'],'alternative_emp_id':domain_alternative}
        res.update({'domain': domain})
        return res

    def write(self, cr, uid, ids, vals, context=None):
        """
        Method thats overwrite the write method to compare the total days of allowance state and the number
        of days for the mission line.

        @param vals: Values that have been entered
        @return: Supper copy Method 
        """
        write_boolean = super(employee_mission_line, self).write(cr, uid, ids, vals, context=context)
        for line in self.browse(cr, uid, ids, context=context):
            total_days = 0
            for allow_state in line.allow_state:
                total_days += allow_state.day_state 
            if total_days > line.days:
                raise osv.except_osv(_('Warning!'),_('The total days of allowance state for the employee %s is more than mission days for the same employee.')%(line.employee_id.name))
    
        return write_boolean


    def create(self, cr, uid, vals, context=None):
        """
        Method thats overwrite the create method and naming the mission by adding its sequence to the name.

        @param vals: Values that have been entered
        @return: super create method
        """
        if vals.has_key('allow_state') and vals['allow_state']:
            total_days = 0
            emp = self.pool.get('hr.employee').browse(cr,uid,vals['employee_id'])
            for state in vals['allow_state'][2]:
                total_days += state['day_state']
            if total_days > vals['days']:
                raise osv.except_osv(_('Warning!'),_('The total days of allowance state for the employee %s is more than mission days for the same employee.')%(emp.name))
        return super(employee_mission_line, self).create(cr, uid, vals, context=context)



class granted_rights_order(osv.Model):
    
    _inherit = "granted.rights.order"


    def write(self, cr, uid, ids, vals, context=None):
        """
        Method thats overwrite the write method and send email to the alternative employee

        @param vals: Values that have been entered
        @return: Supper copy Method 
        """

        write_boolean = super(granted_rights_order, self).write(cr, uid, ids, vals, context=context)
        rec = self.browse(cr, uid, ids, context=context)[0]
        
        
        ## to send notification
        if vals.has_key('state') and vals['state'] == 'granted' :
            group = False
            text = u'تم نقل صلاحيات الموظف  '.encode('utf-8') + (rec.employee_donor.name).encode('utf-8') + u' إليك للفترة من '.encode('utf-8') 
            text += str(rec.start_grant_date).encode('utf-8') + u' إلى '.encode('utf-8') + str(rec.end_grant_date).encode('utf-8') + u' وذلك لعدم توفره في هذه الفترة'.encode('utf-8')
            #text = text.encode('utf-8')
            send_mail(self, cr, uid, ids[0], group,u'الموظف البديل'.encode('utf-8'), 
                    text, 
                    [rec.employee_candidate.user_id.id] ,context=context)
            
        return write_boolean



        


    
