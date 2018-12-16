# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from datetime import datetime
import time
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import netsvc

class hr_salary_scale(osv.Model):
    _inherit = "hr.salary.scale"
    _columns = {
        'military_type' : fields.selection([ ('officer' , 'Officers'),('soldier' , 'Soldiers')], string='Military Type'),
    }


class hr_employee(osv.Model):
    _inherit = "hr.employee"
    _columns = {
        'military_type' : fields.selection([ ('officer' , 'Officers'),('soldier' , 'Soldiers')], string='Military Type'),
    }   

    def write(self, cr, uid, ids, vals, context=None):
        new_v = super(hr_employee, self).write(cr, uid, ids, vals, context=context)
        if 'degree_id' in vals:
            for rec in self.browse(cr, uid, ids, context):
                if rec.user_id:
                    if rec.user_id.partner_id:
                        rec.user_id.partner_id.write({'degree_id':rec.degree_id.id}) 
        
        if 'state' in vals:
            if vals['state'] == 'refuse':
                for rec in self.browse(cr, uid, ids, context):
                    if rec.user_id:
                        cr.execute("""delete from res_groups_users_rel where uid = %s""" %(rec.user_id.id,))
        return new_v
