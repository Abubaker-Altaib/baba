# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import itertools
import logging
import psycopg2
import operator
import base64
from odoo.tools.mimetypes import guess_mimetype
import psycopg2
from odoo import api, models
from odoo import api ,osv, fields,exceptions,_
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
from datetime import datetime, timedelta
try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None



class AccountBankStatementImport(models.TransientModel):
    _inherit = "account.bank.statement.import"

    journal_id = fields.Many2one('account.journal', string='Journal', required=True,domain=[('type', '=', 'bank')])

    def _check_xls(self, filename):
        return filename and filename.lower().strip().endswith('.xls')

    @api.multi
    def import_file(self):
        if not self._check_xls(self.filename):
            return super(AccountBankStatementImport, self).import_file()
        ctx = dict(self.env.context)
        import_wizard = self.env['base_import.import'].with_context({'bank_statement_import_id':self.ids}).create({
            'res_model': 'account.bank.statement.line',
            'file': base64.b64decode(self.data_file),
            'file_name': self.filename,
            'file_type': 'application/vnd.ms-excel',
            'journal_id':self.journal_id.id,

        })
        ctx['wizard_id'] = import_wizard.id
        ctx['bank_statement_import_id'] = self.ids
        return {
            'type': 'ir.actions.client',
            'tag': 'import_bank_stmt',
            'params': {
                'model': 'account.bank.statement.line',
                'context': ctx,
                'filename': self.filename,
            }
        }


class AccountBankStmtImportXls(models.TransientModel):

    _inherit = 'base_import.import'

    journal_id = fields.Many2one('account.journal', string='Journal')


    @api.model
    def get_fields(self, model, depth=2):
        fields_list = super(AccountBankStmtImportXls, self).get_fields(model, depth=depth)
        if self._context.get('bank_stmt_import', False):
            add_fields = [{
                'id': 'balance',
                'name': 'balance',
                'string': _('Cumulative Balance'),
                'required': False,
                'fields': [],
                'type': 'monetary',
            }, {
                'id': 'debit',
                'name': 'debit',
                'string': _('Debit'),
                'required': False,
                'fields': [],
                'type': 'monetary',
            }, {
                'id': 'credit',
                'name': 'credit',
                'string': _('Credit'),
                'required': False,
                'fields': [],
                'type': 'monetary',
            }]
            fields_list.extend(add_fields)
        return fields_list

    def _convert_to_float(self, value):
        return float(value) if value else 0.0

    @api.multi
    def _parse_import_data(self, data, import_fields, options):
        data = super(AccountBankStmtImportXls, self)._parse_import_data(data, import_fields, options)
        statement_id = self._context.get('bank_statement_id', False)
        if not statement_id:
            return data
        ret_data = []

        vals = {}
        import_fields.append('statement_id/.id')
        import_fields.append('sequence')
        index_balance = False
        convert_to_amount = False
        if 'debit' in import_fields and 'credit' in import_fields:
            index_debit = import_fields.index('debit')
            index_credit = import_fields.index('credit')
            self._parse_float_from_data(data, index_debit, 'debit', options)
            self._parse_float_from_data(data, index_credit, 'credit', options)
            import_fields.append('amount')
            convert_to_amount = True
        # add starting balance and ending balance to context
        if 'balance' in import_fields:
            index_balance = import_fields.index('balance')
            self._parse_float_from_data(data, index_balance, 'balance', options)
            vals['balance_start'] = self._convert_to_float(data[0][index_balance])
            vals['balance_start'] -= self._convert_to_float(data[0][import_fields.index('amount')]) \
                                            if not convert_to_amount \
                                            else self._convert_to_float(data[0][index_debit])-self._convert_to_float(data[0][index_credit])
            vals['balance_end_real'] = data[len(data)-1][index_balance]
            import_fields.remove('balance')
        # Remove debit/credit field from import_fields
        if convert_to_amount:
            import_fields.remove('debit')
            import_fields.remove('credit')

        for index, line in enumerate(data):
            line.append(statement_id)
            line.append(index)
            remove_index = []
            if convert_to_amount:
                line.append(abs(self._convert_to_float(line[index_debit]))-abs(self._convert_to_float(line[index_credit])))
                remove_index.extend([index_debit, index_credit])
            if index_balance:
                remove_index.append(index_balance)
            # Remove added field debit/credit/balance
            for index in sorted(remove_index, reverse=True):
                line.remove(line[index])
            if line[import_fields.index('amount')]:
                ret_data.append(line)
        if 'date' in import_fields:
            vals['date'] = data[len(data)-1][import_fields.index('date')]

        # add starting balance and date if there is one set in fields
        if vals:
            self.env['account.bank.statement'].browse(statement_id).write(vals)
        return ret_data


    @api.multi
    def parse_preview(self, options, count=10):
        if options.get('bank_stmt_import', False):
            self = self.with_context(bank_stmt_import=True)
        return super(AccountBankStmtImportXls, self).parse_preview(options, count=count)

    @api.multi
    def do(self, fields, options, dryrun=False):
        if options.get('bank_stmt_import', False):
            self._cr.execute('SAVEPOINT import_bank_stmt')
            vals = {
                'journal_id': self.journal_id.id,
                'reference': self.file_name,
                'name': str(self.file_name) + ' - '+ str(datetime.today().strftime('%Y-%m-%d')),
            }
            statement = self.env['account.bank.statement'].create(vals)
            res = super(AccountBankStmtImportXls, self.with_context(bank_statement_id=statement.id)).do(fields, options, dryrun=dryrun)

            try:
                if dryrun:
                    self._cr.execute('ROLLBACK TO SAVEPOINT import_bank_stmt')
                else:
                    self._cr.execute('RELEASE SAVEPOINT import_bank_stmt')
            except psycopg2.InternalError:
                pass
            return res
        else:
            return super(AccountBankStmtImportXls, self).do(fields, options, dryrun=dryrun)
