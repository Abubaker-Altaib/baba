# -*- coding: utf-8 -*-

from odoo import models, fields, api

class hr_share(models.Model):
    _name = 'hr.share'

    name = fields.Char('Share Name')
    type_of_share = fields.Char("Type of Share")
    org = fields.Char("Organisation")
    date = fields.Date("Date")
    state = fields.Selection([('draft','Draft'),('confirm','confirm'),
             ('deduction','Waiting for deduction'),('done','done'),
            ('cancel', 'Cancelled')] , default='draft')
    share_lines =fields.One2many('hr.share.line', 'share_id', 'Share Lines', copy=False)
   

    @api.multi
    def confirm(self):    
        self.write({'state': 'confirm'})

    @api.multi
    def deduction(self):    
        self.write({'state': 'deduction'})    


    # @api.multi
    # def write(self,vals):
    #     print("################################## override write")
    #     rec = super(hr_share, self).write(vals)
    #     if 'state' in vals :
    #         for share in self:
    #             share_state = 'done'
    #             for line in share.share_lines :
    #                 if line.state == 'draft':
    #                     share_state = 'not done'
    #             if share_state == 'done':
    #                 vals.update({'state' : 'done'})        
    #     return rec

class hr_share_line(models.Model):
    _name = 'hr.share.line'

    employee_id= fields.Many2one("hr.employee","Employee")
    amount = fields.Integer("Amount")
    state = fields.Selection([('draft','Draft'),('deducted','deducted')] ,  default='draft' , readonly=True)
    share_id = fields.Many2one("hr.share",'Share')


    ### change state of share if all share line is done 
    @api.multi
    def write(self,vals):
        rec = super(hr_share_line, self).write(vals)
        for share_line in self : 
            if 'state' in vals :
                share = self.env['hr.share'].search([('id','=',share_line.share_id.id)])

                if share :
                    share_state = 'done'
                    for line in share.share_lines :
                        if line.state == 'draft':
                            share_state = 'not done'
                    if share_state == 'done':
                        share.state = 'done'     
        return rec
