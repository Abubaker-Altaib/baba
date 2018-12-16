# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from datetime import date,datetime
from openerp.osv import osv, fields
from openerp.tools.translate import _
 



class unit_report(osv.osv):
    _name = "unit.report"

    _description = "Unit Report"

    _columns = {
        'name':fields.many2one('unit.report.type','name', select=True),
        'company_id':fields.many2one('res.company','company', select=True),
        'line_ids':fields.many2many('unit.report.line',string='Lines'),
        'common':fields.boolean('common'),
    }

class unit_report_line(osv.osv):
    _name = "unit.report.line"

    _description = "Accounts"

    _columns = {
        'with_value':fields.boolean('with_value'),
        'account_id':fields.many2one('account.account','account'),
        'code':fields.char('code'),
        'name':fields.char('name'),
        'closure':fields.integer('closure'),
         

    }


class unit_report_type(osv.osv):
    _name = "unit.report.type"

    _description = "types"

    _columns = {
 
 
        'name':fields.char('name'),
        'code':fields.char('code'),
 
         

    }
