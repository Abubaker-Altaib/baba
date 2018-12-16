# -*- coding: utf-8 -*-
# Copyright 2018, AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models,api, exceptions,_
import re
from odoo.exceptions import ValidationError, AccessError 
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta

class OrphanRegistrationOrder(models.Model):
    _name = 'orphan.registration.order'

    name = fields.Char("Order Sequence")
    date = fields.Date(string="Order Date",default=datetime.today())
    subject_name = fields.Char(string='Subject Name',size=256)
    local_state_id = fields.Many2one('zakat.local.state', string='Local State')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id, ondelete='restrict')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('approval', 'Approved'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel')],string="Status", default='draft')
    fageer_ids = fields.One2many('fageer.orphan.relation', 'orphan_id', string='Orphans')
    notes = fields.Text(string='Notes')

    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('name', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('orphan.registration.order.sequance') or '/'
        return super(OrphanRegistrationOrder, self).create(vals)
    
    @api.multi
    def action_confirm(self):
        """
        Change State To Confirm
        :return:
        """
        check = True
        if len(self.fageer_ids)>0:
            for rec in self.fageer_ids:
                if rec.name.state != 'done':
                    check = False
                    message = "The Case Study To ",rec.name.name," Is Not Done Yet"
                    raise ValidationError(_(message))  
        else:
            raise ValidationError(_("This Order Have No Family Members"))
        if check:
            self.write({'state': 'confirmed'})

    @api.multi
    def action_approve(self):
        """
        Change State To Approve
        :return:
        """
        self.write({'state': 'approval'})
    
    @api.multi
    def action_cancle(self):
        """
        Change State To Cancle
        :return:
        """
        self.write({'state': 'cancel'})

    @api.multi
    def action_done(self):
        """
        Change State To Done
        :return:
        """
        check = False
        for rec in self.fageer_ids:
            rec.name.orphan = True
            rec.family_ids.is_orphan = True
            if rec.name.orphan:
                check = True
        if check:
            print("_________________")
            plan = self.env['orphang.rantee.planning'].search(
            ['&', '&', ('state', '=', 'done'), ('date_from', '<=', self.date),
             ('date_to', '>=', self.date)])
            print("||||||||||||||",plan)
            for fageer in self.fageer_ids:
                for sector in plan.sector_ids:
                    print("+++++++++++++++++++++")
                    if sector.unit_of_adminstrative_id == fageer.admin_unit_id:
                        print("*******************")
                        sector.executing_actual += 1
                        sector.percentage = sector.executing_actual * 100 / sector.no_of_families
            self.write({'state': 'done'})
        else:
            raise ValidationError(_("Can\'t Make That Faqeer Orphan"))

    @api.multi
    def action_set_draft(self):
        """
        Change State To Draft
        :return:
        """
        self.write({'state': 'draft'})
    
    def unlink(self):
        if self.state != 'draft':
            raise ValidationError(_("You Can\'t Delete None Drafted Record"))
        else:
            return super(OrphanRegistrationOrder, self).unlink()


class FageerIdsClass(models.Model):
    _name = 'fageer.orphan.relation'

    name = fields.Many2one('zakat.aplication.form', string="Faqeer")
    admin_unit_id = fields.Many2one(string='Administrative Unit',related='name.faqeer_id.admin_unit')
    decision = fields.Selection([('accept', 'Accept'),
                              ('reject', 'Reject')])
    family_ids = fields.Many2one('zakat.family', string='Relative Orphan')
    orphan_id = fields.Many2one('orphan.registration.order')
