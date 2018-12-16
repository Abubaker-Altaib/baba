# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

#from openerp.osv import osv, fields
from __future__ import division
from mx import DateTime
from openerp import tools
import time
import datetime
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
from openerp import netsvc
import openerp.addons.decimal_precision as dp
import math
from openerp.addons.account_voucher.account_voucher import resolve_o2m_operations
from tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp.osv.orm import except_orm
from urlparse import urljoin
from urllib import urlencode
from admin_affairs.model.email_serivce import send_mail

class document_file(osv.Model):
    _inherit = 'ir.attachment'

    _columns = {
        'field':fields.char(size=32),
        }

    def write(self, cr, uid, ids, vals, context=None):
        if 'datas' in vals:
            if not vals['datas']:
              super(document_file, self).unlink(cr, uid, ids, context=context)
            else :
              super(document_file, self).write(cr, uid, ids, vals, context=context)

    def unlink(self, cr, uid, ids, context=None):
        ir_attachment = self.pool.get('ir.attachment')
        attachments = ir_attachment.browse(cr,uid,ids,context=context)
        att_list = filter(lambda x:x.field != False and x.res_model == 'hr.employee',attachments)
        for i in att_list:
            if i.field in ['nation','identity','pass','brth','nation_serve','re_emp']:
                self.pool.get('hr.employee').write(cr,uid,[i.res_id],{i.field:False})

        att_list = filter(lambda x:x.field != False and x.res_model == 'hr.employee.qualification',attachments)
        for i in att_list:
            if i.res_model == 'hr.employee.qualification':
                self.pool.get('hr.employee.qualification').write(cr,uid,[i.res_id],{'file':False})
                employee_id = self.pool.get('hr.employee.qualification').browse(cr,uid,i.res_id,context=context).employee_id.id
                search_ids = self.search(cr,uid,
                [('res_model','=','hr.employee'),
                 ( 'field','=','qualification,'+str(i.res_id) ),
                 ('res_id','=',employee_id)],context=context )
                super(document_file, self).unlink(cr, uid,search_ids, context=context)

        att_list = filter(lambda x:x.field != False and x.res_model == 'hr.employee.family',attachments)
        for i in att_list:
            if i.res_model == 'hr.employee.family':
                self.pool.get('hr.employee.family').write(cr,uid,[i.res_id],{'file':False})
                employee_id = self.pool.get('hr.employee.family').browse(cr,uid,i.res_id,context=context).employee_id.id
                search_ids = self.search(cr,uid,
                [('res_model','=','hr.employee'),
                 ( 'field','=','relation,'+str(i.res_id) ),
                 ('res_id','=',employee_id)],context=context )
                super(document_file, self).unlink(cr, uid,search_ids, context=context)
        
        super(document_file, self).unlink(cr, uid,ids, context=context)

