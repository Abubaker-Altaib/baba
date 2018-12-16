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

#-----------------------------------------
#   HR Employee Seniority Report Wizard
#-----------------------------------------

class seniority_report_wizard(osv.osv_memory):
    _name = "seniority.report.wizard"

    _columns = {
        'degrees': fields.many2many('hr.salary.degree', 'seniority_wizard_degree_rel', string="degrees"),
        'departments': fields.many2many('hr.department', 'seniority_wizard_department_rel', string="Departments"),
        'type': fields.selection([('degree', 'By Degree'), ('department', 'By Department')], string="Type")
    }

    def print_report(self, cr, uid, ids, context={}):

        data = {'form': self.read(cr, uid, ids, [])[0]}
        
        return {'type': 'ir.actions.report.xml', 'report_name': 'seniority.report', 'datas': data}
