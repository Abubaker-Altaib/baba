
from odoo.exceptions import Warning,UserError, ValidationError
from odoo import api, fields, models, _
from num2words import num2words



class account_payment(models.Model):
    _inherit = 'account.payment'

    #receive_account = fields.Many2one('account.journal')
    voucher_id = fields.Many2one('account.voucher')
    payment_receive_id = fields.Many2one('account.payment','Payment Receive',readonly=1)
    from_purchase_receipts_f = fields.Boolean()
    from_purchase_receipts_s = fields.Boolean()
    amount_text = fields.Char('Amount Text', compute="_amount_to_text",readonly=1)


    @api.one
    @api.depends('amount')
    def _amount_to_text(self):
        """
        to Write Total Amount as Text
        :return: string
        """
        self.amount_text = num2words( self.amount , lang = self._context.get('lang','ar')[0:2])

    @api.multi
    def post(self):
        """
        Override post func to create new payment if this payment created from voucher
        :return:
        """
        super(account_payment,self).post()
        #I changed the self to rec to avoid the problem of conforming more than one payment
        for rec in self:
            if rec.from_purchase_receipts_f == True:

                payment = rec.env['account.payment'].create({
                'amount': rec.amount,
                'partner_id': rec.partner_id.id or None,
                'partner_type': 'supplier',
                'journal_id': rec.journal_id.id,
                'payment_date': fields.datetime.now(),
                'payment_type': 'inbound',
                'payment_method_id': 1,
                'from_purchase_receipts_s':True,
                'voucher_id':rec.voucher_id.id


                })
                rec.payment_receive_id = payment.id



    @api.onchange('payment_type')
    def fixed_payment_type(self):
        """
        restrict user from change payment type if payment created from reciept
        :return:
        """

        if self.from_purchase_receipts_f == True:
            self.payment_type = 'outbound'
            self.partner_type = 'supplier'
            self.partner_id = self.voucher_id.partner_id.id
        elif self.from_purchase_receipts_s == True:
            self.payment_type = 'inbound'
            self.partner_type = 'supplier'
            self.partner_id = self.voucher_id.partner_id.id

