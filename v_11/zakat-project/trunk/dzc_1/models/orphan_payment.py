
from odoo import fields, models, api, exceptions, _
import re
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from datetime import date
##################################################################
#  Payment of orphan sponsorship
##################################################################

class OrphanSponsorshipPayment(models.Model):
    _name = 'zakat.orphan.sponsorship.payment'

    _inherits = {'zakat.guarantee.order': 'order_id'}
    _order = "create_date desc"

    name = fields.Char(string='Order Number')
    guaranteed_ids = fields.One2many('zakat.orphans.list', 'orphan_order')
    type = fields.Selection([('s_support', 'Social Support'),
                             ('i_health', 'Insurance Health'),
                             ('student', 'Student'),
                             ('orphan', 'Orphan')], default='s_support')

    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('done', 'Done'), ('cancel', 'Cancel')],
        default="draft", string="Status")
    salary_total = fields.Float(string="Total Salary")
    orphan_no = fields.Integer(string="Orphans")
    local_state_id = fields.Many2one('zakat.local.state' , string="Local State")
    notes = fields.Text(String="Notes")
    """
    Workflow states
    """

    @api.multi
    def confirm_action(self):
        if not self.guaranteed_ids:
            raise UserError(_('There is No Orphans to Pay For.'))
        else:
            self.write({'state': 'confirm'})

    @api.multi
    def cancel_action(self):
        self.write({'state': 'cancel'})

   
    @api.multi
    def done_action(self):
        guarantees = self.env['zakat.guarantees'].search([('company_id', '=', self.env.user.company_id.id),
                                                              ('type', '=', self.type)])
        
        orphans_line = []
        for rec in self.guaranteed_ids:
            orphans_line +=  [(0, 6, {
            'name': rec.guaranteed_id.name,
            'account_id': guarantees.property_account_id.id,
            'quantity': 1,
            'name': _('Orphan Support'),
            'price_unit': guarantees.amount,
            })]

            voucher = self.env['account.voucher'].create(
                {
                'name': rec.guaranteed_id.name ,
                'journal_id': guarantees.journal_id.id,
                'company_id': guarantees.company_id.id,
                'pay_now': 'pay_later',
                'partner_id':rec.guaranteed_id.faqeer_id.id,
                'reference':rec.guaranteed_id.name,
                'voucher_type': 'purchase',
                'line_ids' :orphans_line,
                })
            rec.vaucher_id = voucher.id
            orphans_line = []
        self.write({'state': 'done'})

    @api.multi
    def set_to_draft_action(self):
        self.write({'state': 'draft'})

    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('orphan_sponsorship_payment.sequence') or '/'
        return super(OrphanSponsorshipPayment, self).create(vals)

    """
    unlinke can not be in done state
    """

    @api.multi
    def unlink(self):
        for record in self:
            if record.state not in ('draft'):
                raise UserError(_('Sorry! You Cannot Delete Order In Not Draft State.'))
        return models.Model.unlink(self)

    @api.multi
    def get_data(self):
        amount = 0
        if self.type == 'orphan':
            guarantees = self.env['zakat.guarantees'].search([('company_id', '=', self.env.user.company_id.id),
                                                              ('type', '=', self.type)])
            if not guarantees:
                raise exceptions.ValidationError(_("You Must have Orphan Guarantess in Configuration!!"))

            amount = guarantees.amount
            data = self.env['zakat.aplication.form'].search(['&', ('orphan', '=', True), ('state', '=', 'done'),('local_state_id','=', self.local_state_id.id)])

            if not data:
                raise exceptions.ValidationError(_("There is no Data of orphan "))
            faqir_line = {}
            salary_sum = 0.0
            orphan_num = 0
            for record in data:
                faqir_line = {}
                salary_sum += amount
                orphan_num += 1

                faqir_line = self.guaranteed_ids.create(
                    {
                        'guaranteed_id': record.id,
                        'salary': amount,
                        'unit_admin': record.faqeer_id.admin_unit.id
                    })

                self.guaranteed_ids += faqir_line
            self.salary_total = salary_sum
            self.orphan_no = orphan_num


"""
Orphan Guarnteed list
"""


class OrphanList(models.Model):
    _name = 'zakat.orphans.list'

    orphan_order = fields.Many2one('zakat.orphan.sponsorship.payment', store=True)
    guaranteed_id = fields.Many2one('zakat.aplication.form', store=True)
    unit_admin = fields.Many2one(related="guaranteed_id.admin_unit_id", store=True, string="Adminstrative Unit")
    salary = fields.Float(string="Salary")
    vaucher_id = fields.Many2one('account.voucher')
    

    _sql_constraints = [('uniq_guaranteed_orphan_order', 'unique(guaranteed_id,orphan_order)',
                         _("Guarantee Cannot Be Given To the Same Person Twice !"))]
