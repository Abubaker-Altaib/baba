# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
import time
from tools.translate import _


class residence_wizard_report(osv.osv_memory):
    _name = "residence_wizard.report"

    _columns = {
        'degree_ids': fields.many2many('hr.salary.degree', 'residence_wizard_degree_rel', string="degrees"),
        'state_ids': fields.many2many('hr.employee.location.state', 'residence_wizard_state_rel', string="states",domain=[('type','=','state')]),
        'local_ids': fields.many2many('hr.employee.location.state', 'residence_wizard_local_rel', string="locals",domain=[('type','=','local')]),
        'type': fields.selection([('state', 'State'), ('state_local', 'State Local')], string="Type")
    }

    def print_report(self, cr, uid, ids, context={}):

        data = {'form': self.read(cr, uid, ids, [])[0]}
        return {'type': 'ir.actions.report.xml', 'report_name': 'residence_state_report', 'datas': data}


