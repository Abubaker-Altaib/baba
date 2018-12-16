# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import calendar
from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import float_compare, float_is_zero


class AccountAssetCategory(models.Model):
    _name = 'account.asset.category'
    _description = 'Asset category'
    _inherit = 'account.asset.category'


    depreciable = fields.Boolean(string='Depreciable', default=True)
    has_location = fields.Boolean(
        string='Has Location', default=False)
    has_barcode = fields.Boolean(string='Has Barcode', default=False)

    account_investment = fields.Many2one(
        'account.account', 'Investment Asset Account')

    account_not_investment = fields.Many2one(
        'account.account', 'Not Investment Asset Account')

    account_rehabilitation_id = fields.Many2one(
        'account.account', 'Rehabilitation Account')

    account_sale_revenue = fields.Many2one(
        'account.account', 'Sale Revenue Account')
    account_sale_lost = fields.Many2one(
        'account.account', 'Sale Lost Account')

    account_reval_id = fields.Many2one(
        'account.account', 'Revalue Account')
    account_pl_id = fields.Many2one(
        'account.account', 'P/L Account',
        help="This account is used for book value in the abandon operation.")

    asset_ids = fields.One2many(
        'account.asset.asset', 'category_id',
        string='Assets', copy=False)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'category name must be unique !'),
    ]
    
    @api.multi
    def unlink(self):
        for asset in self:
            if asset.asset_ids:
                raise UserError(_('You cannot delete a document that contains assets.'))
        return super(AccountAssetCategory, self).unlink()