class hr_employee(osv.Model):

    _inherit = "hr.employee"

    def _curr_id(self, cr, uid, ids, name, args, context=None):
        result = {}
        user_obj = self.pool.get('res.users')
        for emp in self.browse(cr, uid, ids, context=context):
            if emp.user_id.id == uid:
                result[emp.id] = True
            else:
                result[emp.id] = False
        return result

    def _curr_id_hr(self, cr, uid, ids, name, args, context=None):
        result = {}
        user_obj = self.pool.get('res.users')
        for emp in self.browse(cr, uid, ids, context=context):
            if user_obj.has_group(cr,uid,'base.group_hr_user') or user_obj.has_group(cr,uid,'purchase_ntc.group_internal_auditor'):
                result[emp.id] = True
            else:
                result[emp.id] = False
        return result

    def _curr_user(self, cr, uid, context=None):
        result = False
        user_obj = self.pool.get('res.users')
        if user_obj.has_group(cr,uid,'base.group_hr_user') or user_obj.has_group(cr,uid,'purchase_ntc.group_internal_auditor'):
                result = True
        
        return result

    def _is_gs_m(self, cr, uid, ids, name, args, context=None):
        res = {}
        user_obj = self.pool.get('res.users')

        result = self.browse(cr, uid, ids,context)
        for emp in result:
            if user_obj.has_group(cr,emp.user_id.id,'base_custom.group_general_department_manager'):
                res[emp.id] = True
            else:
                res[emp.id] = False


        return res
    
        

    def _is_gs_m_search(self, cr, uid, obj, name, args, context=None):
        new_list = []
        result = self.search(cr, uid, [])
        user_obj = self.pool.get('res.users')
        #g_ids = groups_ids(cr, ['base_custom.group_general_department_manager'])

        g_ids = []
        for group_ext_id in ['base_custom.group_general_department_manager']:
            assert group_ext_id and '.' in group_ext_id, "External ID must be fully qualified"
            module, ext_id = group_ext_id.split('.')
            cr.execute("""SELECT res_id FROM ir_model_data WHERE module=%s AND name=%s""",
                    (module, ext_id))
            fetch = [x[0] for x in cr.fetchall()]
            g_ids += fetch
        

        g_ids+=g_ids

        cr.execute('''select distinct emp.id as id 
        from res_groups_users_rel rgu 
        left join res_users u on(rgu.uid = u.id)
        left join resource_resource res_res on (res_res.user_id = u.id)
        left join hr_employee emp on (emp.resource_id = res_res.id) 
        where rgu.gid in %s  ''',
                    (tuple(g_ids), ))
        re=[ x['id'] for x in cr.dictfetchall() if x['id'] ]
        
        re = list ( set( re ) )
        return [('id','in',re)]



    _columns = {
        'bank_name':fields.char("Bank Name", size=32, readonly=True, states={'draft':[('readonly', False)]}),
        'home_1':fields.char("Home", size=32, readonly=True, states={'draft':[('readonly', False)]}),
        'home_2':fields.char("Home2", size=32, readonly=True, states={'draft':[('readonly', False)]}),
        'home_3':fields.char("Home3", size=32, readonly=True, states={'draft':[('readonly', False)]}),
        'home_4':fields.char("Home4", size=32, readonly=True, states={'draft':[('readonly', False)]}),
        'fname':fields.char(string="First Name", readonly=True, states={'draft':[('readonly', False)]}),
        'sname':fields.char(string="Second Name", readonly=True, states={'draft':[('readonly', False)]}),
        'tname':fields.char(string="Third Name", readonly=True, states={'draft':[('readonly', False)]}),
        'lname':fields.char(string="Last Name", readonly=True, states={'draft':[('readonly', False)]}),
        'city_id':fields.char("City", size=40, readonly=True, states={'draft':[('readonly', False)]}),
        'state_id':fields.many2one('res.country.state',"State", readonly=True, states={'draft':[('readonly', False)]}),
        'country':fields.many2one('res.country',"Country", readonly=True, states={'draft':[('readonly', False)]}),
        'nearer_family':fields.char("Address Nearer Family", size=40, readonly=True, states={'draft':[('readonly', False)]}),
        'family_phone':fields.char("Family Phone", size=40, readonly=True, states={'draft':[('readonly', False)]}),
        'lang2':fields.many2many('language',string='Language', required=False, readonly=False, states={'draft':[('readonly', False)]}),
	'lang': fields.selection(tools.scan_languages(),'Language'),	
	'employee_health_status': fields.many2many('employee.health',string='Employee Health Status', readonly=True, states={'draft':[('readonly', False)]}),
        #'section_id': fields.many2one('hr.degree.category',string="Section", store=True),
	'exp_nation_date' :fields.date('Nationality Export Date',  size=32, readonly=True, states={'draft':[('readonly', False)]}),
        'pass_exp_date' :fields.date('passport Export Date ',  size=32, readonly=True, states={'draft':[('readonly', False)]}),
        'inval_pass_date' :fields.date('Invalid passport Date ', readonly=True, states={'draft':[('readonly', False)]}),
        'nation_inval_date' :fields.date('Invalid National Date ', readonly=True, states={'draft':[('readonly', False)]}),
        'licence_no' :fields.char('Driving Licence No ', readonly=True, states={'draft':[('readonly', False)]}),
	'licen_exp_date' :fields.date('Licence Export Date', readonly=True, states={'draft':[('readonly', False)]}),
	'licen_inval_date' :fields.date('Licence Invalid Date', readonly=True, states={'draft':[('readonly', False)]}),
	'place_residence':fields.char('Place Residence', readonly=True, states={'draft':[('readonly', False)]}),
	'external_transfer':fields.selection([('delegation', 'Delegation'), ('loaning', 'Loaning'),('transfer', 'Transfer'), ('new', 'Employee')], 'External Transfer', readonly=True, states={'draft':[('readonly', False)]}),
	'transfer':fields.selection([('normal', 'Normal transmission'), ('delegate', 'Delegate transfer'),('final', 'Final transfer')], 'Transfer', readonly=True, states={'draft':[('readonly', False)]}),

    	'side':fields.char("Sides", size=40, readonly=True, states={'draft':[('readonly', False)]}),

    	'nation':fields.binary('attachments'),
    	'identity':fields.binary('attachments'),
    	'pass':fields.binary('attachments'),
    	'brth':fields.binary('attachments'),
    	'nation_serve':fields.binary('attachments'),
    	're_emp':fields.binary('attachments'),
    	'licen_data':fields.binary('attachments'),
    	'employement_date1':fields.date("Employement Date"), 
            'first_emp':fields.binary('attachments'),  
        'curr_uid': fields.function(_curr_id,type="boolean", string='current_user'),
        'curr_uid_hr': fields.function(_curr_id_hr, type="boolean", string='hr user'),
        'salary_suspend' : fields.boolean('Salary Suspend'),
        'substitution' : fields.boolean('Substitution'),
        'mile_allowance' : fields.boolean('Mile Allowance'),
        'active' : fields.boolean('Active'),
        'training_no':fields.char("Training Number"),
        'is_gs_m': fields.function(_is_gs_m,type="boolean", fnct_search=_is_gs_m_search),

        
    }

    

    

    def onchange_code_custom(self, cr, uid, ids, code, context={}):
        """
        Method check if the name contains spaces at its begining or ending and returns it without sapces 
        @param name: name of the payroll
        @return: name without spaces
        """
        vals={}
        if code!=False:
            vals={'emp_code':code.strip()}
        return {'value':vals}

    def onchange_start_date(self, cr, uid, ids, employment_date, context={}):
        vals = {}
        if employment_date!=False:
            vals={'employement_date1':employment_date}
        return {'value':vals}
    
    def name_change(self, cr, uid, ids, name, fname, sname, tname, lname, context=None):
        """
        create the full name from it's components'

        @param the name components
        @return: Dictionary of name value
        """
        new_name = ""
        fname = fname and fname.lstrip().rstrip() or ""
        sname = sname and sname.lstrip().rstrip() or ""
        tname = tname and tname.lstrip().rstrip() or ""
        lname = lname and lname.lstrip().rstrip() or ""
        if len(fname) > 0:
            new_name += fname+" "
        if len(sname) > 0:
            new_name += sname+" "
        if len(tname) > 0:
            new_name += tname+" "
        if len(lname) > 0:
            new_name += lname
        new_name = new_name.lstrip().rstrip()
        new_name = len(new_name) > 0 and new_name or name
        return {
            'value': {
                'name':new_name,
                }
            }
    
    def write(self, cr, uid, ids, vals, context=None):
        l = ['1','2','3','4','5','6','7','8','9','0']
        if 'fname' in vals or 'sname' in vals or 'tname' in vals or 'lname' in vals:
            for employee in self.browse(cr,uid,ids,context=context):
                fname = employee.fname
                sname = employee.sname
                tname = employee.tname
                lname = employee.lname
                if 'fname' in vals:
                    fname = vals['fname']

                if 'sname' in vals:
                    sname = vals['sname']

                if 'tname' in vals:
                    tname = vals['tname']

                if 'lname' in vals:
                    lname = vals['lname']
                new_name = ""
                fname = fname and fname.lstrip().rstrip() or ""
                sname = sname and sname.lstrip().rstrip() or ""
                tname = tname and tname.lstrip().rstrip() or ""
                lname = lname and lname.lstrip().rstrip() or ""
                if len(fname) > 0:
                    new_name += fname+" "
                if len(sname) > 0:
                    new_name += sname+" "
                if len(tname) > 0:
                    new_name += tname+" "
                if len(lname) > 0:
                    new_name += lname
                new_name = new_name.lstrip().rstrip()
                new_name = len(new_name) > 0 and new_name or ''
                vals['name'] = new_name

                for c in range(0,10):
                    if l[c] in vals['name']:
                        raise osv.except_osv(_('Error'), _('Name Should Not Contain Number'))
        
        if 'nation' in vals:
            ir_attachment = self.pool.get('ir.attachment')
            for id in ids:
                search_ids = ir_attachment.search(cr,uid,[('res_id','=',id),('res_model','=','hr.employee'),
                    ('field','=','nation'),])
                ir_attachment.write(cr,uid,search_ids,{'datas':vals['nation']})
                if not search_ids:
                    ir_attachment.create(cr,uid,{'name':'Nationality','datas':vals['nation'],
                    'res_model':'hr.employee','res_id':id,'field':'nation'},context=context)

        if 'identity' in vals:
            ir_attachment = self.pool.get('ir.attachment')
            for id in ids:
                search_ids = ir_attachment.search(cr,uid,[('res_id','=',id),('res_model','=','hr.employee'),
                    ('field','=','identity'),])
                ir_attachment.write(cr,uid,search_ids,{'datas':vals['identity']})
                if not search_ids:
                    ir_attachment.create(cr,uid,{'name':'Identification','datas':vals['identity'],
                    'res_model':'hr.employee','res_id':id,'field':'identity'},context=context)

        if 'pass' in vals:
            ir_attachment = self.pool.get('ir.attachment')
            for id in ids:
                search_ids = ir_attachment.search(cr,uid,[('res_id','=',id),('res_model','=','hr.employee'),
                    ('field','=','pass'),])
                ir_attachment.write(cr,uid,search_ids,{'datas':vals['pass']})
                if not search_ids:
                    ir_attachment.create(cr,uid,{'name':'Passport','datas':vals['pass'],
                    'res_model':'hr.employee','res_id':id,'field':'pass'},context=context)

        if 'brth' in vals:
            ir_attachment = self.pool.get('ir.attachment')
            for id in ids:
                search_ids = ir_attachment.search(cr,uid,[('res_id','=',id),('res_model','=','hr.employee'),
                    ('field','=','brth'),])
                ir_attachment.write(cr,uid,search_ids,{'datas':vals['brth']})
                if not search_ids:
                    ir_attachment.create(cr,uid,{'name':'Birthday Certificate','datas':vals['brth'],
                    'res_model':'hr.employee','res_id':id,'field':'brth'},context=context)

        if 'nation_serve' in vals:
            ir_attachment = self.pool.get('ir.attachment')
            for id in ids:
                search_ids = ir_attachment.search(cr,uid,[('res_id','=',id),('res_model','=','hr.employee'),
                    ('field','=','nation_serve'),])
                ir_attachment.write(cr,uid,search_ids,{'datas':vals['nation_serve']})
                if not search_ids:
                    ir_attachment.create(cr,uid,{'name':'Nation Service','datas':vals['nation_serve'],
                    'res_model':'hr.employee','res_id':id,'field':'nation_serve'},context=context)

        if 're_emp' in vals:
            ir_attachment = self.pool.get('ir.attachment')
            for id in ids:
                search_ids = ir_attachment.search(cr,uid,[('res_id','=',id),('res_model','=','hr.employee'),
                    ('field','=','re_emp'),])
                ir_attachment.write(cr,uid,search_ids,{'datas':vals['re_emp']})
                if not search_ids:
                    ir_attachment.create(cr,uid,{'name':'Reemployeement','datas':vals['re_emp'],
                    'res_model':'hr.employee','res_id':id,'field':'re_emp'},context=context)

        if 'first_emp' in vals:
            ir_attachment = self.pool.get('ir.attachment')
            for id in ids:
                search_ids = ir_attachment.search(cr,uid,[('res_id','=',id),('res_model','=','hr.employee'),
                    ('field','=','first_emp'),])
                ir_attachment.write(cr,uid,search_ids,{'datas':vals['first_emp']})
                if not search_ids:
                    ir_attachment.create(cr,uid,{'name':'First Employement','datas':vals['first_emp'],
                    'res_model':'hr.employee','res_id':id,'field':'first_emp'},context=context)
        if 'period' in vals or 'employment_date' in vals:
            rec = self.browse(cr,uid,ids[0])
            employment_date = 'employment_date' in vals and vals['employment_date'] or rec.employment_date
            period = 'period' in vals and vals['period'] or rec.period
            dt_from = employment_date and datetime.datetime.strptime(employment_date, DEFAULT_SERVER_DATE_FORMAT)
            date = DateTime.Parser.DateTimeFromString(employment_date)
            if period != 0:
                days = 0
                c = 0
                x = dt_from.month
                year = dt_from.year
                while c < period:
                    c += 1
                    if x in [1,3,5,7,8,10,12]:
                        days += 31
                    elif x in [2] and year % 4 == 0:
                        days += 29
                    elif x in [2] and year % 4 != 0:
                        days += 28
                    else:
                        days += 30
                    year = x == 12 and (year+1) or year
                    x = (x != 12) and (x+1) or 1
                vals['end_date'] = str(dt_from + datetime.timedelta(days - 1))
            else:
                vals['end_date'] = False
        #super(hr_employee,self).write(cr, uid, ids, vals, context)
        emp_write = super(hr_employee, self).write(cr, uid, ids, vals, context)
        update_field = [key for key in vals.keys() if key in ('payroll_id', 'degree_id', 'bonus_id', 'department_id', 'status', 'state', 'tax_exempted', 'category_ids', 'company_id', 'substitution', 'mile_allowance')]
        if update_field:
            self.write_employee_salary(cr, uid, ids, [])
        return emp_write
        #return True
            
    def create(self, cr, uid, vals, context=None):
        """
        Override create method to create a new user for the employee

        @return: super create method
        """
        ir_attachment = self.pool.get('ir.attachment')
        l = ['1','2','3','4','5','6','7','8','9','0']
                    
        if context is None:
            context = {}
        fname = vals['fname']
        sname = vals['sname']
        tname = vals['tname']
        lname = vals['lname']
        new_name = ""
        fname = fname and fname.lstrip().rstrip() or ""
        sname = sname and sname.lstrip().rstrip() or ""
        tname = tname and tname.lstrip().rstrip() or ""
        lname = lname and lname.lstrip().rstrip() or ""
        if len(fname) > 0:
            new_name += fname+" "
        if len(sname) > 0:
            new_name += sname+" "
        if len(tname) > 0:
            new_name += tname+" "
        if len(lname) > 0:
            new_name += lname
        new_name = new_name.lstrip().rstrip()
        new_name = len(new_name) > 0 and new_name or ''
        vals['name'] = new_name
        for c in range(0,10):
                    if l[c] in vals['name']:
                        raise osv.except_osv(_('Error'), _('Name Should Not Contain Number'))


        if 'period' in vals or 'employment_date' in vals:
            employment_date = vals['employment_date']
            period = vals['period']
            dt_from = employment_date and datetime.datetime.strptime(employment_date, DEFAULT_SERVER_DATE_FORMAT)
            date = DateTime.Parser.DateTimeFromString(employment_date)
            if period != 0:
                days = 0
                c = 0
                x = dt_from.month
                year = dt_from.year
                while c < period:
                    c += 1
                    if x in [1,3,5,7,8,10,12]:
                        days += 31
                    elif x in [2] and year % 4 == 0:
                        days += 29
                    elif x in [2] and year % 4 != 0:
                        days += 28
                    else:
                        days += 30

                    year = x == 12 and (year+1) or year
                    x = (x != 12) and (x+1) or 1
                vals['end_date'] = str(dt_from + datetime.timedelta(days - 1))
            else:
                vals['end_date'] = False

        id = super(hr_employee, self).create(cr, uid, vals, context=context)

        if vals.get('user_id',False):
            if vals['nation']:
                ir_attachment.create(cr,uid,{'name':'Nationality','datas':vals['nation'],
                    'res_model':'hr.employee','res_id':id,'field':'nation'},context=context)

            if vals['identity']:
                ir_attachment.create(cr,uid,{'name':'Identification','datas':vals['identity'],
                    'res_model':'hr.employee','res_id':id,'field':'identity'},context=context)

            if vals['pass']:
                ir_attachment.create(cr,uid,{'name':'Passport','datas':vals['pass'],
                    'res_model':'hr.employee','res_id':id,'field':'pass'},context=context)

            if vals['brth']:
                ir_attachment.create(cr,uid,{'name':'Birthday Certificate','datas':vals['brth'],
                    'res_model':'hr.employee','res_id':id,'field':'brth'},context=context)

            if vals['nation_serve']:
                ir_attachment.create(cr,uid,{'name':'Nation Service','datas':vals['nation_serve'],
                    'res_model':'hr.employee','res_id':id,'field':'nation_serve'},context=context)

            if vals['re_emp']:
                ir_attachment.create(cr,uid,{'name':'Reemployeement','datas':vals['re_emp'],
                    'res_model':'hr.employee','res_id':id,'field':'re_emp'},context=context)

            if vals['first_emp']:
                ir_attachment.create(cr,uid,{'name':'First Employement','datas':vals['first_emp'],
                    'res_model':'hr.employee','res_id':id,'field':'first_emp'},context=context)
            return id
        
        if vals['nation']:
            ir_attachment.create(cr,uid,{'name':'Nationality','datas':vals['nation'],
                'res_model':'hr.employee','res_id':id,'field':'nation'},context=context)

        if vals['identity']:
            ir_attachment.create(cr,uid,{'name':'Identification','datas':vals['identity'],
                'res_model':'hr.employee','res_id':id,'field':'identity'},context=context)

        if vals['pass']:
            ir_attachment.create(cr,uid,{'name':'Passport','datas':vals['pass'],
                'res_model':'hr.employee','res_id':id,'field':'pass'},context=context)

        if vals['brth']:
            ir_attachment.create(cr,uid,{'name':'Birthday Certificate','datas':vals['brth'],
                'res_model':'hr.employee','res_id':id,'field':'brth'},context=context)

        if vals['nation_serve']:
            ir_attachment.create(cr,uid,{'name':'Nation Service','datas':vals['nation_serve'],
                'res_model':'hr.employee','res_id':id,'field':'nation_serve'},context=context)

        if vals['re_emp']:
                ir_attachment.create(cr,uid,{'name':'Reemployeement','datas':vals['re_emp'],
                    'res_model':'hr.employee','res_id':id,'field':'re_emp'},context=context)
        if vals['first_emp']:
                ir_attachment.create(cr,uid,{'name':'First Employement','datas':vals['first_emp'],
                    'res_model':'hr.employee','res_id':id,'field':'first_emp'},context=context)

        
        return id
       
    def on_change_bank(self, cr, uid, ids, bank_account_id, context=None):
        """
        On change bank_account_id field value function gets the value of bank_name.

        @param bank_account_id: id of current bank_account
        @return: Dictionary of bank_name value
        """
        if not bank_account_id:
            return {
                'value': {
                    'bank_name':False
                    }
				}
        bank = self.pool.get('res.partner.bank').browse(cr, uid, bank_account_id, context=context)
        return {
            'value': {
                'bank_name':bank.bank_name
                },
        }
    
    def _default_country(self, cr, uid, context=None):
        if context is None:
            context = {}
        model_data = self.pool.get('ir.model.data')
        res = False
        try:
            res = model_data.get_object_reference(cr, uid, 'base', 'sd')[1]
        except ValueError:
            res = False
        return res

    def _default_country_birth(self, cr, uid, context=None):
        if context is None:
            context = {}
        res = False
        country_obj = self.pool.get('res.country')
        idss = country_obj.search(cr,uid,[('name','=','Sudan')])
        res = idss and idss[0] or res
        return res

    _defaults = {
        'country_id' : _default_country_birth,
        'external_transfer': 'new',
        'country' : _default_country_birth,
        'substitution': False,
        'salary_suspend': False,
        'curr_uid_hr' : _curr_user,
        'mile_allowance': False,
        'active':'1',
    
    }

    def name_search(self, cr, uid, name, args=None , operator='ilike', context=None, limit=100):
        """
        Method that overwrites name_search method Search for department (only departments 
        that requested trainings) and their display name.

        @param name: Object name to search
        @param args: List of tuples specifying search criteria
        @param operator: Operator for search criterion
        @param limit: Max number of records to return
        @return: Super name_search method 
        """
        if not args:
            args = []
        if context is None:
            context = {}
        if context.get('model') == 'hr.salary.addendum.percentage':
            if context.get('line_ids',[]):
                emp_ids = resolve_o2m_operations(cr, uid, self.pool.get('hr.salary.addendum.percentage'),
                                              context.get('line_ids'), ["employee_id"], context)
                values=[]
                for d in emp_ids:
                    if d.get('id',False):
                        values.append(d['employee_id'][0])
                    if not d.get('id',False):
                        values.append(d['employee_id'])
                    args.append(('id', 'not in', values))

        if context.get('model') == 'hr.holidays':
            holidays_obj = self.pool.get('hr.holidays')
            if context['active_id']:
                holiday_rec = holidays_obj.browse(cr,uid,context['active_id'])
                holidays_status_obj = self.pool.get('hr.holidays.status')
                date_from = holiday_rec.date_from
                date_to = holiday_rec.date_to
                state = ['draft','confirm','validate']
                emp_ids = []
                emp_ids.append(holiday_rec.employee_id.id)
                holiday_status_id = holidays_status_obj.search(cr,uid,['|',('absence', '=', False),('absence', '!=', True)])
                cr.execute('SELECT Distinct  employee_id '\
                      'FROM public.hr_holidays '\
                      'where date_from <= %s '\
                      'AND date_to >= %s '\
                      'AND holiday_status_id in %s',(date_from,date_to,tuple(holiday_status_id)))
                res = cr.dictfetchall()
                for h in res:
                    if h['employee_id'] not in emp_ids:
                        emp_ids.append(h['employee_id'])
                if emp_ids:

                    args.append(('id', 'not in', emp_ids))
        return super(hr_employee, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)

    def write_employee_salary(self, cr, uid, emp_ids, allow_deduct_list, date=None):
        """
        Method to compute all employee's allowances and deductions when create or write on employee object.
        @param emp_ids: List of employees ids
        @param allow_deduct_list: List of allowances/deductions ids
        @return: True
        """
        payroll_obj = self.pool.get('payroll')
        date = date and date or time.strftime('%Y-%m-%d')
        for emp in self.browse(cr, uid, emp_ids):
            allow_deduct_dict = payroll_obj.allowances_deductions_calculation(cr, uid, date, emp, {}, allow_deduct_list , False, [])
            payroll_obj.write_allow_deduct(cr, uid, emp.id, allow_deduct_dict['result'], emp_obj=True)
        return True


    def get_emp_analytic(self, cr, uid, employees,  dic, date=time.strftime('%Y-%m-%d'), context={}):
        analytic_obj = self.pool.get('hr.employee.analytic')
        allowance_obj = self.pool.get('hr.allowance.deduction')
        year = int(time.strftime('%Y'))
        month = int(time.strftime('%m'))
        analytic = False
        lines = {}
        length = len(employees)
        #print employees
        for e in employees:
           emp_ids = analytic_obj.search(cr,uid, [('employee_id','=',e.id),('year','=',year),('month','=',month)] )
           re = analytic_obj.read(cr, uid, emp_ids, ['analytic_account_id','percentage'])
           for x in re:
              analytic_id = x['analytic_account_id'][0]
              if lines.get(analytic_id,False) and lines[analytic_id]:
                   lines[analytic_id].update({
                     'amount':lines[analytic_id]['amount']+(employees[e] * x['percentage']/100) ,
                })
              else:
                   lines[e] = dic.copy()
                   lines[analytic_id].update({
                       'account_analytic_id':analytic_id,
                        'amount': (employees[e] * x['percentage']/100) ,
                       }) 

           if not emp_ids:
                if dic.has_key('allow_deduct_id'):
                    rec = allowance_obj.browse(cr,uid,dic['allow_deduct_id'])
                    analytic = rec.analytic_id and rec.analytic_id.id or False
                    if not analytic:
                         raise osv.except_osv(_('Warning!'),\
                        _('Please Set an analytic account for this allowance %s .') % (rec.name) )
                else:
                    analytic = e.department_id.analytic_account_id and e.department_id.analytic_account_id.id
                if not analytic:
                     raise osv.except_osv(_('Warning!'),\
                    _('Please Set an analytic account for this employee %s department.') % (e.name) )
                lines[e] = dic.copy()
                lines[e].update({
                           'account_analytic_id':analytic,
                            'amount': employees[e]  ,
                           }) 
        return lines.values()


