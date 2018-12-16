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
#   department duration report wizard
#-----------------------------------------

class dept_duration_report_wizard(osv.osv_memory):
    _name = "dept.duration.report.wizard"

    _columns = {
        'type': fields.selection([('department_duration','Department Duration'),('age','Age until today')] ,'Type',required=True ),                                       
        'department_id': fields.many2one('hr.department', string="Departments"),
        'degree_id': fields.many2one('hr.salary.degree', string="Degrees"),
        'more_than': fields.integer(string="more than",size=2),
		'less_than': fields.integer(string="less than",size=2),
		'age_from': fields.integer(string="Age From",size=3),
		'age_to': fields.integer(string="Age To",size=3),
    }

    _defaults = {
        'age_from':  18,
        'age_to':  60,
    }

    def print_report(self, cr, uid, ids, context={}):

        data = {'form': self.read(cr, uid, ids, [])[0]}
        
        return {'type': 'ir.actions.report.xml', 'report_name': 'dept_duration_reports', 'datas': data}
