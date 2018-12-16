# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _
import netsvc

#----------------------------------------
# Training Categories
#----------------------------------------
class hr_training_category(osv.Model):

    _name = "hr.training.category"

    _description = "Training Category"

    _columns = {
        'name' : fields.char("Category Name", size=50, required=True),
        'active' : fields.boolean('Active'),
        'code': fields.char('Code', size=64),
    }

    _defaults = {
        'active':1,
    }

    _sql_constraints = [('name_uniqe', 'unique (code)', _('You can not create same code !'))]

    def _name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=100, name_get_uid=None):
        """
        Method that searchs for records whether the enterd value is name or code of the category.

        @param name: String represents category name or code
        @param operator: Operator for search criterion
        @param limit: Max number of records to return
        @param name_get_uid: Id of the user
        @return:  List of tuple
        """
        if args is None:
            args = []
        ids = self.search(cr, uid, args + ['|', ('name', operator, name), ('code', operator, name)], limit=limit, context=context)
        return self.name_get(cr, name_get_uid or uid, ids, context=context)

    def name_get(self, cr, uid, ids, context=None):
        """
        Method that overwrite get_name to reads the name and the code of the category  
        and concatenates them together as the  name if no code then its just return
        the name as name.

        @return:  List of tuple that contains record's id and name
        """
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name', 'code'], context=context)
        return [(record['id'], record['code'] and record['code'] + '-' + record['name'] or record['name']) for record in reads]

    def unlink(self, cr, uid, ids, context=None):
        course_obj = self.pool.get('hr.training.course')
        course_id = course_obj.search(cr, uid, [('training_category_id', 'in', ids)], context=context)
        if course_id:
            raise osv.except_osv(_('Warning!'), _('You cannot delete this Category because some courses is assign to this Category'))
        return super(hr_training_category, self).unlink(cr, uid, ids, context)

#----------------------------------------
# Training Courses
#----------------------------------------
class hr_training_course(osv.Model):

    _name = "hr.training.course"

    def _check_recursion(self, cr, uid, ids, context=None):
        """Check recursion to avoid choosing course in previouse course for the course it self.
           @param ids: List of course ids
           @return: True or False
        """
        for c in self.browse(cr, uid, ids):
            if c in tuple(c.prev_course_ids):
                return False
        return True

    def _editable(self, cr, uid, ids, context=None):
        #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> "
        training_obj = self.pool.get('hr.employee.training')
        training_id = training_obj.search(cr, uid, [('course_id', 'in', ids)], context=context)
        for s in training_obj.browse(cr, uid, training_id):
            if s.state == 'done':
                raise osv.except_osv(_('Error!'), _('You can not edit the Name of course in Done State.'))
                return False
        return True

    _description = "Training Course"

    _columns = {
        'name': fields.char("Course Name", size=64, required=True),
        'code': fields.char("Course Code", size=64),
        'training_category_id': fields.many2one('hr.training.category', 'Course Category'),
        'objective': fields.text('Course Objective', size=64),
        'content': fields.text('Course Content', size=64),
        'job_ids': fields.many2many('hr.job', 'hr_course_job_rel', 'course_id', 'job_id', 'Dedicated Jobs'),
        'qualification_ids': fields.many2many('hr.qualification', 'hr_course_qualification_rel', 'course_id', 'qualification_id', 'Qualifications'),
        'prev_course_ids': fields.many2many('hr.training.course', 'hr_prev_course_rel', 'course_id', 'prev_id', 'Previous Courses Required'),
        'specification_ids': fields.many2many('hr.specifications', 'hr_course_specification_rel', 'course_id', 'general_id', ' Experience Specifications'),
        'employee_category_ids': fields.many2many('hr.employee.category', 'hr_course_employee_category_rel', 'course_id', 'category_id', 'Employee Categories'),
        'check_both': fields.boolean('Both Experiences Required'),
        'general_experience_year': fields.integer('General Experience Years'),
        'specific_experience_year': fields.integer('Specific Experience Years'),    
    }

    _defaults = {
        'check_both': True,
    }

    _sql_constraints = [
        ('name_unique', 'unique(name)', _('The name of the training should be unique!')),
        ('general_experience_check', 'check (general_experience_year>=0)', 'The General Experience of Year should be integer or Zero !'),
        ('course_code_unique', 'unique(code)', 'The code of the training should be unique!')
    ]

    _constraints = [
        (_check_recursion, 'Error ! You cannot create recursive courses.', ['name']),
        (_editable, 'Error ! You can not edit the Name of course in Done State.', ['name']),
    ]
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        for course in self.browse(cr, uid, ids, context=context):
            if 'name' in vals and course.name != vals['name']:
                courses = self.pool.get('hr.employee.training').search(cr, uid, [('course_id', 'in', ids),('state', '=', 'done')])
                if courses:
                    raise osv.except_osv(_('Warning!'), _('This course has approved course, therefore you cannot modify its name field.'))
        return super(hr_training_course, self).write(cr, uid, ids, vals, context=context)
        
    def unlink(self, cr, uid, ids, context=None):
        training_obj = self.pool.get('hr.employee.training')
        training_id = training_obj.search(cr, uid, [('course_id', 'in', ids)], context=context)
        if training_id:
            raise osv.except_osv(_('Warning!'), _('You cannot delete this Course because it is assign to approved or suggested courses and executed'))
        return super(hr_training_course, self).unlink(cr, uid, ids, context)

#----------------------------------------
# Training Enrich