class language(osv.Model):

    _name = "language"

    _columns = {
        'name':fields.char('Language', required=True),
    }

class employee_health(osv.Model):

    _name = "employee.health"
    _description = "Employee Health Status"

    _columns = {
        'name' : fields.char("Status Name", size=64),
        'code': fields.char('Code', size=64),
    }


class hr_employee_loan(osv.Model):

    _inherit = "hr.employee.loan"

    _track = {
        'state': {
            'hr_ntc_custom.mt_loan_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'hr_ntc_custom.mt_loan_requested': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'requested',
            'hr_ntc_custom.mt_loan_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'approved',
            'hr_ntc_custom.mt_loan_paid': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'paid',
            'hr_ntc_custom.mt_loan_rejected_suspend': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'suspend',
            'hr_ntc_custom.mt_loan_rejected': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'rejected',
        },
    }

    def get_refund(self, cr, uid, ids, loan_id, args,context=None) :
	res = {}
	payroll_obj= self.pool.get('payroll')
	addendum_refund = 0.0
	salary_refund = 0.0
	installment_amount = 0.0
	addendum_installment = 0.0
	for rec in self.browse(cr, uid, ids):
		loan_setting = rec.loan_id
		if rec.refund_from == 'salary' :
			salary_refund = rec.loan_amount
			addendum_refund = 0.0
		if rec.refund_from == 'addendum':
			addendum_refund = rec.loan_amount
			salary_refund = 0.0
		if rec.refund_from == 'both':
			paid_out = sum([arc.loan_amount for arc in rec.loan_arc_ids if arc.payment_type=='payment'])

			addendum_refund = rec.loan_amount + rec.addendum_plus - rec.salary_plus -paid_out
			salary_refund = addendum_refund + rec.salary_plus - rec.addendum_plus - paid_out
		#FIXME: addendum_install_no/addendum_installment
		addendum_install_no = rec.addendum_install_no >0 and rec.addendum_install_no  or 1
		total_installment = rec.total_installment  >0 and rec.total_installment  or 1
		###############
		installment_amount = salary_refund / total_installment 
		if rec.refund_from == 'both':
		    addendum_installment = rec.addendum_percentage * installment_amount  /100
		if rec.refund_from == 'addendum':
		    addendum_installment = addendum_refund / addendum_install_no
		self.write(cr, uid, ids, {'installment_amount':installment_amount,'addendum_install':addendum_installment})
		res.update({rec.id: {'addendum_refund': addendum_refund ,
                                             'salary_refund': salary_refund,
                                             'installment_amount':installment_amount,
                                              'addendum_install':addendum_installment}})
	return res
    _columns = {
	'salary_refund': fields.function(get_refund, method=True , string='Salary Refund', 
									store = {'hr.employee.loan': (lambda self, cr, uid, ids, c={}: ids, ['loan_id','addendum_plus',\
												'advance_amount','salary_plus','addendum_install_no','total_installment','addendum_percentage',\
												'loan_amount','refund_from'], 20)},multi='loan_id'),
	'addendum_refund': fields.function(get_refund, method=True, string="Addendum Refund", type='float', 
									store = {'hr.employee.loan': (lambda self, cr, uid, ids, c={}: ids, ['loan_id','addendum_plus',\
												'salary_plus','advance_amount','addendum_install_no','total_installment',\
												'loan_amount','addendum_percentage','refund_from'], 20)},multi='loan_id'),
    'state':fields.selection([('draft','Draft'),('requested','Waiting Manager of the Commission Approval'),('approved','Waiting for payment'),('rejected','Rejected'),
                                          ('transfered','Transfered'),('paid','Paid'),('suspend','Suspend'),('done','Done')],"State",readonly=True),
    'user_id': fields.many2one('res.users', "Manager user"),
    'url':fields.char('URL',size=156, readonly=True,),
    'active' : fields.boolean('Active'),
    }

    _defaults = {
            'active' : 1,
              } 


    def write(self, cr, uid, ids, vals, context=None):
        """
        Mehtod that updates holiday name by adding the date to the it 
        useful in the case of changing the holiday after the creation.

        @param vals: Dictionary contains the enterred values
        @return: Super write Mehtod
        """
        template_obj = self.pool.get('email.template')
        data_obj = self.pool.get('ir.model.data')
        rec = self.browse(cr,uid,ids[0])
        user_obj = self.pool.get('res.users')
        if rec.state in ['paid', 'done']:
            if not user_obj.has_group(cr, uid, 'base.group_loan_user'):
                raise osv.except_osv(_('ERROR'), _('Forbidden'))
        if vals.has_key('state') and rec.state != 'suspend':
            super(hr_employee_loan, self).write(cr, uid, ids, vals, context=context)
            result = self.check_manager_email(cr,uid,ids,context)
            return True
        else: 
            return super(hr_employee_loan, self).write(cr, uid, ids, vals, context=context)

    def check_manager_email(self, cr, uid, ids, context=None):
        template_obj = self.pool.get('email.template')
        data_obj = self.pool.get('ir.model.data')
        user_group_obj = self.pool.get('res.groups.users.rel')
        mail_template_id = data_obj.get_object_reference(cr, uid,'hr_ntc_custom', 'email_hr_loan')
        force_send = True
        for h in self.browse(cr, uid, ids, context=context):
            
            if h.state in ('requested','approved','paid'):
                user_ids = []
                group_id = False
                if h.state == 'requested' :
                    group_id = data_obj.get_object_reference(cr, uid,'base', 'group_loan_manager')
                if h.state == 'approved' :
                    group_id = data_obj.get_object_reference(cr, uid,'base', 'group_loan_user')
                if group_id:
                    cr.execute('SELECT g.uid as user_id ' \
                                'FROM public.res_groups_users_rel g ' \
                                'WHERE g.gid = %s', (group_id[1],) )
                    user_group_ids = cr.dictfetchall()

                    user_ids = [x['user_id'] for x in user_group_ids]
                if h.state in ('paid', 'approved'):
                    user_ids.append(h.employee_id.user_id.id)
                if user_ids:
                        user_ids.append(0)
                        cr.execute('SELECT hr_employee.id as emp_id, res_users.login as login, res_users.id as user_id, res_partner.email as email ' \
                            'FROM public.res_users, public.hr_employee, public.resource_resource, public.res_partner ' \
                            'WHERE hr_employee.resource_id = resource_resource.id '\
                            'AND resource_resource.user_id = res_users.id '\
                            'AND res_users.partner_id = res_partner.id '\
                            'AND res_users.id in %s', (tuple(user_ids),) )
                        res = cr.dictfetchall()
                        for r in res:
                            print "-----------------------res", r
                            cr.execute("update hr_employee_loan set user_id=%s where id=%s" , ( r['user_id'], h.id))
                            
                            base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')

                            query = {'db': cr.dbname}
                            fragment = {
                                'login': r['login'],
                                'model': 'hr.employee.loan',
                                'id': ids[0],
                            }
                            try:
                                self.pool.get('hr.employee.loan').check_access_rule(cr, r['user_id'], ids, 'read', context=context)
                                url = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
                                cr.execute("update hr_employee_loan set url=%s where id=%s" , (url, ids[0]))
                            except except_orm, e:
                                cr.execute("update hr_employee_loan set url=NULL where id=%s" %(ids[0]))

                            template_obj.send_mail(cr, uid, mail_template_id[1], h.id, force_send, context=context)
                        return True
            '''if h.state == 'requested' :
                group_id = data_obj.get_object_reference(cr, uid,'base', 'group_loan_manager')
                cr.execute('SELECT g.uid as user_id ' \
                            'FROM public.res_groups_users_rel g ' \
                            'WHERE g.gid = %s', (group_id[1],) )
                user_group_ids = cr.dictfetchall()

                user_ids = [x['user_id'] for x in user_group_ids]
                if user_ids:
                        user_ids.append(0)
                        cr.execute('SELECT hr_employee.id as emp_id, res_users.login as login, res_users.id as user_id, res_partner.email as email ' \
                            'FROM public.res_users, public.hr_employee, public.resource_resource, public.res_partner ' \
                            'WHERE hr_employee.resource_id = resource_resource.id '\
                            'AND resource_resource.user_id = res_users.id '\
                            'AND res_users.partner_id = res_partner.id '\
                            'AND res_users.id in %s', (tuple(user_ids),) )
                        res = cr.dictfetchall()
                        for r in res:
                            cr.execute("update hr_employee_loan set user_id=%s where id=%s" , ( r['user_id'], h.id))
                            
                            base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')

                            query = {'db': cr.dbname}
                            fragment = {
                                'login': r['login'],
                                'model': 'hr.employee.loan',
                                'id': ids[0],
                            }
                            try:
                                self.pool.get('hr.employee.loan').check_access_rule(cr, r['user_id'], ids, 'read', context=context)
                                url = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
                                cr.execute("update hr_employee_loan set url=%s where id=%s" , (url, ids[0]))
                            except except_orm, e:
                                cr.execute("update hr_employee_loan set url=NULL where id=%s" %(ids[0]))

                            template_obj.send_mail(cr, uid, mail_template_id[1], h.id, force_send, context=context)
                        return True
            
            if h.state == 'approved' :
                group_id = data_obj.get_object_reference(cr, uid,'base', 'group_loan_user')
                cr.execute('SELECT g.uid as user_id ' \
                            'FROM public.res_groups_users_rel g ' \
                            'WHERE g.gid = %s', (group_id[1],) )
                user_group_ids = cr.dictfetchall()
                user_ids = [x['user_id'] for x in user_group_ids]
                user_ids.append(h.employee_id.user_id.id)
                if user_ids:
                        user_ids.append(0)
                        cr.execute('SELECT hr_employee.id as emp_id, res_users.login as login, res_users.id as user_id, res_partner.email as email ' \
                            'FROM public.res_users, public.hr_employee, public.resource_resource, public.res_partner ' \
                            'WHERE hr_employee.resource_id = resource_resource.id '\
                            'AND resource_resource.user_id = res_users.id '\
                            'AND res_users.partner_id = res_partner.id '\
                            'AND res_users.id in %s', (tuple(user_ids),) )
                        res = cr.dictfetchall()
                        for r in res:
                            cr.execute("update hr_employee_loan set user_id=%s where id=%s" , ( r['user_id'], h.id))
                            
                            base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')

                            query = {'db': cr.dbname}
                            fragment = {
                                'login': r['login'],
                                'model': 'hr.employee.loan',
                                'id': ids[0],
                            }
                            try:
                                self.pool.get('hr.employee.loan').check_access_rule(cr, r['user_id'], ids, 'read', context=context)
                                url = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
                                cr.execute("update hr_employee_loan set url=%s where id=%s" , (url, ids[0]))
                            except except_orm, e:
                                cr.execute("update hr_employee_loan set url=NULL where id=%s" %(ids[0]))

                            template_obj.send_mail(cr, uid, mail_template_id[1], h.id, force_send, context=context)
                        return True

            if h.state == 'paid':
                user_ids = []
                """group_id = data_obj.get_object_reference(cr, uid,'base', 'group_loan_user')
                cr.execute('SELECT g.uid as user_id ' \
                            'FROM public.res_groups_users_rel g ' \
                            'WHERE g.gid = %s', (group_id[1],) )
                user_group_ids = cr.dictfetchall()
                user_ids = [x['user_id'] for x in user_group_ids]"""
                print "-------------------user_ids11111", user_ids,h.employee_id.user_id.id
                user_ids.append(h.employee_id.user_id.id)
                print "-------------------user_ids222", user_ids
                if user_ids:
                        user_ids.append(0)
                        cr.execute('SELECT hr_employee.id as emp_id, res_users.login as login, res_users.id as user_id, res_partner.email as email ' \
                            'FROM public.res_users, public.hr_employee, public.resource_resource, public.res_partner ' \
                            'WHERE hr_employee.resource_id = resource_resource.id '\
                            'AND resource_resource.user_id = res_users.id '\
                            'AND res_users.partner_id = res_partner.id '\
                            'AND res_users.id in %s', (tuple(user_ids),) )
                        res = cr.dictfetchall()
                        for r in res:
                            cr.execute("update hr_employee_loan set user_id=%s where id=%s" , ( r['user_id'], h.id))
                            
                            base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')

                            query = {'db': cr.dbname}
                            fragment = {
                                'login': r['login'],
                                'model': 'hr.employee.loan',
                                'id': ids[0],
                            }
                            try:
                                self.pool.get('hr.employee.loan').check_access_rule(cr, r['user_id'], ids, 'read', context=context)
                                url = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
                                cr.execute("update hr_employee_loan set url=%s where id=%s" , (url, ids[0]))
                            except except_orm, e:
                                cr.execute("update hr_employee_loan set url=NULL where id=%s" %(ids[0]))

                            template_obj.send_mail(cr, uid, mail_template_id[1], h.id, force_send, context=context)
                        return True'''


        return True

    def request_loan(self, cr, uid, ids, context=None):
        print "--------------request_loan"
        for loan in self.browse(cr, uid, ids, context=context):
            
            request_dict= self.request_loan_check(cr, uid,ids, loan.loan_id, loan.employee_id, loan.start_date, context=context)
            vals = {'loan_amount': request_dict.get('loan_amount',0),
                    'installment_amount': request_dict.get('installment_amount',0),
                    #'state': 'requested',
                    #'reject_reasons' : request_dict.get('reject_reasons',''),
            }
            print "---------------------vals", vals
               
            self.write(cr, uid,[loan.id],vals,context=context)
                
        return True
    
    def request_loan_check(self, cr, uid,ids, loan, employee, start_date, context=None):
        
        """
        Request loan for specific employee where it checks that the employee
        meets the conditions of the requested loan and the company general 
        trends in regard to loans if it violates one of them the request will
        be canceled.
        Could be rejected for following reasons:
        * Exceeding employment years or max percentage of department loan 
              or max no of Installments
        * Has been already taken, loan interference, payments exceeding 
          pension date, loan not allowed for the degree, salary is suspensed, 
          loans over allowed

        @return: True
        """
        rec = self.browse(cr, uid, ids[0], context=context)
        payroll_obj= self.pool.get('payroll')
        request_dict= {}
        #check reject_reasons 7:Loan Not Allowed for The Degree of Employee
        if not loan.degree_ids or \
                    (loan.degree_ids and employee.degree_id.id in [d.id for d in loan.degree_ids]):
                    
            all_loan_ids=self.search(cr, uid, [('employee_id','=',employee.id),
                                               ('state','not in',('draft','rejected'))])
            #check reject_reasons 9:Employee Loans Over Allowed Number                                    
            if not employee.company_id.allowed_number or \
                (len(all_loan_ids) <= employee.company_id.allowed_number):

                check_loan_ids=self.search(cr, uid, [('employee_id','=',employee.id),
                                                     ('state','not in',('draft','rejected'))])
                #check reject_reasons 4:Loan Limit is Once and Already Taken
                #if (loan.loan_limit=='one' and not check_loan_ids) or (loan.loan_limit=='unlimit'):
                if loan.loan_limit=='one' or loan.loan_limit=='unlimit':
                    counter = 0
                    if check_loan_ids:
                        crunt_loan_ids=self.search(cr, uid, [('id','=',check_loan_ids),('state','!=','done')])
                        counter=len(crunt_loan_ids)
                    #check reject_reasons 5:Interference Between same Loan Not Allowed
                    #if loan.loan_limit=='one' or (not check_loan_ids or (check_loan_ids and counter==0) or (check_loan_ids and loan.allow_interference)) :
                    if loan.loan_limit=='one' or loan.loan_limit=='unlimit' :
                        if not employee.payroll_id or not employee.bonus_id or not \
                           employee.bonus_id.basic_salary:
                            raise osv.except_osv(_('ERROR'), \
                                               _('Kindly make sure your selected employee/s salary configure correctly.'))
                        if loan.loan_type=='amount':
                            total_loan=loan.amount
                            install_amount= total_loan
                        else:
                            if loan.installment_type=='fixed':
                                total_loan=loan.amount
                                install_amount = loan.amount/loan.installment_no
                            else:
                                loan_based_salary=0.0
                                if loan.allowances_id:
				    if rec.loan_amount:
					loan_based_salary = rec.loan_amount

                                    else:
                                    	loan_based_salary=payroll_obj.allowances_deductions_calculation(cr,uid,start_date,employee,{}, [loan.allowances_id.id])
					loan_based_salary = loan_based_salary['total_allow']* loan.factor
                                total_loan=loan_based_salary
                                install_amount = total_loan/loan.installment_no 
                        emp_total_per_month= install_amount
                        if not employee.company_id.max_employee or not employee.company_id.max_department :
                            raise osv.except_osv(_('ERROR'), _('You Must Enter policy for Company'))
                        check_installment_ids=self.search(cr, uid, [('employee_id','=',employee.id),
                                                                    ('state','not in',('draft','done','rejected'))])
                        if check_installment_ids:
                            for c in self.browse(cr, uid, check_installment_ids):
                                emp_total_per_month += c.installment_amount
                        payroll=payroll_obj.allowances_deductions_calculation(cr,uid,start_date,employee,{}, [])
                        emp_payroll=payroll['total_allow'] + employee.bonus_id.basic_salary
                        request_dict.update({'payroll':payroll,'emp_total_per_month':emp_total_per_month - install_amount})
                        #check reject_reasons 3:Total Loans Installments for The Employee Exceed Max Percentage
                        if emp_total_per_month <= (emp_payroll*employee.company_id.max_employee)/100 :
                            dept_total_per_month=emp_total_per_month
                            dept_payroll = emp_payroll
                            check_dept_installments_ids=self.search(cr, uid,[ 
                                                          ('employee_id.department_id','=',employee.department_id.id),
                                                          ('state','not in',('done','rejected')),('id','!=',loan.id)])
                            if check_dept_installments_ids:
                                for c in self.browse(cr, uid,check_dept_installments_ids):
                                    if not c.employee_id.bonus_id.basic_salary:
                                        raise osv.except_osv(_('ERROR'), _('You Must Enter bonus for the employee %s in the same department')%(c.employee_id.name))
                                    dept_total_per_month+= c.installment_amount
                                    payroll=payroll_obj.allowances_deductions_calculation(cr,uid,start_date,c.employee_id,{}, [])
                                    dept_payroll+=payroll['total_allow'] +c.employee_id.bonus_id.basic_salary
                            #check reject_reasons 2:Total Loans Installments for The Department Exceed Max Percentage
                            if dept_total_per_month <= (dept_payroll*employee.company_id.max_department)/100:
                                check_employment_years=True
                                loan_year= datetime.datetime.strptime(start_date, '%Y-%m-%d').year
                                if loan.year_employment:
                                    employment_year= datetime.datetime.strptime(employee.employment_date, '%Y-%m-%d').year
                                    if int(loan_year) - int(employment_year) < loan.year_employment:
                                        check_employment_years=False 
                                #check reject_reasons 1:Employment years
                                if check_employment_years:
                                    if not employee.company_id.age_pension:
                                        raise osv.except_osv(_('ERROR'), _('You must enter age pension in HR configuration'))
                                    if not employee.birthday:
                                        raise osv.except_osv(_('ERROR'), _('You must enter employee birth date'))
                                    emp_age= datetime.datetime.strptime(employee.birthday, '%Y-%m-%d').year
                                    pension=employee.company_id.age_pension -(int(emp_age)-int(loan_year))
                                    #TODO: check when change_installment_no 
                                    #check reject_reasons 6:Pension Reached Before Finishing Loan Installments 
                                    if pension >= (loan.installment_no / 12 ):
                                        #check reject_reasons 8:Salary Suspend 
                                        if not employee.salary_suspend:
                                            request_dict.update({'loan_amount': total_loan, 
                                                'installment_amount': install_amount})
                                        else:
                                            request_dict.update({'reject_reasons' :'8'})
                                    else:
                                        request_dict.update({'reject_reasons' :'6'})
                                else:
                                    request_dict.update({'reject_reasons' :'1'})
                            else:
                                request_dict.update({'reject_reasons' :'2'})
                        else:
                            request_dict.update({'reject_reasons' :'3'})
                    else:
                        request_dict.update({'reject_reasons' :'5'})
                else:
                    request_dict.update({'reject_reasons' :'4'})
            else:
                request_dict.update({'reject_reasons' :'9'})
        else:
            request_dict.update({'reject_reasons' :'7'})
            
        
        return request_dict 




