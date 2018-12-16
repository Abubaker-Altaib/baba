# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountAccountCode(models.Model):
    _inherit = 'account.account'


    parent_id = fields.Many2one('account.account','Parent Account',ondelete="set null")
    child_ids = fields.One2many('account.account','parent_id', 'Child Accounts')
    parent_left = fields.Integer('Left Parent', index=1)
    parent_right = fields.Integer('Right Parent', index=1)
    next_child = fields.Integer('next child', default=1)


    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'code, name'
    _order = 'parent_left'


    #specify a constrain on user_type_id to prevent user from changing type of parent if it has childs
    @api.constrains('user_type_id')
    def _check_child_id(self):
        child_ids=self.env['account.account'].search([('parent_id','in',self.ids)])
        if child_ids and self.ids:
            raise ValidationError(_("You can't change account type from view to another type when it has children"))


    @api.one
    @api.constrains('next_child')
    def _check_nex_child(self):
        if self.next_child<=0:
            raise Warning(_('The Next child  must be more than zero !!!!!'))

    @api.onchange('parent_id')
    def onchange_parent_id(self):
        '''
        This function generates the account number automatically with the possibility to modify it
        '''
        par_code=""
        if self.parent_id:
            par_code = self.parent_id.code
            count= self.parent_id.next_child
            serial=int(count)
            self.code = par_code+str(serial)
            serial+=1
            #self.parent_id.write({'next_child':serial})

    @api.onchange('code')
    def onchange_code(self):
        child_ids=self.env['account.account'].search([('parent_id','=',self._origin.id)])
        if child_ids and self._origin.id:
            self.next_child=1
            par_code_self=self.code
            for r in child_ids:
                count_child= self.next_child
                seria=int(count_child)
                new_code= par_code_self+str(seria)
                r.code=new_code
                r.write({'code':new_code})
                seria+=1
                self.next_child=seria

        '''This function generates the account number automatically with the possibility to modify it
        '''

    #@api.constrains('code')
    #def check_account_moves(self):
    #    """
    #     To Prevent Change code if account have moves
    #    """
    #    moves = self.env['account.move.line'].search([('account_id','=',self.id)])
    #    if len(moves) > 0:
    #        raise UserError(_("You can't change Account Code for Account have already moves"))

    @api.model
    def create(self,vals):
        """
        not change parent next child unless if parent account  changed
        """
        if vals.get('parent_id',False):
            parent_account = self.env['account.account'].search([('id','=',vals.get('parent_id'))])
            for parent in parent_account:
                parent.next_child = parent.next_child + 1


        return super(AccountAccountCode,self).create(vals)

    def write(self,vals):
        """
        not change parent next child unless if parent account  changed
        """
        if vals.get('parent_id',False):
            parent_account = self.env['account.account'].search([('id','=',vals.get('parent_id'))])
            for parent in parent_account:
                parent.next_child = parent.next_child + 1


        return super(AccountAccountCode,self).write(vals)



    @api.onchange('parent_id','user_type_id')
    def onchange_parent_id_code(self,code=False):
        '''
        1-This function generates the account number automatically with the possibility to modify it
        2-Override Onchange in parent_account module to set account code depends on account code size in setting
        :return:Integer Code
        """
        '''

        if self.parent_id and self.user_type_id.name not in ('View',False):
            # get code size from company data
            code_size  = self.env.user.company_id.account_code_size

            parent_code = self.parent_id.code
            #to make new code start with 1
            count = self.parent_id.next_child
            serial = int(count)
            code_length = len(str(parent_code)) + len(str(serial))
            #Insert zeros between main parent code and new code
            zeros = '0'
            #you can multiple strings , PYTHON IS AWOSOME ^_^
            self.code = parent_code + (zeros * (code_size - code_length)) +str(serial)
            serial += 1
            #self.parent_id.write({'next_child': serial})
        elif self.parent_id :
            parent_id = self.parent_id
            count = parent_id.next_child
            serial = int(count)
            self.code = parent_id.code + str(serial)
        #else:
        #    self.code = None