#----------------------------------------
class hr_training_enrich(osv.Model):

    _name = "hr.training.enrich"

    _description = "Training Enrich"

    _columns = {
        'name': fields.char('Enrich', size=64, required=True),
        'code': fields.char("Code", size=64, required=True),
        'enrich_type':fields.selection([('1', 'Amount'),('2', 'Factor'),('3', 'Protocols')], 'Enrich Type', required=True),
        'fixed_value' :fields.integer("Fixed value"),
        'allowance_id' :fields.many2one('hr.allowance.deduction', 'Allowance', required=False, domain=[('name_type', '=', 'allow')]),
        'currency': fields.many2one('res.currency', 'Enrich Currency' , required=True),
        'emp_states' :fields.one2many('emp.states', 'name', 'Employee States'),
        'comments': fields.text('Course Content', size=32),
    }

    def _check_not_zero(self, cr, uid, ids, context=None):
        """
        Method that checks if the fix value is greater than zero or not, if not 
        it raises and exception.

        @return: Boolean True
        """
        enrich = self.browse(cr, uid, ids, context=context)
        if ((enrich[0]['enrich_type'] == '3') and (enrich[0]['fixed_value'] <= 0)):
                raise osv.except_osv(_('Warning!'), _('The value  must be more than zero !!%s'))
        return True

    _constraints = [
        (_check_not_zero, 'The value  must be more than zero !', ['fixed_value']),
    ]

    _sql_constraints = [
       ('name_uniqe', 'unique (name)', 'You can not entered the same name of Enrich!'),
    ]

    def onchange_enrich_type(self, cr, uid, ids , enrich_type, context=None):
        return {'value': {'fixed_value': 0.0, 'allowance_id': False , 'emp_states':False}}

    def copy(self, cr, uid, id, default=None, context=None):
        default = {} if default is None else default.copy()
        plan = self.browse(cr, uid, id, context=context)
        default.update({'name':plan.name + "(copy)"})
        return super(hr_training_enrich, self).copy(cr, uid, id, default, context=context)

    def unlink(self, cr, uid, ids, context=None):
        training_obj = self.pool.get('hr.employee.training')
        training_id = training_obj.search(cr, uid, [('enrich_id', 'in', ids)], context=context)
        if training_id:
            raise osv.except_osv(_('Warning!'), _('You cannot delete this Enrich because it is assign to approved or suggested courses'))
        return super(hr_training_enrich, self).unlink(cr, uid, ids, context)

#----------------------------------------
# Employee States
#----------------------------------------
class emp_states(osv.Model):

    def _check_not_zero(self, cr, uid, ids, context=None):
        enrich_obj = self.pool.get('hr.training.enrich')
        enrich_id = enrich_obj.search(cr, uid, [('emp_states', 'in', ids)], context=context)
        for enrich in enrich_obj.browse(cr, uid, enrich_id, context = context):
            states = self.browse(cr, uid, ids, context=context)
            for rec in states:
                #print">>>>>>>>>>>>>>>rec    states    " ,rec ,states
                #print">>>>>>>>>>>>>>>    enrich_id    " ,enrich_id
                if ((enrich.enrich_type == '1') and (rec.amount <= 0)):
                    raise osv.except_osv(_('Warning!'), _('The value  must be more than zero !!%s'))
        return True

    _name = "emp.states"

    _description = "Company's Training Enrich Amount"

    _columns = {
        'name':fields.many2one('hr.training.enrich', 'Name' , required=True , ondelete='cascade'),
        'company_id' : fields.many2one('res.company', 'Company' , required=True),
        'amount' :fields.integer("Enrichment Amount" , required=True),
    }
    _sql_constraints = [
       ('company_uniqe', 'unique (name,company_id)', 'You can not selected the same company twice !'),
                        ]
    _constraints = [
        (_check_not_zero, 'The value  must be more than zero !', ['amount']),
    ]

#----------------------------------------
# Training Plan
#----------------------------------------
class hr_training_plan(osv.Model):

    _name = "hr.training.plan"

    _description = "Training Plan"

    _columns = {
        'name': fields.char('Plan Name', size=64, required=True),
        'code': fields.char("Plan Code ", size=64, required=True),
        'percentage': fields.integer("Percentage", help="The percentage of employees allow to nominate from each department.\nIf it equal 0 it means unlimited."),
        'classification': fields.selection((('special', 'Special Plan'), ('yearly', 'Yearly Plan'), ('emergency', 'Emergency Plan')), 'Plan Classification'),
        'start_date': fields.date('Plan Start Date'),
        'end_date': fields.date('Plan End Date'),
        'active': fields.boolean('Active', select=True),
        'suggested_course_ids' :fields.one2many('hr.employee.training.suggested', 'plan_id', 'Suggested Courses',
                                                domain=[('type', '=', 'hr.suggested.course'), ('state', 'in', ('validated', 'approved'))], readonly=True),
    }

    _defaults = {
        'active':1,
       }

    _sql_constraints = [
       ('name_uniqe', 'unique (name)', 'You can not entered the same name of Plan!'),
       ('percentage_check', 'check (percentage>=0)', 'The number of percentage should be integer or Zero !'),
    ]

    def copy(self, cr, uid, id, default=None, context=None):
        default = {} if default is None else default.copy()
        plan = self.browse(cr, uid, id, context=context)
        default.update({'name':plan.name + "(copy)", 'suggested_course_ids': False })
        return super(hr_training_plan, self).copy(cr, uid, id, default, context=context)


class res_partner(osv.Model):

    _inherit = 'res.partner'

    _columns = {
                'trainer': fields.boolean('Training Center'),
    }

    def onchange_trainer(self, cr, uid, ids, trainer, context=None):
        if trainer:
            return {'value':{'supplier':trainer}}
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
