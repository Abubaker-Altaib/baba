# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#

############################################################################
from openerp.osv import fields, osv, orm


class hr_employee(osv.Model):

    _inherit = "hr.employee"
    _name = "hr.employee"

    def write(self, cr, uid, ids, vals, context=None):
        """
        to reflect change of employee in stored related fields in admin affairs
        """
        returned = super(hr_employee, self).write(cr, uid, ids, vals, context)
        if type(ids) is not list:
            ids = [ids]

        temp_ids = []
        for i in ids:
            i = int(i)
            temp_ids.append(i)
        ids = temp_ids

        ids = ids + ids
        ids = tuple( ids )
        
        
        cr.execute("""update fleet_vehicle f_v set department_id=emp.department_id , degree_id=emp.degree_id , company_id=users.company_id
                    from hr_employee emp
                    left join resource_resource res_res on (emp.resource_id=res_res.id)
                    left join res_users users on (res_res.user_id=users.id) 
                    where (f_v.employee_id=emp.id) and emp.id in %s""" %(ids,))
        return returned