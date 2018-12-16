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
from account_ntc.report.owner_equity import owner_equity_report

class owner_equity_wizard(osv.osv):
    _name = "owner.equity.line"

    _description = "Owner Equity Line"

    _columns = {
        'opening':fields.boolean('Opening'),
        'opening_journal':fields.char('Opening Journal'),
        'name':fields.char('name'),
        'value1':fields.char('رأس المال'),
        'value2':fields.char('الاحتاطيات'),
        'value3':fields.char('الفائض المرحل'),
        'value4':fields.char('المجموع'),

    }

class owner_equity_wizard(osv.osv):
    _name = "owner.equity"

    _description = "Owner Equity"

    _columns = {
        'year0':fields.many2one('account.fiscalyear','Previous Fiscal Year', select=True),
        'year':fields.many2one('account.fiscalyear','Fiscal Year', select=True),
        'line_ids':fields.many2many('owner.equity.line',string='Lines'),
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'owner.equity',
             'form': data
            }
        owner = owner_equity_report( cr, uid, '', context)
        try:
            owner.lines(datas)
        except:
            raise osv.except_osv(_('Error'), _("Wrong data Entered"))

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'owner_equity.report',
            'datas': datas,
            }