class AccountAssetAsset(models.Model):
    _name = 'account.asset.asset'
    _description = 'Asset/Revenue Recognition'
    _inherit = 'account.asset.asset'
    operation_count = fields.Integer(compute='_operation_count', string='# Asset Operations')
    custody_count = fields.Integer(compute='_custody_count', string='# Asset custodies')

    value = fields.Float(
        string='Gross Value', compute='_sum_amount', method=True,
        digits=0, copy=False)
    initial_value = fields.Float(
        string='Purchase Value', required=True, readonly=True,
        digits=0, states={'draft': [('readonly', False)]})
    depreciable = fields.Boolean(
        related='category_id.depreciable', string='Depreciable',
        copy=False)
    has_location = fields.Boolean(
        related='category_id.has_location', string='Has Location',
        copy=False)
    has_barcode = fields.Boolean(
        related='category_id.has_barcode', string='Has Barcode',
        copy=False)

    operation_ids = fields.One2many(
        'account.asset.operation', 'asset_id',
        string='Operation Archive', copy=False)

    custody_ids = fields.One2many(
        'account.asset.custody', 'asset_id',
        string='Custody Archive', copy=False)
    image = fields.Binary(
        "Image", attachment=True, copy=False,
        help="This field holds the image used as photo for the asset, limited to 1024x1024px.")

    location = fields.Char(
        'Location', copy=False,
        default='{"position":{"lat":24.72401309288487,"lng":46.68484727744112},"zoom":5}')
    barcode = fields.Char('barcode', copy=False)

    document = fields.Binary(
        "Original Document", attachment=True, copy=False,
        help="This field holds the original document of the asset.")

    is_purchased = fields.Boolean(string='Purchased', default=False)
    seq = fields.Char(string='sequence', size=32, readonly=True)

    asset_type = fields.Selection(
        [('investment', 'Investment'),
         ('not_investment', 'Not Investment')],
        'Asset Type', required=True, copy=False, default='investment')

    invoice_id = fields.Many2one(
        'account.voucher', string='Invoice',
        states={'draft': [('readonly', False)]},
        copy=False)

    employee_id = fields.Many2one(
        'hr.employee', string='Employee',
        states={'draft': [('readonly', False)]},
        copy=False)

    department_id = fields.Many2one(
        'hr.department', string='Department',
        states={'draft': [('readonly', False)]},
        copy=False)

    def get_sequence_code(self, has_location=False, depreciable=False,
                          has_barcode=False):
        sequence_code = False
        if has_location and not depreciable and not has_barcode:
            sequence_code = 'asset.location'
        if not has_location and not depreciable and has_barcode:
            sequence_code = 'asset.barcode'
        if not has_location and depreciable and not has_barcode:
            sequence_code = 'asset.depreciable'
        if has_location and depreciable and not has_barcode:
            sequence_code = 'asset.location.depreciable'
        if has_location and not depreciable and has_barcode:
            sequence_code = 'asset.location.barcode'
        if not has_location and depreciable and has_barcode:
            sequence_code = 'asset.depreciable.barcode'
        if has_location and depreciable and has_barcode:
            sequence_code = 'asset.location.depreciable.barcode'
        return sequence_code

    @api.model
    def create(self, vals):

        has_location = depreciable = has_barcode = False
        if 'has_location' in vals and vals['has_location']:
            has_location = True
        if 'depreciable' in vals and vals['depreciable']:
            depreciable = True
        if 'has_barcode' in vals and vals['has_barcode']:
            has_barcode = True

        sequence_code = self.get_sequence_code(
            has_location, depreciable, has_barcode)

        vals['seq'] = self.env['ir.sequence'].next_by_code(
            sequence_code)

        asset = super(AccountAssetAsset, self.with_context(
            mail_create_nolog=True)).create(vals)
        return asset

    @api.multi
    def write(self, vals):
        if 'category_id' in vals:
            old_has_location = old_depreciable = old_has_barcode = {}
            for rec in self:
                old_has_location[rec.id] = rec.has_location
                old_depreciable[rec.id] = rec.depreciable
                old_has_barcode[rec.id] = rec.has_barcode

        res = super(AccountAssetAsset, self).write(vals)
        if 'category_id' in vals:
            for rec in self:
                if rec.has_location != old_has_location[rec.id] or rec.depreciable != old_depreciable[
                        rec.id] or rec.has_barcode != old_has_barcode[rec.id]:
                    sequence_code = self.get_sequence_code(
                        rec.has_location, rec.depreciable, rec.has_barcode)
                    seq = self.env['ir.sequence'].next_by_code(
                        sequence_code)
                    rec.write({'seq': seq})
        return res

    @api.multi
    def unlink(self):
        for asset in self:
            if asset.operation_ids:
                raise UserError(_('You cannot delete a document that contains operation.'))
        return super(AccountAssetAsset, self).unlink()

    @api.onchange('category_id')
    def onchange_category(self):
        if self.category_id:
            self.depreciable = self.category_id.depreciable
            self.has_location = self.category_id.has_location
            self.has_barcode = self.category_id.has_barcode

    @api.one
    @api.depends('initial_value', 'operation_ids')
    def _sum_amount(self):
        total_amount = self.initial_value
        last_revalution = self.operation_ids.search(
            [('type', '=', 'revalue'), ('asset_id', '=', self.id)])
        if last_revalution:
            total_amount = last_revalution[0].amount
        self.value = total_amount

    def _compute_board_undone_dotation_nb(
            self, depreciation_date, total_days):
        method_number = self.method_number
        method_period = self.method_period
        method_end = self.method_end

        last_revalution_enhance = self.operation_ids.search(
            [('type', 'in', ['revalue', 'enhance']),
             ('asset_id', '=', self.id),
             ('state', '=', 'done')])
        if last_revalution_enhance:
            last_revalution_enhance = last_revalution_enhance[0]
            method_number = last_revalution_enhance.method_number
            method_period = last_revalution_enhance.method_period
            method_end = last_revalution_enhance.method_end

        undone_dotation_number = method_number
        if self.method_time == 'end':
            end_date = datetime.strptime(method_end, DF).date()
            undone_dotation_number = 0
            while depreciation_date <= end_date:
                depreciation_date = date(
                    depreciation_date.year, depreciation_date.month,
                    depreciation_date.day) + relativedelta(
                    months=+self.method_period)
                undone_dotation_number += 1
        if self.prorata:
            undone_dotation_number += 1
        return undone_dotation_number

    def _compute_board_amount(
            self, sequence, residual_amount, amount_to_depr,
            undone_dotation_number, posted_depreciation_line_ids,
            total_days, depreciation_date):
        method_number = self.method_number
        method_period = self.method_period
        method_end = self.method_end

        last_revalution_enhance = self.operation_ids.search(
            [('type', 'in', ['revalue', 'enhance']),
             ('asset_id', '=', self.id),
             ('state', '=', 'done')])
        if last_revalution_enhance:
            last_revalution_enhance = last_revalution_enhance[0]
            method_number = last_revalution_enhance.method_number
            method_period = last_revalution_enhance.method_period
            method_end = last_revalution_enhance.method_end

        amount = 0
        if sequence == undone_dotation_number:
            amount = residual_amount
        else:
            if self.method == 'linear':
                amount = amount_to_depr / (
                    undone_dotation_number -
                    len(posted_depreciation_line_ids))
                if self.prorata:
                    amount = amount_to_depr / method_number
                    if sequence == 1:
                        if method_period % 12 != 0:
                            date = datetime.strptime(
                                self.date, '%Y-%m-%d')
                            month_days = calendar.monthrange(
                                date.year, date.month)[1]
                            days = month_days - date.day + 1
                            amount = (amount_to_depr / method_number) / \
                                month_days * days
                        else:
                            days = (self.company_id.compute_fiscalyear_dates(
                                depreciation_date)['date_to'] - depreciation_date).days + 1
                            amount = (amount_to_depr / method_number) / \
                                total_days * days
            elif self.method == 'degressive':
                amount = residual_amount * self.method_progress_factor
                if self.prorata:
                    if sequence == 1:
                        if method_period % 12 != 0:
                            date = datetime.strptime(
                                self.date, '%Y-%m-%d')
                            month_days = calendar.monthrange(
                                date.year, date.month)[1]
                            days = month_days - date.day + 1
                            amount = (
                                residual_amount * self.method_progress_factor) / month_days * days
                        else:
                            days = (self.company_id.compute_fiscalyear_dates(
                                depreciation_date)['date_to'] - depreciation_date).days + 1
                            amount = (
                                residual_amount * self.method_progress_factor) / total_days * days
        return amount

    @api.multi
    def compute_depreciation_board(self):
        self.ensure_one()

        if self.depreciable:
            method_number = self.method_number
            method_period = self.method_period
            method_end = self.method_end

            last_revalution_enhance = self.operation_ids.search(
                [('type', 'in', ['revalue', 'enhance']),
                 ('asset_id', '=', self.id),
                 ('state', '=', 'done')])
            if last_revalution_enhance:
                last_revalution_enhance = last_revalution_enhance[0]
                method_number = last_revalution_enhance.method_number
                method_period = last_revalution_enhance.method_period
                method_end = last_revalution_enhance.method_end

            posted_depreciation_line_ids = self.depreciation_line_ids.filtered(
                lambda x: x.move_check).sorted(key=lambda l: l.depreciation_date)
            unposted_depreciation_line_ids = self.depreciation_line_ids.filtered(
                lambda x: not x.move_check)

            # Remove old unposted depreciation lines. We cannot use unlink() with One2many field
            commands = [(2, line_id.id, False)
                        for line_id in unposted_depreciation_line_ids]

            if self.value_residual != 0.0:
                amount_to_depr = residual_amount = self.value_residual
                if self.prorata:
                    # if we already have some previous validated entries, starting date is last entry + method perio
                    if posted_depreciation_line_ids and posted_depreciation_line_ids[-1].depreciation_date:
                        last_depreciation_date = datetime.strptime(
                            posted_depreciation_line_ids[-1].depreciation_date, DF).date()
                        depreciation_date = last_depreciation_date + \
                            relativedelta(months=+method_period)
                    else:
                        depreciation_date = datetime.strptime(
                            self._get_last_depreciation_date()[self.id], DF).date()
                else:
                    # depreciation_date = 1st of January of purchase year if annual valuation, 1st of
                    # purchase month in other cases
                    if method_period >= 12:
                        asset_date = datetime.strptime(
                            self.date[:4] + '-01-01', DF).date()
                    else:
                        asset_date = datetime.strptime(
                            self.date[:7] + '-01', DF).date()
                    # if we already have some previous validated entries, starting date isn't 1st January but last
                    # entry + method period
                    if posted_depreciation_line_ids and posted_depreciation_line_ids[-1].depreciation_date:
                        last_depreciation_date = datetime.strptime(
                            posted_depreciation_line_ids[-1].depreciation_date, DF).date()
                        depreciation_date = last_depreciation_date + \
                            relativedelta(months=+method_period)
                    else:
                        depreciation_date = asset_date
                day = depreciation_date.day
                month = depreciation_date.month
                year = depreciation_date.year
                total_days = (year % 4) and 365 or 366

                undone_dotation_number = self._compute_board_undone_dotation_nb(
                    depreciation_date, total_days)

                for x in range(
                        len(posted_depreciation_line_ids),
                        undone_dotation_number):
                    sequence = x + 1
                    amount = self._compute_board_amount(
                        sequence, residual_amount, amount_to_depr,
                        undone_dotation_number, posted_depreciation_line_ids,
                        total_days, depreciation_date)
                    amount = self.currency_id.round(amount)
                    if float_is_zero(
                            amount,
                            precision_rounding=self.currency_id.rounding):
                        continue
                    residual_amount -= amount
                    vals = {
                        'amount': amount,
                        'asset_id': self.id,
                        'sequence': sequence,
                        'name': (self.code or '') + '/' + str(sequence),
                        'remaining_value': residual_amount,
                        'depreciated_value': self.value - (self.salvage_value + residual_amount),
                        'depreciation_date': depreciation_date.strftime(DF),
                    }
                    commands.append((0, False, vals))
                    # Considering Depr. Period as months
                    depreciation_date = date(
                        year, month, day) + relativedelta(months=+method_period)
                    day = depreciation_date.day
                    month = depreciation_date.month
                    year = depreciation_date.year

            self.write({'depreciation_line_ids': commands})

            return True
        return True

    @api.multi
    def validate(self):
        if self.is_purchased:
            asset_operation_obj = self.env['account.asset.operation']
            new_op = asset_operation_obj.create({
                'asset_id': self.id,
                'type': 'purchase',
                'date': self.date,
                'currency_id': self.currency_id.id,
                'company_id': self.company_id.id,
                'amount': self.initial_value,
                'category_id': self.category_id.id,
                'partner_id': self.partner_id.id,
                'asset_type': self.asset_type,
                'document': self.document,
                'barcode': self.barcode,
                'location': self.location,
                'image': self.image,
                'purchase_invoice_id': self.invoice_id and self.invoice_id.id or False,
                'depreciable': self.depreciable,
                'has_location': self.has_location,
                'has_barcode': self.has_barcode,
                'code': self.code,
                'asset_name': self.name,
                'employee_id': self.employee_id and employee_id.id or False,
                'department_id': self.department_id and department_id.id or False,
            })
            new_op.write({'state': 'done'})
            new_op.create_move()

        return super(AccountAssetAsset, self).validate()

    @api.multi
    @api.depends('depreciation_line_ids.move_id', 'operation_ids.move_id')
    def _entry_count(self):
        for asset in self:
            res_dep = self.env['account.asset.depreciation.line'].search_count(
                [('asset_id', '=', asset.id), ('move_id', '!=', False)])
            res_ops = self.env['account.asset.operation'].search_count(
                [('asset_id', '=', asset.id), ('move_id', '!=', False)])

            asset.entry_count = ((res_dep or 0) + (res_ops or 0)) or 0

    @api.multi
    @api.depends('operation_ids')
    def _operation_count(self):
        for asset in self:
            res_ops = self.env['account.asset.operation'].search_count(
                [('asset_id', '=', asset.id), ('move_id', '!=', False)])
            asset.operation_count = (res_ops or 0) or 0
    
    @api.multi
    @api.depends('custody_ids')
    def _custody_count(self):
        for custody in self:
            res_custody = self.env['account.asset.custody'].search_count(
                [('asset_id', '=', custody.id),])
            custody.custody_count = (res_custody or 0) or 0

    @api.multi
    def open_entries(self):
        move_ids = []
        for asset in self:
            for depreciation_line in asset.depreciation_line_ids:
                if depreciation_line.move_id:
                    move_ids.append(depreciation_line.move_id.id)

            for operation in asset.operation_ids:
                if operation.move_id:
                    move_ids.append(operation.move_id.id)
        return {
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', move_ids)],
        }

    @api.multi
    def open_entries_ops(self):
        ops_ids = []
        for asset in self:
            for operation in asset.operation_ids:
                if operation.state == 'done':
                    ops_ids.append(operation.id)
        return {
            'name': _('Asset Operations'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.asset.operation',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', ops_ids)],
        }
    

    @api.multi
    def open_entries_custody(self):
        custody_ids = []
        for asset in self:
            for custody in asset.custody_ids:
                if custody.state == 'done':
                    custody_ids.append(custody.id)
        return {
            'name': _('Asset Custodies'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.asset.custody',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', custody_ids)],
        }


