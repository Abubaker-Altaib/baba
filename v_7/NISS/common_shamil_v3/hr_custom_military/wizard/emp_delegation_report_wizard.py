# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv, fields

#-----------------------------------------
#   department duration report wizard
#-----------------------------------------

class emp_delegation_report_wizard(osv.osv_memory):
    _name = "emp.delegation.report.wizard"

    _columns = {
        'state_id': fields.many2one('hr.service.state', string="Service State"),
        'state_id_level2': fields.many2one("hr.service.state", string="State level2"),
        'state_id_level3': fields.many2one("hr.service.state", string="State level3"),
        'date_from': fields.date(string="Date From"),
        'date_to': fields.date(string="Date To"),
        'department_id': fields.many2one('hr.department', string="Department"),
        }

    def print_report(self, cr, uid, ids, context={}):

        data = {'form': self.read(cr, uid, ids, [])[0]}
        
        return {'type': 'ir.actions.report.xml', 'report_name': 'emp_delegation_reports', 'datas': data}
