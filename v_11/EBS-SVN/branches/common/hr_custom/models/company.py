from odoo import api, fields, models,_
from odoo.exceptions import Warning,UserError, ValidationError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    age_pension = fields.Integer("Age Pention")


    @api.model    
    def create(self, vals):
        """Method that overwrites create method and check settings fields and change their values in
            res.company
        @param vals: dictionary contains the entered values 
        @return: the new record
        """
        if(len(str(vals['age_pension'])) >= 3 or vals['age_pension'] < 0 ):
            raise UserError(_('Length Of Age Pension Should Be Less Than Three Numbers'))
        if vals['age_pension'] < 0:
            raise UserError(_('Value Of Age Pension Should Be More Than Zero'))

        res=super(ResConfigSettings, self).create(vals)
       
        company=self.env['res.users'].search([('id','=',self._uid)]).company_id

        company.write({'age_pension':vals['age_pension']})
        return res


    @api.multi
    def write(self, vals):
        company=self.env['res.users'].search([('id','=',self._uid)]).company_id
        res = super(ResConfigSettings, self).write(vals)

        for rec in self :

            age_pension = rec.age_pension
            if 'age_pension' in vals :
                age_pension = vals['age_pension']

            if(len(str(age_pension)) >= 3 ):
                raise UserError(('Length Of Age Pension Should Be Less Than Three Numbers'))
            if age_pension < 0:
                raise UserError(_('Value Of Age Pension Should Be More Than Zero'))

            company.write({'age_pension':age_pension })
        
        return res


    @api.model
    def default_get(self, fields):

        res = super(ResConfigSettings, self).default_get(fields)
        company=self.env['res.users'].search([('id','=',self._uid)]).company_id

        age_pension= company.age_pension

        res.update({'age_pension': age_pension})
        return res



class hr_config_settings_inherit(models.Model):
    """Inherits res.company to add feilds that spesify the employee types that can undergone the process.
    """
    _inherit = 'res.company'

    age_pension = fields.Integer("Age Pention")

