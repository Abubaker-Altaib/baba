# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from osv import osv
from tools.translate import _


class reflect_department_change(osv.osv_memory):

    _name = "reflect_department_change"

    def reflect(self, cr, uid, ids, context=None):
        cr.execute("""update fleet_vehicle f_v set department_id=emp.department_id 
                    from hr_employee emp where (f_v.employee_id=emp.id) """)
        pass
