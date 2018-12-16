# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv, fields
from openerp.tools.translate import _
from lxml import etree
from openerp.osv.orm import setup_modifiers
import openerp.addons.decimal_precision as dp
import time
import datetime
from lxml import etree

#--------------------------
#   HR Employee Seniority
#--------------------------
class  hr_employee_seniority(osv.osv):
    """ To manage HR Employee Seniority """
    _name = "hr.employee.seniority"
    _order = "degree_seq DESC,sequance"
    _columns = {
    	'sequance': fields.integer(string="Sequance"),
        'employee_id': fields.many2one('hr.employee', "Employee"),
        'degree_id': fields.many2one("hr.salary.degree",string="Degree",readonly=1),
        'degree_seq': fields.integer(string="Degree Sequance"),
        'emp_no': fields.related('employee_id','otherid',type="char",string="Employee No",readonly=1),
        'degree_date': fields.related('employee_id','promotion_date',type="date",string="Promotion Date"),
        'department_id':fields.many2one('hr.department',string='Department',readonly=True),
        'company_id': fields.related('employee_id','company_id',type="many2one",relation='res.company',string="company",readonly=1),
        'employment_date': fields.related('employee_id','employment_date',type="date",string="Employment Date", readonly=1),
    }

    _sql_constraints = [
        ('employee_id_uniqe', 'unique(employee_id)', 'The Employee must be unique !')
    ]

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        #override of fields_view_get to change the String of employee_id fields
        emp_obj=self.pool.get('hr.employee')
        belong_to=False
        if context is None:
            context={}
        res = super(hr_employee_seniority, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        emp=emp_obj.search(cr, uid, [('user_id','=',uid)])
        employee = emp_obj.browse(cr, uid, emp and emp[0] or 0)
        for cat in (emp and employee.category_ids or []):
            if cat.belong_to:
                belong_to=cat.belong_to
        if belong_to:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='employee_id']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier'))
                else:
                    node.set('string', _('Soldier'))
            for node in doc.xpath("//label[@for='employee_id']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier'))
                else:
                    node.set('string', _('Soldier'))
            for node in doc.xpath("//field[@name='emp_no']"):
                if belong_to == 'officer_affairs':
                    node.set('string', _('Officer Number'))
                elif belong_to == 'soldier_affairs':
                    node.set('string', _('Soldier Number'))
                else:
                    node.set('string', _('Soldier Number'))
            res['arch'] = etree.tostring(doc)
        return res

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            raise osv.except_osv(_('Warning!'),_('The Delete is Forbidden.'))
        return super(hr_employee_seniority, self).unlink(cr, uid, ids, context)

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.degree_id.name + '-' + str(record.sequance)
            res.append((record.id, name))
        return res

    def create(self, cr, uid, vals, context=None):
        """
        Override create method
        @return: super create method
        """        
        return super(hr_employee_seniority, self).create(cr, uid, vals, context=context)


class seniority_update(osv.osv_memory):
    _name = "seniority.update"


    def check_create(self, cr, uid, ids,emp_dict, context=None):
        """
        To check create of Employee Seniority.

        @param emp_dict:Employee IDs 
        @return:List of IDs 
        """
        create_ids=[]


        cr.execute("""SELECT s.employee_id as employee_id
            From hr_employee_seniority s
            where employee_id in %s""",(tuple(emp_dict), ))
        res = cr.dictfetchall()

        result = map (lambda x:x['employee_id'],res)

        create_ids=list(set(emp_dict) - set(result))


        return create_ids

    def check_update(self, cr, uid, ids,emp_dict, context=None):
        """
        To check update of Employee Seniority.

        @param emp_dict:Employee IDs 
        @return:List of IDs 
        """
        seniority=self.pool.get('hr.employee.seniority')
        update_ids=[]
        for res in emp_dict:

            #idss = seniority.search(cr , uid , [('employee_id' , '=' , res['employee_id'])])
            #obj_idss = seniority.browse(cr, uid, idss)
            idss=[]
            idss.append(res['employee_id'])

            cr.execute( """SELECT sequance,id 
            From hr_employee_seniority 
            where employee_id in %s""",(tuple(idss), ))
            sql_res = cr.dictfetchall()

            if sql_res:
                if res['seq'] != sql_res[0]['sequance']:
                    update_ids.append({'employee_id':res['employee_id'],'seq':sql_res[0]['id'],'new_seq':res['seq']})

        return update_ids


    def seniority_update(self, cr, uid, ids, context=None):
        """
        To update or create Employee Seniority.

        @param: 
        @return:Boolean True 
        """

        cr.execute( """DELETE From hr_employee_seniority where employee_id in 
            (select s.employee_id from hr_employee_seniority s left join hr_employee h on(h.id = s.employee_id) 
                        where h.state != 'approved' )
                    """)


        cr.execute( """SELECT row_number() over(partition by h.degree_id ORDER BY d.sequence DESC,h.promotion_date,LPAD(h.otherid,20,'0')) as seq,h.id as employee_id
            From hr_employee h left join hr_salary_degree d on(h.degree_id = d.id) 
            where h.state = 'approved'
            ORDER BY d.sequence DESC,h.promotion_date,LPAD(h.otherid,20,'0')""")
        res = cr.dictfetchall()

        result = map (lambda x:x['employee_id'],res)

        create_ids=[]
        create_ids= self.check_create(cr, uid, ids,result,context=context)

        if create_ids:
            cr.execute( """INSERT into hr_employee_seniority (sequance,employee_id,degree_seq,department_id,degree_id)
                select row_number() over(partition by h.degree_id) as seq,h.id as employee_id,d.sequence,h.department_id,h.degree_id 
                From hr_employee h left join hr_salary_degree d on(h.degree_id = d.id) 
                where h.state = 'approved' and h.id in %s
                ORDER BY d.sequence DESC,h.promotion_date,LPAD(h.otherid,20,'0')""" ,(tuple(create_ids), )) 

        update_ids=[]
        update_ids= self.check_update(cr, uid, ids,res,context=context)
        employee_id = map (lambda x:x['employee_id'],update_ids)
        seq = map (lambda x:x['seq'],update_ids)

        if update_ids:
            for update in update_ids:
                cr.execute( """UPDATE hr_employee_seniority s set sequance = %s,degree_seq=q.sequence,department_id=q.department_id,degree_id=q.degree_id 
                    from(select h.id as employee_id,d.sequence as sequence ,h.department_id as department_id,h.degree_id as degree_id 
                    From hr_employee h left join hr_salary_degree d on(h.degree_id = d.id) 
                    where h.state = 'approved' and h.id = %s) q where s.employee_id = q.employee_id and s.id = %s""",(update['new_seq'],update['employee_id'],update['seq']) )

        
        cr.execute( """update hr_employee base_emp 
        set otherid_seniority=sub.sequance 
        from (select emp.id, sen.sequance from hr_employee emp 
        left join hr_employee_seniority sen on (sen.employee_id=emp.id)) as sub 
        where sub.id=base_emp.id""")

        return True