class hr_employee_qualification(osv.Model):

    _inherit = "hr.employee.qualification"

    _description = "employee's qualifications"

    def onchange_qualification(self, cr, uid, ids, emp_qual_type ,context=None):
        """ 
        return value of emp_qual_id, according to emp_qual_type.        
        @param pay_now: char payment method
        @param emp_qual_type: ID of  qualification type 
        @param emp_qual_id: ID of employee qualification
        @return: dictionary of values of fields to be updated 
        """ 
        domain = {'emp_qual_id':[('parent_id','=',emp_qual_type)],
                  }
        if emp_qual_type:
            return {'value': {'emp_qual_id':False} , 'domain': domain}
        else:
            return {'domain': domain}




    _columns = {

        'emp_qual_type' : fields.many2one('hr.qualification', 'Qualification type' ,required=True, ondelete="restrict" , readonly=True,  	 states={'draft':[('readonly', False)]}),
        'file':fields.binary('attachments', readonly=True, states={'draft':[('readonly', False)]}),

    }

    def create(self, cr, uid, vals, context=None):
        """
        Override create method to create a new qualification

        @return: super create method
        """
        ir_attachment = self.pool.get('ir.attachment')
        qual_name = self.pool.get('hr.qualification').browse(cr,uid,vals['emp_qual_id'],context=context).name
        id = super(hr_employee_qualification, self).create(cr, uid, vals, context=context)
        if vals['file']:
            ir_attachment.create(cr,uid,{'name':'file','datas':vals['file'],
                'res_model':'hr.employee.qualification','res_id':id,'field':'file'},context=context)

            ir_attachment.create(cr,uid,{'name':'qualification :'+qual_name,'datas':vals['file'],
                'res_model':'hr.employee','res_id':vals['employee_id'],'field':'qualification,'+str(id)},context=context)
        return id

    def write(self, cr, uid, ids, vals, context=None):
        if 'file' in vals:
            ir_attachment = self.pool.get('ir.attachment')
            for id in ids:
                obj = self.browse(cr,uid,id,context=context)
                qual_name = obj.emp_qual_id.name
                employee = obj.employee_id.id
                search_ids = ir_attachment.search(cr,uid,[('res_id','=',id),('res_model','=','hr.employee.qualification'),
                    ('field','=','file'),])
                ir_attachment.write(cr,uid,search_ids,{'datas':vals['file']})

                if not search_ids:
                    ir_attachment.create(cr,uid,{'name':'file','datas':vals['file'],
                        'res_model':'hr.employee.qualification','res_id':id,'field':'file'},context=context)

                search_ids = ir_attachment.search(cr,uid,[('res_id','=',employee),('res_model','=','hr.employee'),
                    ('field','=','qualification,'+str(id) ),])
                ir_attachment.write(cr,uid,search_ids,{'datas':vals['file']})
                
                if not search_ids:
                    ir_attachment.create(cr,uid,{'name':'qualification :'+qual_name,'datas':vals['file'],
                        'res_model':'hr.employee','res_id':employee,'field':'qualification,'+str(id)},context=context)
        super(hr_employee_qualification,self).write(cr, uid, ids, vals, context)
        return True
    def unlink(self, cr, uid, ids, context=None):
        ir_attachment = self.pool.get('ir.attachment')
        search_ids = ir_attachment.search(cr,uid,
                [('res_model','=','hr.employee.qualification'),
                 ('res_id','=',ids)],context=context )
        ir_attachment.unlink(cr,uid,search_ids,context=context)
        super(hr_employee_qualification, self).unlink(cr, uid,ids, context=context)

