# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from report import report_sxw

class report_asset_detail(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(report_asset_detail, self).__init__(cr, uid, name, context=context)
        self.period_ids = []
        self.journal_ids = []
        self.sort_selection = 'date'
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'sum_depr': self._sum_depr,
            'display_currency':self._display_currency,
    })

    '''def set_context(self, objects, data, ids, report_type=None):
        obj_move = self.pool.get('account.move.line')
        new_ids = ids
        self.query_get_clause = ''
        #if (data['model'] == 'ir.ui.menu'):

        new_ids = [data['form']['asset_id']]
        objects = self.pool.get('account.asset.asset').browse(self.cr, self.uid, new_ids)

        return super(report_asset_detail, self).set_context(objects, data, ids, report_type=report_type)'''

    def _sum_depr(self, id):
        res = {}
        obj_mline = self.pool.get('account.asset.history')
        asset = self.pool.get('account.asset.asset').browse(self.cr, self.uid, id)
        self.cr.execute("SELECT sum(amount) FROM account_asset_depreciation_line where asset_id=%s and move_check=True", (id,  ))
        res['depr'] = self.cr.fetchone()[0] or 0.0
        print res['depr'],"res['depr']"
        self.cr.execute("SELECT sum(amount) FROM account_asset_history where asset_id=%s and type='initial'", (id,  ))
        res['initial'] = self.cr.fetchone()[0] or 0.0
        print res['initial'],"res['initial']"
        self.cr.execute("SELECT sum(amount) FROM account_asset_history where asset_id=%s and type='reval'", (id,  ))
        res['reval'] = self.cr.fetchone()[0] or 0.0
        print res['reval'],"res['reval']"
        self.cr.execute("SELECT sum(amount) FROM account_asset_history where asset_id=%s and type in ('abandon','sale')", (id,  ))
        res['close'] = self.cr.fetchone()[0] or 0.0
        print res['close'],"res['close']"
        return [res]


    def lines(self, id):
        obj_mline = self.pool.get('account.asset.history')
        self.cr.execute('SELECT id FROM account_asset_history where asset_id=%s', (id,  ))
        ids = [r[0] for r in self.cr.fetchall()]
        return obj_mline.browse(self.cr, self.uid, ids)




    def _get_account(self, data):
        if data['model'] == 'account.journal.period':
            return self.pool.get('account.journal.period').browse(self.cr, self.uid, data['id']).company_id.name
        return super(report_asset_detail, self)._get_account(data)

    def _display_currency(self, data):
        if data['model'] == 'account.journal.period':
            return True
        return data['form']['amount_currency']


report_sxw.report_sxw('report.asset.detaill', 'account.asset.asset',
    'addons/account_asset_custom/report/asset_detail.rml',parser=report_asset_detail, header='internal')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