class account_asset_operation(models.Model):
    """Object to record all operation (revalue, abandon and sale, ...) to asset.
    """
    _name = 'account.asset.operation'
    _description = "Operation"
    _inherit = ['mail.thread']

    @api.multi
    @api.depends('asset_id', 'type', 'date')
    def _get_name(self):
        for line in self:
            line.name = line.asset_id and line.asset_id.name or ""+"/"+line.type+"/"+line.date+"/"

    _order = "date desc"
    name = fields.Char('name', compute='_get_name', copy=False, default='/')
    asset_id = fields.Many2one(
        'account.asset.asset', string='Asset',
        states={'draft': [('readonly', False)]},
        copy=False)
    type = fields.Selection(
        [('purchase', 'Purchase'),
         ('change_type', 'Change Type'),
         ('enhance', 'Enhance'),
         ('revalue', 'Revalue'),
         ('sale', 'Sale'),
         ('abandon', 'Abandon')],
        string='type', required=True)
    date = fields.Date(
        string='Date', required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        default=fields.Date.context_today)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done')],
        'Status', required=True, copy=False, default='draft')
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,
        readonly=True, states={'draft': [('readonly', False)]},
        default=lambda self: self.env.user.company_id.currency_id.id)
    company_id = fields.Many2one(
        'res.company', string='Company', required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get(
            'account.asset.operation'))

    amount = fields.Float(
        string='amount', digits=0)
    note = fields.Text()
    move_id = fields.Many2one(
        'account.move', string='Depreciation Entry')
    move_check = fields.Boolean(
        compute='_get_move_check', string='Linked',
        track_visibility='always', store=True)
    move_posted_check = fields.Boolean(
        compute='_get_move_posted_check', string='Posted',
        track_visibility='always', store=True)

    category_id = fields.Many2one(
        'account.asset.category', string='Category')

    partner_id = fields.Many2one(
        'res.partner', string='Partner', readonly=True,
        states={'draft': [('readonly', False)]})

    purchase_invoice_id = fields.Many2one(
        'account.voucher', string='Invoice',
        states={'draft': [('readonly', False)]},
        copy=False)

    sale_invoice_id = fields.Many2one(
        'account.voucher', string='Invoice',
        states={'draft': [('readonly', False)]},
        copy=False)

    image = fields.Binary(
        "Image", attachment=True, copy=False,
        help="This field holds the image used as photo for the asset, limited to 1024x1024px.")

    location = fields.Char(
        'Location', copy=False,
        default='{"position":{"lat":24.72401309288487,"lng":46.68484727744112},"zoom":5}')
    barcode = fields.Char('barcode', copy=False)

    document = fields.Binary(
        "Original Document", attachment=True, copy=False,
        help="This field holds the original document of the asset.")

    asset_type = fields.Selection(
        [('investment', 'Investment'),
         ('not_investment', 'Not Investment')],
        'Asset Type', required=True, copy=False, default='investment')

    depreciable = fields.Boolean(
        related='category_id.depreciable', string='Depreciable',
        copy=False)
    has_location = fields.Boolean(
        related='category_id.has_location', string='Has Location',
        copy=False)
    has_barcode = fields.Boolean(
        related='category_id.has_barcode', string='Has Barcode',
        copy=False)

    code = fields.Char(
        string='Reference', size=32, readonly=True,
        states={'draft': [('readonly', False)]})
    asset_name = fields.Char(string='Asset Name')

    asset_method_number = fields.Integer(
        compute='_get_asset_dep_info',
        string='Asset Number of Depreciations')
    asset_method_period = fields.Integer(
        compute='_get_asset_dep_info', string='Asset Period Length')
    asset_method_end = fields.Date(
        compute='_get_asset_dep_info', string='Asset Ending date')

    method_number = fields.Integer(string='Number of Depreciations')
    method_period = fields.Integer(string='Period Length')
    method_end = fields.Date(string='Ending date')

    asset_method_time = fields.Char(string='Asset Method Time')

    employee_id = fields.Many2one(
        'hr.employee', string='Employee',
        states={'draft': [('readonly', False)]},
        copy=False)

    department_id = fields.Many2one(
        'hr.department', string='Department',
        states={'draft': [('readonly', False)]},
        copy=False)

    @api.multi
    def unlink(self):
        for operation in self:
            if operation.state != 'draft':
                raise UserError(_('You cannot delete a document is in %s state.') % (operation.state,))
        return super(account_asset_operation, self).unlink()

    @api.one
    def _get_asset_dep_info(self):
        if self.asset_id:
            method_number = self.asset_id.method_number
            method_period = self.asset_id.method_period
            method_end = self.asset_id.method_end

            if self.id:
                last_revalution_enhance = self.search(
                    [('type', 'in', ['revalue', 'enhance']),
                     ('asset_id', '=', self.asset_id.id),
                     ('state', '=', 'done'),
                     ('id', '!=', self.id)])
            if not self.id:
                last_revalution_enhance = self.search(
                    [('type', 'in', ['revalue', 'enhance']),
                     ('asset_id', '=', self.asset_id.id),
                     ('state', '=', 'done')])

            if last_revalution_enhance:
                last_revalution_enhance = last_revalution_enhance[0]
                method_number = last_revalution_enhance.method_number
                method_period = last_revalution_enhance.method_period
                method_end = last_revalution_enhance.method_end

            self.asset_method_number = method_number
            self.asset_method_period = method_period
            self.asset_method_end = method_end

    @api.onchange('category_id')
    def onchange_category(self):
        if self.category_id:
            self.depreciable = self.category_id.depreciable
            self.has_location = self.category_id.has_location
            self.has_barcode = self.category_id.has_barcode
        if not self.category_id and not self.asset_id:
            self.depreciable = False
            self.has_location = False
            self.has_barcode = False

    @api.onchange('asset_id')
    def onchange_asset(self):
        if self.asset_id:
            self.depreciable = self.asset_id.depreciable
            self.has_location = self.asset_id.has_location
            self.has_barcode = self.asset_id.has_barcode
            self.category_id = self.asset_id.category_id.id

            method_number = self.asset_id.method_number
            method_period = self.asset_id.method_period
            method_end = self.asset_id.method_end

            if self.id:
                last_revalution_enhance = self.search(
                    [('type', 'in', ['revalue', 'enhance']),
                     ('asset_id', '=', self.asset_id.id),
                     ('state', '=', 'done'),
                     ('id', '!=', self.id)])
            if not self.id:
                last_revalution_enhance = self.search(
                    [('type', 'in', ['revalue', 'enhance']),
                     ('asset_id', '=', self.asset_id.id),
                     ('state', '=', 'done')])

            if last_revalution_enhance:
                last_revalution_enhance = last_revalution_enhance[0]
                method_number = last_revalution_enhance.method_number
                method_period = last_revalution_enhance.method_period
                method_end = last_revalution_enhance.method_end

            self.asset_method_time = self.asset_id.method_time
            self.asset_method_number = method_number
            self.asset_method_period = method_period
            self.asset_method_end = method_end

            self.method_number = method_number
            self.method_period = method_period
            self.method_end = method_end
        if not self.asset_id and not self.category_id:
            self.depreciable = False
            self.has_location = False
            self.has_barcode = False

    @api.multi
    @api.depends('move_id')
    def _get_move_check(self):
        for line in self:
            line.move_check = bool(line.move_id)

    @api.multi
    @api.depends('move_id.state')
    def _get_move_posted_check(self):
        for line in self:
            line.move_posted_check = True if line.move_id and line.move_id.state == 'posted' else False

    @api.one
    def create_move(self):
        created_moves = self.env['account.move']
        prec = self.env['decimal.precision'].precision_get('Account')
        asset_name = self.name
        asset_id = self.asset_id
        type = self.type
        category_id = self.asset_id.category_id
        date = self.date
        amount = self.amount

        account_asset_id = False

        if self.asset_id.asset_type == 'investment':
            account_asset_id = category_id.account_investment
        elif self.asset_id.asset_type == 'not_investment':
            account_asset_id = category_id.account_not_investment

        company_currency = self.asset_id.company_id.currency_id
        current_currency = self.asset_id.currency_id

        if type == "purchase":
            account_id = self.partner_id.property_account_payable_id
            move_line_1 = {
                'account_id': account_id.id,
                'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0
            }
            move_line_2 = {
                'account_id': account_asset_id.id,
                'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0
            }
        elif type == "change_type":
            amount = self.asset_id.value
            # account_id = category_id.account_rehabilitation_id
            if self.asset_type == 'investment':
                account_id = category_id.account_investment
            elif self.asset_type == 'not_investment':
                account_id = category_id.account_not_investment

            move_line_1 = {
                'account_id': account_asset_id.id,
                'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0
            }
            move_line_2 = {
                'account_id': account_id.id,
                'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0
            }

        elif type == "enhance":
            account_id = category_id.account_rehabilitation_id
            move_line_1 = {
                'account_id': account_id.id,
                'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0
            }
            move_line_2 = {
                'account_id': account_asset_id.id,
                'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0
            }

        elif type == "revalue":
            account_id = category_id.account_reval_id
            move_line_1 = {
                'account_id': account_id.id,
                'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0
            }
            move_line_2 = {
                'account_id': account_asset_id.id,
                'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0
            }

        elif type == "abandon":
            account_id = category_id.account_pl_id

        move_line_1.update(
            {'name': asset_name, 'journal_id': category_id.journal_id.id,
             'partner_id': self.asset_id.partner_id.id,
             'analytic_account_id': category_id.account_analytic_id.id
             if category_id.type == 'sale' else False,
             'currency_id': company_currency !=
             current_currency and current_currency.id or False,
             'amount_currency': company_currency != current_currency and -1.0 *
             amount or 0.0, })

        move_line_2.update(
            {'name': asset_name, 'journal_id': category_id.journal_id.id,
             'partner_id': self.asset_id.partner_id.id,
             'analytic_account_id': category_id.account_analytic_id.id
             if category_id.type == 'purchase' else False,
             'currency_id': company_currency !=
             current_currency and current_currency.id or False,
             'amount_currency': company_currency !=
             current_currency and self.amount or 0.0, })

        move_vals = {
            'ref': self.asset_id.code,
            'date': date or False,
            'journal_id': category_id.journal_id.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
        }
        move = self.env['account.move'].create(move_vals)
        self.write({'move_id': move.id, 'move_check': True})
        if move:
            move.post()

    @api.one
    def create_voucher(self):
        invoice_obj = self.env['account.voucher']

        prec = self.env['decimal.precision'].precision_get('Account')
        asset_name = self.name
        asset_id = self.asset_id
        type = self.type
        category_id = self.asset_id.category_id
        date = self.date
        amount = self.amount
        partner_id = self.partner_id

        currency_id = self.currency_id

        if type == 'sale':
            if amount >= asset_id.value_residual:
                account_id = category_id.account_sale_revenue
            if amount < asset_id.value_residual:
                account_id = category_id.account_sale_lost
        voucher_line = {
            'name': asset_name,
            'partner_id': partner_id.id,
            'account_id': account_id.id,
            'price_unit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'company_id': self.company_id.id,
            'currency_id': currency_id.id,
        }

        invoice_vals = {
            'voucher_type': 'sale',
            'voucher_type': 'sale',
            'name': asset_name,
            'reference': self.asset_id.code,
            'date': date or False,
            'account_date': date or False,
            'currency_id': currency_id.id,
            'company_id': self.company_id.id,
            'journal_id': category_id.journal_id.id,
            'line_ids': [(0, 0, voucher_line)],
        }

        invoice = self.env['account.voucher'].create(invoice_vals)
        self.sale_invoice_id = invoice.id

    @api.multi
    def done(self):
        for rec in self:
            if rec.type == 'purchase':
                rec.asset_id.create({
                    'name': rec.asset_name,
                    'category_id': rec.category_id.id,
                    'asset_type': rec.asset_type,
                    'document': rec.document,
                    'barcode': rec.barcode,
                    'location': rec.location,
                    'image': rec.image,
                    'invoice_id': rec.purchase_invoice_id and rec.purchase_invoice_id.id or False,
                    'image': rec.image,
                    'partner_id': rec.partner_id.id,
                    'category_id': rec.category_id.id,
                    'initial_value': rec.amount,
                    'date': rec.date,
                    'company_id': rec.company_id.id,
                    'currency_id': rec.currency_id.id,
                    'depreciable': rec.category_id.depreciable,
                    'has_location': rec.category_id.has_location,
                    'has_barcode': rec.category_id.has_barcode,
                    'employee_id': self.employee_id and employee_id.id or False,
                    'department_id': self.department_id and department_id.id or False,
                })
                rec.asset_id.validate()
                rec.create_move()

            if rec.type == "change_type":
                if rec.asset_type == rec.asset_id.asset_type:
                    raise UserError(
                        _('You can not change asset type to the old one.'))
                rec.create_move()
                rec.asset_id.write({'asset_type': rec.asset_type})
            elif rec.type in ['revalue', 'enhance']:
                rec.create_move()
                if rec.depreciable and(
                        rec.asset_method_end, rec.asset_method_number, rec.asset_method_period) != (
                        rec.method_end, rec.method_number, rec.method_period):
                    # to be used in the compute_depreciation_board method
                    rec.write({'state': 'done'})
                    rec.asset_id.compute_depreciation_board()

            elif rec.type in ['sale']:
                rec.create_voucher()

            elif rec.type in ['abandon']:
                rec.abandon()
                rec.asset_id.write({'state': 'close'})

        self.write({'state': 'done'})

    @api.multi
    def open_entries(self):
        move_ids = []
        for op in self:
            move_ids.append(op.move_id.id)
        return {
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', move_ids)],
        }

    @api.multi
    def sale_invoice_id_change(self):
        for line in self:
            if not line.move_id and line.sale_invoice_id.state == 'posted' and line.type in ['sale']:
                created_moves = self.env['account.move']
                prec = line.env['decimal.precision'].precision_get('Account')
                asset_name = line.name
                asset_id = line.asset_id
                type = line.type
                category_id = line.asset_id.category_id
                date = line.date
                amount = line.amount

                account_asset_id = False

                if line.asset_id.asset_type == 'investment':
                    account_asset_id = category_id.account_investment
                elif line.asset_id.asset_type == 'not_investment':
                    account_asset_id = category_id.account_not_investment

                company_currency = line.asset_id.company_id.currency_id
                current_currency = line.asset_id.currency_id

                dep_value = line.asset_id.value - line.asset_id.value_residual - line.asset_id.salvage_value
                account_id = line.partner_id.property_account_receivable_id

                move_line_1 = {
                    'name': asset_name,
                    'account_id': account_id.id,
                    'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                    'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                    'journal_id': category_id.journal_id.id,
                    'analytic_account_id': category_id.account_analytic_id.id
                    if category_id.type == 'purchase' else False,
                    'currency_id': company_currency !=
                    current_currency and current_currency.id or False,
                    'amount_currency': company_currency !=
                    current_currency and self.amount or 0.0,
                    'partner_id': self.asset_id.partner_id.id,
                }

                move_line_2 = {
                    'name': asset_name,
                    'account_id': category_id.account_depreciation_id.id,
                    'credit': 0.0 if float_compare(dep_value, 0.0, precision_digits=prec) > 0 else -dep_value,
                    'debit': dep_value if float_compare(dep_value, 0.0, precision_digits=prec) > 0 else 0.0,
                    'journal_id': category_id.journal_id.id,
                    'analytic_account_id': category_id.account_analytic_id.id
                    if category_id.type == 'purchase' else False,
                    'currency_id': company_currency !=
                    current_currency and current_currency.id or False,
                    'amount_currency': company_currency !=
                    current_currency and self.amount or 0.0,
                }

                if amount >= asset_id.value_residual:
                    revenue = amount - asset_id.value_residual + line.asset_id.salvage_value
                    move_line_3 = {
                        'account_id': line.category_id.account_sale_revenue.id,
                        'debit': 0.0 if float_compare(revenue, 0.0, precision_digits=prec) > 0 else -revenue,
                        'credit': revenue if float_compare(revenue, 0.0, precision_digits=prec) > 0 else 0.0,
                        'journal_id': category_id.journal_id.id,
                        'analytic_account_id': category_id.account_analytic_id.id
                        if category_id.type == 'purchase' else False,
                        'currency_id': company_currency !=
                        current_currency and current_currency.id or False,
                        'amount_currency': company_currency !=
                        current_currency and self.amount or 0.0,
                    }

                if amount < asset_id.value_residual:
                    lost = asset_id.value_residual - amount + line.asset_id.salvage_value
                    move_line_3 = {
                        'name': asset_name,
                        'account_id': line.category_id.account_sale_lost.id,
                        'credit': 0.0 if float_compare(lost, 0.0, precision_digits=prec) > 0 else -lost,
                        'debit': lost if float_compare(lost, 0.0, precision_digits=prec) > 0 else 0.0,
                        'journal_id': category_id.journal_id.id,
                        'analytic_account_id': category_id.account_analytic_id.id
                        if category_id.type == 'purchase' else False,
                        'currency_id': company_currency !=
                        current_currency and current_currency.id or False,
                        'amount_currency': company_currency !=
                        current_currency and self.amount or 0.0,
                    }

                move_line_4 = {
                    'name': asset_name, 'account_id': account_asset_id.id, 'debit': 0.0
                    if float_compare(line.asset_id.value, 0.0, precision_digits=prec) > 0 else -line.asset_id.value,
                    'credit': line.asset_id.value
                    if float_compare(line.asset_id.value, 0.0, precision_digits=prec) > 0 else 0.0,
                    'journal_id': category_id.journal_id.id, 'analytic_account_id': category_id.account_analytic_id.id
                    if category_id.type == 'purchase' else False, 'currency_id': company_currency !=
                    current_currency and current_currency.id or False, 'amount_currency': company_currency !=
                    current_currency and self.amount or 0.0, }

                move_vals = {
                    'ref': line.asset_id.code,
                    'date': date or False,
                    'journal_id': category_id.journal_id.id,
                    'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2), (0, 0, move_line_3), (0, 0, move_line_4)],
                }

                move = self.env['account.move'].create(move_vals)
                line.write({'move_id': move.id, 'move_check': True})

                line.asset_id.write({'state': 'close'})

                if move:
                    move.post()

    @api.multi
    def abandon(self):
        for line in self:
            created_moves = self.env['account.move']
            prec = line.env['decimal.precision'].precision_get('Account')
            asset_name = line.name
            asset_id = line.asset_id
            type = line.type
            category_id = line.asset_id.category_id
            date = line.date

            account_asset_id = False

            if line.asset_id.asset_type == 'investment':
                account_asset_id = category_id.account_investment
            elif line.asset_id.asset_type == 'not_investment':
                account_asset_id = category_id.account_not_investment

            company_currency = line.asset_id.company_id.currency_id
            current_currency = line.asset_id.currency_id

            dep_value = line.asset_id.value - line.asset_id.value_residual - line.asset_id.salvage_value
            account_id = category_id.account_pl_id

            amount = line.asset_id.value - dep_value
            move_line_1 = {
                'name': asset_name,
                'account_id': account_id.id,
                'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': category_id.journal_id.id,
                'analytic_account_id': category_id.account_analytic_id.id
                if category_id.type == 'purchase' else False,
                'currency_id': company_currency !=
                current_currency and current_currency.id or False,
                'amount_currency': company_currency !=
                current_currency and self.amount or 0.0,
            }

            move_line_2 = {
                'name': asset_name,
                'account_id': category_id.account_depreciation_id.id,
                'credit': 0.0 if float_compare(dep_value, 0.0, precision_digits=prec) > 0 else -dep_value,
                'debit': dep_value if float_compare(dep_value, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': category_id.journal_id.id,
                'analytic_account_id': category_id.account_analytic_id.id
                if category_id.type == 'purchase' else False,
                'currency_id': company_currency !=
                current_currency and current_currency.id or False,
                'amount_currency': company_currency !=
                current_currency and self.amount or 0.0,
            }

            move_line_3 = {
                'name': asset_name, 'account_id': account_asset_id.id, 'debit': 0.0
                if float_compare(line.asset_id.value, 0.0, precision_digits=prec) > 0 else -line.asset_id.value,
                'credit': line.asset_id.value
                if float_compare(line.asset_id.value, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': category_id.journal_id.id, 'analytic_account_id': category_id.account_analytic_id.id
                if category_id.type == 'purchase' else False, 'currency_id': company_currency !=
                current_currency and current_currency.id or False, 'amount_currency': company_currency !=
                current_currency and self.amount or 0.0, }

            move_vals = {
                'ref': line.asset_id.code,
                'date': date or False,
                'journal_id': category_id.journal_id.id,
                'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2), (0, 0, move_line_3)],
            }

            move = self.env['account.move'].create(move_vals)
            line.write({'move_id': move.id, 'move_check': True, 'amount': amount})

            line.asset_id.write({'state': 'close'})

            if move:
                move.post()


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def write(self, vals):
        res = super(AccountVoucher, self).write(vals)
        if 'state' in vals and vals['state'] == 'posted':
            asset_operation_obj = self.env['account.asset.operation']
            for rec in self:
                ops = asset_operation_obj.search([('sale_invoice_id', '=', rec.id)])
                ops.sale_invoice_id_change()

        return res


class account_asset_custody(models.Model):
    """Object to record all custody to asset.
    """
    _name = 'account.asset.custody'
    _description = "Asset Custody"
    _inherit = ['mail.thread']

    _order = "date desc"

    @api.multi
    @api.depends('asset_id', 'employee_id', 'department_id', 'date')
    def _get_name(self):
        for line in self:
            line.name = line.asset_id and line.asset_id.name or "" + "/" + (
                line.employee_id and(line.employee_id.name + "/") or "" + line.department_id
                and(line.department_id.name + "/") or "") + "/" + line.date + "/"

    name = fields.Char('name', compute='_get_name', copy=False, default='/')
    asset_id = fields.Many2one(
        'account.asset.asset', string='Asset',
        states={'draft': [('readonly', False)]},
        copy=False)

    date = fields.Date(
        string='Date', required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        default=fields.Date.context_today)

    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done')],
        'Status', required=True, copy=False, default='draft')

    asset_employee_id = fields.Many2one(
        'hr.employee', string='Asset Employee', compute='_get_asset_info',
        states={'draft': [('readonly', False)]}, store=True,
        copy=False)

    asset_department_id = fields.Many2one(
        'hr.department', string='Asset Department', compute='_get_asset_info',
        states={'draft': [('readonly', False)]}, store=True,
        copy=False)

    employee_id = fields.Many2one(
        'hr.employee', string='Employee',
        states={'draft': [('readonly', False)]},
        copy=False)

    department_id = fields.Many2one(
        'hr.department', string='Department',
        states={'draft': [('readonly', False)]},
        copy=False)

    company_id = fields.Many2one(
        'res.company', string='Company', required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get(
            'account.asset.custody'))

    @api.one
    def _get_asset_info(self):
        if self.asset_id:
            department_id = self.asset_id.department_id
            employee_id = self.asset_id.employee_id

            self.asset_department_id = department_id
            self.asset_employee_id = employee_id

    @api.onchange('asset_id')
    def onchange_asset(self):
        if self.asset_id:
            self.asset_department_id = self.asset_id.department_id
            self.asset_employee_id = self.asset_id.employee_id
        else:
            self.asset_department_id = False
            self.asset_employee_id = False

    @api.multi
    def done(self):
        for rec in self:
            if (rec.asset_employee_id and rec.asset_employee_id.id or False, rec.asset_department_id and
                rec.asset_department_id.id or False) == (rec.employee_id and rec.employee_id.id or False,
                                                         rec.department_id and rec.department_id.id or False):
                raise UserError(
                    _('You can not change asset custody to the old one.'))
            rec.asset_id.write({'employee_id': rec.employee_id.id, 'department_id': rec.department_id.id, })

        self.write({'state': 'done'})