class hr_employee_family(osv.Model):

    _inherit = "hr.employee.family"

    _track = {
            'state': {
                'hr_ntc_custom.mt_family_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
                'hr_ntc_custom.mt_family_complete': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'complete',
                'hr_ntc_custom.mt_family_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'approved',
                'hr_ntc_custom.mt_family_rejected': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'rejected',
                'hr_ntc_custom.mt_family_to_stop': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'to_stop',
                'hr_ntc_custom.mt_family_stopped': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'stopped',
            },
        }

    _columns = {
        'state': fields.selection([('draft', 'Draft'), ('complete','Waiting HR Manager Approval'),
                                   #('review', 'Waiting HR Manager Approval'),
                                   ('approved', 'Approved'), ('rejected', 'Rejected'),
                                   ('to_stop', 'Waiting HR Manager Stop Approval') ,('stopped', 'Stopped')],
                                  'State', readonly=True),
        'file':fields.binary('attachments', readonly=True, states={'draft':[('readonly', False)]}),

    }



    _defaults = {
        'marital': 'married'
        }


    def create(self, cr, uid, vals, context=None):
        """
        Override create method to create a new family

        @return: super create method
        """
        ir_attachment = self.pool.get('ir.attachment')
        rel_name = vals['relation_name']
        id = super(hr_employee_family, self).create(cr, uid, vals, context=context)
        if vals['file']:
            ir_attachment.create(cr,uid,{'name':'file','datas':vals['file'],
                'res_model':'hr.employee.family','res_id':id,'field':'file'},context=context)

            ir_attachment.create(cr,uid,{'name':'relation :'+rel_name,'datas':vals['file'],
                'res_model':'hr.employee','res_id':vals['employee_id'],'field':'relation,'+str(id)},context=context)
        return id

    def write(self, cr, uid, ids, vals, context=None):
        if 'file' in vals:
            ir_attachment = self.pool.get('ir.attachment')
            for id in ids:
                obj = self.browse(cr,uid,id,context=context)
                rel_name = obj.relation_name
                employee = obj.employee_id.id
                search_ids = ir_attachment.search(cr,uid,[('res_id','=',id),('res_model','=','hr.employee.family'),
                    ('field','=','file'),])
                ir_attachment.write(cr,uid,search_ids,{'datas':vals['file']})

                if not search_ids:
                    ir_attachment.create(cr,uid,{'name':'file','datas':vals['file'],
                        'res_model':'hr.employee.family','res_id':id,'field':'file'},context=context)

                search_ids = ir_attachment.search(cr,uid,[('res_id','=',employee),('res_model','=','hr.employee'),
                    ('field','=','relation,'+str(id) ),])
                ir_attachment.write(cr,uid,search_ids,{'datas':vals['file']})
                
                if not search_ids:
                    ir_attachment.create(cr,uid,{'name':'relation :'+rel_name,'datas':vals['file'],
                        'res_model':'hr.employee','res_id':employee,'field':'relation,'+str(id)},context=context)
        if vals.has_key('state'):
            super(hr_employee_family, self).write(cr, uid, ids, vals, context=context)
            result = self.check_manager_email(cr,uid,ids,context)
            return True
        else:
            return super(hr_employee_family,self).write(cr, uid, ids, vals, context)
    
    def unlink(self, cr, uid, ids, context=None):
        ir_attachment = self.pool.get('ir.attachment')
        search_ids = ir_attachment.search(cr,uid,
                [('res_model','=','hr.employee.family'),
                 ('res_id','=',ids)],context=context )
        ir_attachment.unlink(cr,uid,search_ids,context=context)
        return super(hr_employee_family, self).unlink(cr, uid,ids, context=context)


    def check_manager_email(self, cr, uid, ids, context=None):
        template_obj = self.pool.get('email.template')
        data_obj = self.pool.get('ir.model.data')
        user_group_obj = self.pool.get('res.groups.users.rel')
        mail_template_id = data_obj.get_object_reference(cr, uid,'hr_ntc_custom', 'email_hr_process_archive')
        force_send = True
        for h in self.browse(cr, uid, ids, context=context):
            if h.state == 'complete' :
                send_mail(self, cr, uid, ids[0], 'base.group_hr_manager',u'تصديق الكفالة'.encode('utf-8'), u'هناك سجل كفالة في انتظار تصديق مدير الموارد البشرية'.encode('utf-8'), context=context)
            if h.state == 'to_stop' :
                send_mail(self, cr, uid, ids[0], 'base.group_hr_manager',u'تصديق الكفالة'.encode('utf-8'), u'هناك سجل كفالة في انتظار تصديق الوقف من مدير الموارد البشرية'.encode('utf-8'), context=context) 



