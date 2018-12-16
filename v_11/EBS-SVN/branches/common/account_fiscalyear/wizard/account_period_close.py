# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api ,osv, fields,exceptions, models,_
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp
from odoo.tools import  DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.config import config
import operator

class account_period_close(models.TransientModel):
    """
        close period
    """
    _name = "account.period.close"
    _description = "period close"
    
    sure = fields.Boolean('Check this box')
    
    @api.multi
    def data_save(self):
        """
        This function close period
         """
        period_pool = self.env['account.period']
        account_move_obj = self.env['account.move']

        mode = 'done'
        for form in self.read():
            if form['sure']:
                for id in self._context['active_ids']:
                    account_move_ids = account_move_obj.search([('period_id', '=', id), ('state', '=', "draft")])
                    if account_move_ids:
                        raise ValidationError(_('In order to close a period, you must first post related journal entries.'))

                    #self.env.cr.execute('update account_journal_period set state=%s where period_id=%s', (mode, id))
                    #self.env.cr.execute('update account_period set state=%s where id=%s', (mode, id))
                    period=period_pool.search([('id', '=', id)])
                    period.write({'state': 'done'})

        return {'type': 'ir.actions.act_window_close'}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
