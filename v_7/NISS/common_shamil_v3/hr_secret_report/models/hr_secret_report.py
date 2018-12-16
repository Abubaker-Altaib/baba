# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from mx import DateTime
import time
from datetime import datetime
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import netsvc
import openerp.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta
import calendar
from openerp.addons.account_voucher.account_voucher import resolve_o2m_operations

class hr_secret_report(osv.Model):
    _name = "hr.secret.report.process"

    _description = "Hr Secret Report Process"

    Additional_degree = [
        ('0','0'),
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
        ('5','5'),
        ('6','6'),
        ('7','7'),
        ('8','8'),
        ('9','9'),
        ('10','10'),
        ]

    Final_eval = [
        ('excellent','Excellent'),
        ('v_good','Very Good'),
        ('good','Good'),
        ('middle','Middle'),
        ('u_middle','Under Middle'),
        ]

    Report_class = [
        ('satisfied','Satisfied'),
        ('not_satisfied','Not Satisfied')

        ]

    _columns = {
        'employee_id': fields.many2one('hr.employee', string='Employee'),
        'degree_id': fields.many2one('hr.salary.degree', string="Degree"),
        'department_id': fields.many2one('hr.department', string="Department"),
        'job_id': fields.many2one('hr.job', string="Job"),
        #'degree_id': fields.many2one('hr.salary.degree', string="Degree"),
        #'degree_id': fields.related('employee_id', 'degree_id', string="Degree", type="many2one", relation="hr.salary.degree"),
        'birthday': fields.date("Date of Birth"),
        'marital': fields.selection([('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('divorced', 'Divorced')], 'Marital Status'),
        'employment_date' : fields.date('Employement Date'),
        'date': fields.date('Date'),
        'year': fields.integer('Year'),
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], 'State'),
        'personal_character': fields.one2many('hr.secret.report.personal.character','secret_report_id',string="Personal Characteristic", domain=[('part','=','1')] ),
        'inspector_performance_character': fields.one2many('hr.secret.report.personal.character','secret_report_id',string="Inspector Performance", domain=[('part','=','2')]),
        'job_recommandation': fields.one2many('hr.secret.report.personal.character','secret_report_id',string="Job Recommandation", domain=[('part','=','3')]),
        'general_recommandation': fields.one2many('hr.secret.report.personal.character','secret_report_id',string="General Recommandation", domain=[('part','=','4')]),
        'supreme_recommandation': fields.text('Supreme Commander'),
        'direct_recommandation': fields.text('Direct Leader'), 
        'supreme_comment': fields.text('Supreme Commander Comment'),
        'direct_comment': fields.text('Direct Leader Comment'), 
        'direct_leader_id': fields.many2one('hr.employee', string='Name'),
        'direct_leade_degree_id': fields.many2one('hr.salary.degree', string="Degree"),
        'direct_leader_date': fields.date('Date'),
        'supreme_leader_id': fields.many2one('hr.employee', string='Name'),
        'supreme_leade_degree_id': fields.many2one('hr.salary.degree', string="Degree"),
        'supreme_leader_date': fields.date('Date'),
        'supreme_general_recommandation': fields.text('Supreme Commander Recommandation'),
        'direct_general_recommandation': fields.text('Direct Leader Recommandation'),
        'direct_add_grade': fields.selection(Additional_degree, 'Direct Leader'),
        'supreme_add_grade': fields.selection(Additional_degree, 'Supreme Commander'), 
        'direct_final_eval': fields.selection(Final_eval, 'Direct Leader'),
        'supreme_final_eval': fields.selection(Final_eval, 'Supreme Commander'),
        'direct_report_class': fields.selection(Report_class, 'Direct Leader'),
        'supreme_report_class': fields.selection(Report_class, 'Supreme Commander'), 
        'branch_manager_comment': fields.text('Comment of the Director of the Officers Affairs Branch'),
        'deputy_manager_comment': fields.text('Mr deputy general manager'),
        'general_manager_comment': fields.text('Mr general manager'),
        'efficiency_barriers': fields.text('Has the efficiency barriers passed to the next level'),
        'foreign_language': fields.text('Does he know a foreign language and its level'),
        'local_language': fields.text('Does he know a local language and its level'),
        'report_knowledge': fields.text('Was the report based on direct knowledge and communication'),
        'report_assesment': fields.text('Was the report based on the officers assessment through his performance'),
        'company_id': fields.many2one('res.company','company'),
    }

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults = {
        'state': 'draft',
        'date': time.strftime('%Y-%m-%d'),
        'year': int(time.strftime('%Y')),
        'company_id' : _default_company,
    }

    def check_unique(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if there is a record with the same name and part

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            domain = [('employee_id', '=', rec.employee_id.id),('year', '=', rec.year),('id','!=',rec.id)]
            
            idss = self.search(cr,uid, domain)
            if idss:
                raise osv.except_osv(_('ERROR'), _('Report should be unique per employee and year '))
        return True

    _constraints = [
         (check_unique, '', []),
    ]

    def _personal_character_fnct(self, cr, uid, context=None):
        character_obj = self.pool.get('hr.secret.report.character')
        personal_character_list = []
        
        character_ids = character_obj.search(cr, uid, [('part','=','1'),('load','=',True)], order="sequence")
        for x in character_ids:
            personal_character_dict = {
            'name': x,
            'direct': False,
            'supreme': False,
            'part': '1',
            }
            personal_character_list.append(personal_character_dict)
        
        return personal_character_list

    def _inspector_performance_character_fnct(self, cr, uid, context=None):
        character_obj = self.pool.get('hr.secret.report.character')
        inspector_performance_character_list = []
        character_ids = character_obj.search(cr, uid, [('part','=','2'),('load','=',True)], order="sequence")
        for x in character_ids:
            inspector_performance_character_dict = {
            'name': x,
            'direct': False,
            'supreme': False,
            'part': '2',
            }
            inspector_performance_character_list.append(inspector_performance_character_dict)
        
        return inspector_performance_character_list

    

    def _job_recommandation_fnct(self, cr, uid, context=None):
        character_obj = self.pool.get('hr.secret.report.character')
        job_list = []
        character_ids = character_obj.search(cr, uid, [('part','=','3'),('load','=',True)], order="sequence")
        for x in character_ids:
            job_recomm_dict = {
            'name': x,
            'direct_answer': False,
            'supreme_answer': False,
            'part': '3',
            }
            job_list.append(job_recomm_dict)
        
        return job_list

    def _general_recommandation_fnct(self, cr, uid, context=None):
        character_obj = self.pool.get('hr.secret.report.character')
        recomm_list = []
        character_ids = character_obj.search(cr, uid, [('part','=','4'),('load','=',True)], order="sequence")
        for x in character_ids:
            recomm_dict = {
            'name': x,
            'direct_answer': False,
            'supreme_answer': False,
            'part': '4',
            }
            recomm_list.append(recomm_dict)
        
        return recomm_list


    def default_get(self, cr, uid, fields, context=None):
        """
        overwite the super method to load report charcaterstics from the configuration based on 
        the characterstic part
        """
        if context is None: context = {}
        res = super(hr_secret_report, self).default_get(cr, uid, fields, context=context)
        personal_character_dict = self._personal_character_fnct(cr, uid, context)
        inspector_performance_character_dict = self._inspector_performance_character_fnct(cr, uid, context)
        job_recommandation_dict = self._job_recommandation_fnct(cr, uid, context)
        recommandation_dict = self._general_recommandation_fnct(cr, uid, context)
        res.update(personal_character=personal_character_dict)
        res.update(inspector_performance_character=inspector_performance_character_dict)
        res.update(job_recommandation=job_recommandation_dict)
        res.update(general_recommandation=recommandation_dict)
        return res

    def confirm(self,  cr, uid, ids, context=None):
        """
        Method that write state confirmed
        """
        return self.write(cr, uid, ids, {'state': 'confirmed'})

    def draft(self,  cr, uid, ids, context=None):
        """
        Method that write state draft
        """
        return self.write(cr, uid, ids, {'state': 'draft'})

    def onchange_employee_id(self, cr, uid, ids, employee_id, context={}):
        """
        change fields related to employee
        """
        vals = {'degree_id': False, 'department_id': False,
                'job_id': False, 'marital': False,
                'employment_date': False, 'birthday': False,}
        if employee_id:
            emp = self.pool.get('hr.employee').browse(cr, uid, employee_id, context)
            vals = {'degree_id': emp.degree_id.id, 'department_id': emp.department_id.id,
                'job_id': emp.job_id.id, 'marital': emp.marital,
                'employment_date': emp.employment_date, 'birthday': emp.birthday,}

        return {'value':vals}

    def create(self, cr, uid, vals, context={}):
        """
        overwrite create to reflect employee related fields
        """
        on_change_vals = self.onchange_employee_id(cr, uid, [], vals['employee_id'], context)
        vals['degree_id'] = on_change_vals['value']['degree_id']
        vals['department_id'] = on_change_vals['value']['department_id']
        vals['job_id'] = on_change_vals['value']['job_id']
        vals['employment_date'] = on_change_vals['value']['employment_date']
        vals['birthday'] = on_change_vals['value']['birthday']
        vals['marital'] = on_change_vals['value']['marital']

        return super(hr_secret_report, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context={}):
        """
        overwite write method to update related employee fields
        """
        for rec in self.browse(cr, uid, ids, context):
            employee_id = 'employee_id' in vals and vals['employee_id'] or rec.employee_id.id
            on_change_vals = self.onchange_employee_id(cr, uid, [], employee_id, context)
            vals['degree_id'] = on_change_vals['value']['degree_id']
            vals['department_id'] = on_change_vals['value']['department_id']
            vals['job_id'] = on_change_vals['value']['job_id']
            vals['employment_date'] = on_change_vals['value']['employment_date']
            vals['birthday'] = on_change_vals['value']['birthday']
            vals['marital'] = on_change_vals['value']['marital']

            super(hr_secret_report,self).write(cr, uid, ids, vals, context)

        return True


    def unlink(self, cr, uid, ids, context={}):
        """
        Method that prevent delete record not in draft state
        @return : Super unlink function 
        """
        for rec in self.browse(cr, uid, ids, context):
            if rec.state != 'draft':
                raise osv.except_osv(_('Error'), _("You can not delete record not in the draft state!"))

        return super(hr_secret_report, self).unlink(cr, uid, ids, context)

    def name_get(self, cr, uid, ids, context=None):
        """override to compute name from other fields"""
        if not len(ids):
            return []
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.employee_id.name + '-' + str(record.year) 
            res.append((record.id,name))
        return res


# ----------------------------------------------------
# Personal Characteristic
# ----------------------------------------------------
class hr_secret_report_personal_character(osv.Model):
    _name = "hr.secret.report.personal.character"
    CHARACTER_SELECTION = [
        ('0','0'),
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
        ('5','5'),
        ]


    ANSWER = [
        ('yes','Yes'),
        ('no','No'),
    ]

    PART = [
        ('1','Personal Characteristic'),
        ('2','Inspector Performance'),
        ('3','Recommendations for Jobs and Promotion'),
        ('4','General Recommendations'),
    ]

    _description = "Hr Secret Report Personal Characteristic"

    _columns = {
        'secret_report_id': fields.many2one('hr.secret.report.process', string='Secret Report', ondelete='cascade'),
        'name': fields.many2one('hr.secret.report.character','Characteristic', required=True),
        'direct': fields.selection(CHARACTER_SELECTION, 'Direct Leader'),
        'supreme': fields.selection(CHARACTER_SELECTION, 'Supreme Commander'),
        'direct_answer': fields.selection(ANSWER, 'Direct Leader'),
        'supreme_answer': fields.selection(ANSWER, 'Supreme Commander'),
        'supreme_general_recommandation': fields.text('Supreme Commander Recommandation'),
        'direct_general_recommandation': fields.text('Direct Leader Recommandation'),
        'part': fields.selection(PART, 'Part'),
    }
    _defaults = {
        'name':False,
        'direct': False,
        'supreme': False,
        'direct_answer': False,
        'supreme_answer': False,
    }



# ----------------------------------------------------
# Report Characteristic
# ----------------------------------------------------
class hr_secret_report_personal_character(osv.Model):
   
    _name = "hr.secret.report.character"
    
    
    PART = [
        ('1','Personal Characteristic'),
        ('2','Inspector Performance'),
        ('3','Recommendations for Jobs and Promotion'),
        ('4','General Recommendations'),
    ]

    _description = "Hr Secret Report Characteristic"

    _columns = {
        'name': fields.char('Characteristic Name'),
        'part': fields.selection(PART, 'Part'),
        'sequence': fields.integer('Sequence'),
        'load': fields.boolean('Load By Default'),
        'company_id': fields.many2one('res.company','company'),
    }

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults = {
        'name':False,
        'load': False,
        'company_id' : _default_company,
    }


    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        """
        Overwite name_search to not select already existed record per lines
        @return: super 
        """
        lines = []
        emp_cost=[]
        vehicle_ids = []
        ids = []
        if context is None:
            context = {}
        if 'model' in context :

            line_ids = resolve_o2m_operations(cr, uid, self.pool.get(context['model']),
                                                context.get('line_ids'), ["name"], context)            
            args.append(('id', 'not in', [isinstance(
                d['name'], tuple) and d['name'][0] or d['name'] for d in line_ids]))

        return super(hr_secret_report_personal_character, self).name_search(cr, uid, name, args=args, operator=operator, context=context, limit=limit)


    def check_unique(self, cr, uid, ids, context=None):
        """ 
        Constrain method to check if there is a record with the same name and part

        @return: boolean True or False
        """
        
        for rec in self.browse(cr, uid, ids, context=context):
            domain = [('name', '=', rec.name),('part', '=', rec.part),('id','!=',rec.id)]
            
            idss = self.search(cr,uid, domain)
            if idss:
                raise osv.except_osv(_('ERROR'), _('Characteristic Name should be unique per part '))
        return True

    _constraints = [
         (check_unique, '', []),
    ]