class hr_family_relation(osv.Model):

    _inherit = "hr.family.relation"

    _columns = {
        'max_age' : fields.integer("Max Age For Ensuring", required=False),
        
    }



class hr_employee_delegation(osv.osv):
    """
    Inherits hr.employee.delegation to define how to deal with the saraly of the employee during the delegation period.
    """

    _inherit = 'hr.employee.delegation'

    _columns = {
        'period':fields.integer('Delegation Period'),
        'loan':fields.selection([('none','There is no procedure'),('procedure','There is procedure')]," Loans",readonly=True, states={'draft':[('readonly',False)]}),
        'state': fields.selection([('draft', 'Draft'), ('complete', 'Wating Department Manager Recommendation'),
                                   ('confirm', 'Wating General Department Manager Recommendation'),
                                   ('general_dep', 'Waiting HR and Financial Manager Approve'),
                                   ('hr_finance', 'Waiting General Manager Approve'),
                                   ('approve', 'Approve'),
                                   ('cancel', 'Cancel'),('done', 'Done')],'State', readonly=True),
    }

    _defaults = {
        'state' : 'draft', 
        }


    def check_general_dep_manager(self, cr, uid, ids, context=None):
        for h in self.browse(cr, uid, ids, context=context):
            user_id = h.employee_id.user_id.id
            flag = self.pool.get('res.users').has_group(cr, user_id, 'base_custom.group_general_department_manager')
            if flag:
                  return True
            else:
                  return False

    def manager(self, cr, uid, ids, context=None):
        for h in self.browse(cr, uid, ids, context=context):
            dep_cat = h.employee_id.department_id.cat_id
            parent_dep = h.employee_id.department_id.parent_id

            if h.state == 'complete':
                if dep_cat.category_type == 'section':
                    if h.employee_id.department_id.parent_id.manager_id.user_id.id == uid:
                        return True
                    else:
                        raise osv.except_osv(_('Warning!'),_('You are not this employee department manager'))
                        return False

                elif dep_cat.category_type == 'department' and h.employee_id.department_id.manager_id.user_id.id == h.employee_id.user_id.id:
                    if h.employee_id.department_id.parent_id.manager_id.user_id.id == uid:
                        return True
                    else:
                        raise osv.except_osv(_('Warning!'),_('You are not this employee department manager'))
                        return False 
                elif dep_cat.category_type == 'department' and h.employee_id.department_id.manager_id.user_id.id != h.employee_id.user_id.id:
                    if h.employee_id.department_id.manager_id.user_id.id == uid:
                        return True
                    else:
                        raise osv.except_osv(_('Warning!'),_('You are not this employee department manager'))
                else:
                    if dep_cat.category_type == 'general_dep':
                        if h.employee_id.department_id.manager_id.user_id.id == uid:
                            return True
                        else:
                            raise osv.except_osv(_('Warning!'),_('You are not this employee general department manager'))
                    return False

            if h.state == 'confirm':
                parent_dep = h.employee_id.department_id.parent_id
                if dep_cat.category_type == 'section':
                    if parent_dep and parent_dep.parent_id and parent_dep.parent_id.manager_id and parent_dep.parent_id.manager_id.user_id.id == uid:
                        return True
                    else:
                        raise osv.except_osv(_('Warning!'),_('You are not this employee general department manager'))
                        return False

                if dep_cat.category_type == 'department':
                    if parent_dep and parent_dep.manager_id and parent_dep.manager_id.user_id.id == uid:
                        return True
                    else:
                        raise osv.except_osv(_('Warning!'),_('You are not this employee general department manager'))
                        return False

                if dep_cat.category_type == 'general_dep':
                    if h.employee_id.department_id.manager_id.user_id.id == uid:
                        return True
                    else:
                        raise osv.except_osv(_('Warning!'),_('You are not this employee general department manager'))
                        return False


        return False

    def onchange_period(self,cr,uid,ids,period,start_date):
        vals = {}
        if period != 0 and start_date:
            date = DateTime.Parser.DateTimeFromString(start_date)
            days = 0
            c = 0
            x = date.month
            year = date.year
            while c < period:
                c += 1
                c1 = 0
                while c1 < 12:
                    c1 += 1
                    if x in [1,3,5,7,8,10,12]:
                        days += 31
                    elif x in [2] and year % 4 == 0:
                        days += 29
                    elif x in [2] and year % 4 != 0:
                        days += 28
                    else:
                        days += 30

                    year = x == 12 and (year+1) or year
                    x = (x != 12) and (x+1) or 1
            vals['end_date'] = str(date + datetime.timedelta(days - 1))

        return {'value':vals}

    def onchange_loan(self,cr,uid,ids,loan,loan_emp,employee_id):
        vals = {}
        loan_obj = self.pool.get('hr.employee.loan')

        if loan and loan == 'procedure' and employee_id:
            idss = loan_obj.search(cr,uid,[('employee_id','=',employee_id)])
            vals['loan_emp'] = idss

        if loan and loan == 'none':
            vals['loan_emp'] = False 
        return {'value':vals}

    def check_loan(self, cr, uid, ids, context=None):
        message = ''
        emp_loan_obj = self.pool.get('hr.employee.loan')
        for r in self.browse(cr, uid, ids):
            if r.loan!='none':
                state=['done','rejected']
                loans=emp_loan_obj.search(cr,uid,[('end_date', '>=', r.start_date),('start_date', '<=', r.end_date),('state','not in',state),('employee_id','=',r.employee_id.id)],context=context)
                if loans:
                    message = _('This employee has loan')
            if message:
                if not r.message:
                    cr.execute('update hr_employee_delegation set message=%s where id=%s', (message, r.id))
                return False
        return True

    
    def create(self, cr, uid, vals, context=None):
        if 'period' in vals or 'start_date' in vals:
            period = vals['period']
            date = DateTime.Parser.DateTimeFromString(vals['start_date'])
            if period != 0:
                days = 0
                c = 0
                x = date.month
                year = date.year
                while c < period:
                    c += 1
                    c1 = 0
                    while c1 < 12:
                        c1 += 1
                        if x in [1,3,5,7,8,10,12]:
                            days += 31
                        elif x in [2] and year % 4 == 0:
                            days += 29
                        elif x in [2] and year % 4 != 0:
                            days += 28
                        else:
                            days += 30

                        year = x == 12 and (year+1) or year
                        x = (x != 12) and (x+1) or 1
                vals['end_date'] = str(date + datetime.timedelta(days - 1))
        
        return super(hr_employee_delegation, self).create(cr, uid, vals, context)


    def write(self, cr, uid, ids, vals, context=None):
        if 'period' in vals or 'start_date' in vals:
            rec = self.browse(cr,uid,ids[0])
            start_date = vals.has_key('start_date') and vals['start_date'] or rec.start_date
            period = rec.period
            if vals.has_key('period'):
                period = vals['period']
            date = DateTime.Parser.DateTimeFromString(start_date)
            if period != 0:
                days = 0
                c = 0
                x = date.month
                year = date.year
                while c < period:
                    c += 1
                    c1 = 0
                    while c1 < 12:
                        c1 += 1
                        if x in [1,3,5,7,8,10,12]:
                            days += 31
                        elif x in [2] and year % 4 == 0:
                            days += 29
                        elif x in [2] and year % 4 != 0:
                            days += 28
                        else:
                            days += 30

                        year = x == 12 and (year+1) or year
                        x = (x != 12) and (x+1) or 1
                vals['end_date'] = str(date + datetime.timedelta(days - 1))        
        return super(hr_employee_delegation, self).write(cr, uid, ids, vals, context)


