from odoo import fields, models, api, exceptions, _
from datetime import datetime, timedelta


class GaremeenComitte(models.Model):
    _name = 'garmeen.committte'
    name = fields.Char(string='Name')
    code = fields.Char(string='Ref')
    date = fields.Date(string='Date', default=datetime.today())
    state_id = fields.Many2one('zakat.state', 'State')
    local_state_id = fields.Many2one('zakat.local.state', 'Local Sate')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    order_ids = fields.Many2many('dzc_6.garm.request', string='orders')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('done', 'Done'), ('cancel', 'Cancel')],
                             default='draft', string='status')

    @api.constrains('name')
    def name_valiation(self):
        notvalid = False
        for letter in self.name:
            if (not letter.isalpha() and not letter.isdigit()):
                notvalid = True
        if notvalid:
            raise exceptions.ValidationError(_(
                'name Should contain just Charactors or numbers and can not begin with white Space or special charactor'))

    @api.multi
    def confirm_action(self):
        if not self.order_ids:
            raise exceptions.UserError(_('You MUST select at least one Order'))
        else:
            self.write({'state': 'confirm'})

    @api.multi
    def draft_action(self):
        self.write({'state': 'draft'})

    @api.multi
    def done_action(self):
        self.write({'state': 'done'})

    @api.multi
    def cancel_action(self):
        self.write({'state': 'cancel'})

    @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise exceptions.UserError(_('Sorry You Can not Delete non Draft Record'))

    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.sequence.number_next_actual

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('garmeen.committte') or '/'
        return super(GaremeenComitte, self).create(vals)