class hr_process_archive(osv.osv):

    _inherit ='hr.process.archive'
    _track = {
        'state': {
            'hr_ntc_custom.mt_process_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'hr_ntc_custom.mt_process_draft1': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft1',
            'hr_ntc_custom.mt_process_hr_manager': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'hr_manager',
            'hr_ntc_custom.mt_process_general_manag': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'general_manag',
            'hr_ntc_custom.mt_process_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'approved',
            'hr_ntc_custom.mt_process_cancel': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
        },
    }

    def _degree_level(self, cr, uid, ids, name, args, context=None):
        result = {}
        degree_obj = self.pool.get('hr.salary.degree')  
        reads = self.read(cr, uid, ids, ['reference'], context=context)
        for rec in reads:
            level=0
            (model_name, id) = rec['reference'].split(',')   
            if model_name  == 'hr.salary.degree':
                d = degree_obj.browse(cr,uid,id)
                #o = degree_obj.read(cr, uid, [id],['sequence'])
                #sequence = o and o[0]['sequence']
                sequence = d.sequence and d.sequence
                if sequence <= 3:
                    level = 1
                elif sequence >= 4 and sequence <=6:
                    level = 2
                else:
                    level = 3 
            result[rec['id']] = level
        return result
    

    _columns = {

        'degree_level': fields.function(_degree_level, string='Degree level'),
        'user_id': fields.many2one('res.users', "user"),
        'url':fields.char('URL',size=156, readonly=True,),
        'state': fields.selection([('draft', 'Draft'), ('draft1', 'Waiting HR Manager Approve'),
                                   ('hr_manager', 'Waiting HR and Financial Manager Approval'),
                                   #('hr_finance', 'Waiting Reviewer Approval'),
                                   ('general_manag', 'Waiting General Manager Approve'),
                                   #('implement', 'Waiting HR Implementation'),
                                   ('approved', 'Approved'),
                                   ('cancel', 'Cancel')],'State', select=True, readonly=True),
    }

    def unlink(self, cr, uid, ids, context=None):
        for record in self.browse(cr,uid,ids,context=context):
            if record.state not in ['draft', 'cancel']:
                raise osv.except_osv(_('Error'), _('the record have to be in draft state to be deleted!'))
        
        return super(hr_process_archive, self).unlink(cr, uid,ids, context=context)   


    def write(self, cr, uid, ids, vals, context=None):
        """
        Mehtod that updates holiday name by adding the date to the it 
        useful in the case of changing the holiday after the creation.

        @param vals: Dictionary contains the enterred values
        @return: Super write Mehtod
        """
        template_obj = self.pool.get('email.template')
        data_obj = self.pool.get('ir.model.data')
        
        if vals.has_key('state'):
            super(hr_process_archive, self).write(cr, uid, ids, vals, context=context)
            result = self.check_manager_email(cr,uid,ids,context=context)
            return True
        else: 
            return super(hr_process_archive, self).write(cr, uid, ids, vals, context=context)

    def check_manager_email(self, cr, uid, ids, context=None):
        template_obj = self.pool.get('email.template')
        data_obj = self.pool.get('ir.model.data')
        user_group_obj = self.pool.get('res.groups.users.rel')
        mail_template_id = data_obj.get_object_reference(cr, uid,'hr_ntc_custom', 'email_hr_process_archive')
        force_send = True
        for h in self.browse(cr, uid, ids, context=context):
            dep_cat = h.employee_id.department_id.cat_id
            parent_dep = h.employee_id.department_id.parent_id
            
            if h.state == 'draft1' :
                send_mail(self, cr, uid, ids[0], 'base.group_hr_manager',u'تصديق نقل موظف'.encode('utf-8'), u'هناك سجل كفالة في انتظار تصديق مدير الموارد البشرية'.encode('utf-8'), context=context)
            if h.state == 'hr_manager' :
                send_mail(self, cr, uid, ids[0], 'base_custom.group_general_hr_manager',u'تصديق علاوة سنوية/ترقية'.encode('utf-8'), 
                                            u'هناك سجل علاوة سنوية/ترقية في انتظار تصديق مدير اﻹدارة العامة للموارد البشرية و المالية'.encode('utf-8'), context=context)
            
            if h.state == 'general_manag' :
                send_mail(self, cr, uid, ids[0], 'base_custom.group_account_general_manager',u'تصديق ترقية'.encode('utf-8'), 
                                            u'هناك سجل ترقية موظف في انتظار تصديق المدير العام'.encode('utf-8'), context=context)


        return True


    def check_promotion_type(self, cr, uid, ids, context=None):
        check = False
        for row in self.read(cr, uid, ids, context=context):
            (model_name, id) = row['reference'].split(',')
            if model_name  == 'hr.department' or model_name  == 'hr.job':
                check = True

        return check

    def check_promotion_type_two(self, cr, uid, ids, context=None):
        check = False
        for row in self.read(cr, uid, ids, context=context):
            (model_name, id) = row['reference'].split(',')
            if model_name  == 'hr.salary.degree':
                check = True

        return check

        

class hr_department_cat(osv.Model):

    _inherit = 'hr.department.cat'


    _columns = {
        'category_type': fields.selection([('section','Section'),('department','Department'),
                                            ('general_dep','General Department'),
                                            ('unit','Unit for General Manager'),
                                            ('high_dep','Higher Department')],'Category Type'),
   }


class hr_employee_reemployment(osv.osv):

    _inherit ='hr.employee.reemployment'

    _columns = {
        'state': fields.selection( [('draft', 'Draft'),
                                    ('complete', 'Waiting HR and Financial Manager Approve'), 
                                    ('confirm', 'Waiting General Manager Approve'),
                                    ('approve', 'Approve'),('done', 'Done'),('cancel', 'Cancel')], 'State', readonly=True),
        
    }



class hr_job(osv.osv):

    _inherit ='hr.job'

    def _no_of_employee(self, cr, uid, ids, name, args, context=None):
        """
        Method to set the numer of employees occupying the job and the free available positions.
    
        @return: dictionary of fields value to be updated
        """
        res = {}
        for job in self.browse(cr, uid, ids, context=context):
            nb_employees = len([e.id for e in job.employee_ids if e.state != 'refuse' and e.employee_type in('employee','contractor')])
            if job.no_of_recruitment != 0.0 :
                job.no_of_recruitment = job.no_of_recruitment - nb_employees
            res[job.id] = {
                'no_of_employee': nb_employees,
                'expected_employees': job.no_of_recruitment,
                          }
        return res

    def _get_job_position(self, cr, uid, ids, context=None):
        """
        Count the numer of employees in the job

        @return: list of employee IDs
        """
        res = []
        for employee in self.pool.get('hr.employee').browse(cr, uid, ids, context=context):
            if employee.job_id and employee.state != 'refuse':
                res.append(employee.job_id.id)
        return res

    _columns = {
        'employee_ids': fields.one2many('hr.employee', 'job_id', 'Employees', domain=[('state', '=', 'approved')]),
        'dep_ids':fields.many2many('hr.department', 'dep_job_rel', 'job_id','department_id', 'Department'),
        'no_of_employee': fields.function(_no_of_employee, string="Current Number of Employees",
            store={
                'hr.employee': (_get_job_position, ['job_id','state'], 10),
                'hr.job': (lambda self, cr, uid, ids, c=None: ids, ['no_of_recruitment'], 10),
             }, help='Number of employees currently occupying this job position.', multi='no_of_employee'),
        'course_ids':fields.many2many('hr.training.course', 'course_job_rel', 'job_id','course_id', 'Courses'),

        
    }



class hr_job_wiz(osv.osv_memory):

    _name ='hr.job.wiz.update'


    def update_depertment(self,cr,uid,ids,context):
        """
        Method that creates records for allowance/deduction that contain the amount of allowance/deduction for each degree.
        @return: dictionary
        """
        job_obj = self.pool.get('hr.job')
        for job in context['active_ids']:
            dep = [] 
            dep_ids = []
            dep_tuple = []
            rec = job_obj.browse(cr,uid,job)
            dep_ids += rec.dep_ids and [x.id for x in rec.dep_ids] or []
            for emp in rec.employee_ids:
                if emp.department_id.id not in dep:
                    dep.append(emp.department_id.id)
            if dep:
                for d in dep:
                    if d not in dep_ids:
                        dep_ids.append(d)
                        dep_tuple.append((job,d))
                        rec.dep_ids.append(job_obj.browse(cr,uid,d))
                        cr.execute("INSERT INTO dep_job_rel(job_id,department_id) VALUES (%s,%s)",(job,d,))

        return True

    def update_degree(self,cr,uid,ids,context):
        """
        Method that creates records for allowance/deduction that contain the amount of allowance/deduction for each degree.
        @return: dictionary
        """
        job_obj = self.pool.get('hr.job')
        date = time.strftime('%Y-%m-%d')
        employee_substitution_obj = self.pool.get('hr.employee.substitution')
        for job in context['active_ids']:
            degree = [] 
            degree_ids = []
            degree_tuple = []
            rec = job_obj.browse(cr,uid,job)
            degree_ids += rec.degree_ids and [x.id for x in rec.degree_ids] or []
            print "--------------------degree_ids", degree_ids
            for emp in rec.employee_ids:
                substitue_ids = employee_substitution_obj.search(cr, uid, ['|', ('end_date', '>=', date), ('end_date', '=', False), 
                        ('employee_id', '=', emp.id), ('start_date', '<=', date)])
                if substitue_ids:
                    sub_record = employee_substitution_obj.browse(cr, uid, substitue_ids[0])
                    sub_degree = sub_record.degree_id.name
                    if sub_record.degree_id.id not in degree:
                        degree.append(sub_record.degree_id.id)
                else:
                    if emp.degree_id.id not in degree:
                        degree.append(emp.degree_id.id)
            if degree:
                for d in degree:
                    if d not in degree_ids:
                        degree_ids.append(d)
                        degree_tuple.append((job,d))
                        rec.dep_ids.append(job_obj.browse(cr,uid,d))
                        cr.execute("INSERT INTO job_degree_rel(degree_id,job_id) VALUES (%s,%s)",(job,d,))

        return True

    def update_job_dep_num(self,cr,uid,ids,context):
        """
        Method that creates records for allowance/deduction that contain the amount of allowance/deduction for each degree.
        @return: dictionary
        """
        job_obj = self.pool.get('hr.job')
        dep_obj = self.pool.get('department.jobs')
        for job in context['active_ids']:
            dep = [] 
            dep_ids = []
            val = []
            dep_ids1 = []
            val1 = []
            dep_tuple = []
            dep_dic = {}
            rec = job_obj.browse(cr,uid,job)
             
            dep_ids += rec.dep_ids and [x.id for x in rec.dep_ids] or []
            val += rec.dep_ids and [0 for c in dep_ids] or []
            print "----------------rec.department_ids", rec.deparment_ids
            dep_ids1 += rec.deparment_ids and [x.department_id.id for x in rec.deparment_ids] or []
            val1 += rec.deparment_ids and [x.id for x in rec.deparment_ids] or []
            dep_dic = dict(zip(dep_ids,val))
            dep_dic1 = dict(zip(dep_ids1,val1))
             
            for emp in rec.employee_ids:
                if dep_dic.has_key(emp.department_id.id):
                    dep_dic[emp.department_id.id] += 1
            vals = dep_dic.values()
            key = dep_dic.keys()

            if key:
                for k in key:
                    if dep_dic1.has_key(k): 
                        dep_obj.write(cr,uid,[dep_dic1[k]],{'no_emp':dep_dic[k]},context)
                    else:
                        datal={
                        'department_id': k,
                        'no_emp': dep_dic[k],
                        'job': job,
                        }
                        dep_obj.create(cr,uid,datal,context)

        return True


class hr_department(osv.osv):

    _inherit ='hr.department'

    _columns = {
        'job_ids':fields.many2many('hr.job', 'dep_job_rel', 'department_id', 'job_id', 'Job'),
        'active' : fields.boolean('Active'),
        
    }

    _defaults = {
        'active' : 1, 
        }

#----------------------------------------------------------
# Inherit res_partner_bank Class
#----------------------------------------------------------
class res_partner_bank(osv.Model):
    """
    Inherit res partner bank model to do constraint in unlink method
    """
    _inherit = "res.partner.bank"

    def unlink(self, cr, uid, ids, context=None):
        """
        If partner bank already selected in hr.employee
        @return: super unlink() method
        """
        employee_ids = self.pool.get('hr.employee').search(cr, uid,[('bank_account_id','in',ids)], context=context)
        if employee_ids:
            raise osv.except_osv(_('Error'), _('You cann\'t delete this bank account because is related with employee'))
        return super(res_partner_bank, self).unlink(cr, uid, ids, context=context)
    

'''class res_users(osv.Model):

    _inherit = "res.users"

    _name = "res.users"

    def write(self, cr, uid, ids, values,context={}):
        
        res = super(res_users, self).write(cr, uid, ids, values, context)
        for user in self.browse(cr, uid, ids, context):
            user.alias_id.write({'alias_name':'erpmail'})
        return res'''


    
