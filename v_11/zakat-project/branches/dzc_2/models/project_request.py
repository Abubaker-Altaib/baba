import re
import math
from datetime import datetime ,date
from dateutil import relativedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError
from odoo.exceptions import UserError


class dzc_2ProjectRequest(models.Model):
    _name = 'dzc2.project.request'
    _rec_name = 'project_conf'
    
    #############################
    #  OUTER FORM FIELDS
    ############################# 

    # @api.multi
    # @api.onchange( 'individual_partner','collective_partner','service_partner')
    # def _onchange_complete(self):
    #     part = []
    #     if self.type_of_project:
    #         if self.type_of_project == 'individual_production':
    #             pro = self.env['dzc2.project.request'].search(['&',('type_of_project','=', self.type_of_project),('individual_partner', '=', self.individual_partner.id)])
    #             for p in pro:
    #                 part.append(p.id)
    #         if self.type_of_project == 'collective_production':
    #             for rec in self.collective_partner:
    #                 pro = self.env['dzc2.project.request'].search(['&',('type_of_project','=', self.type_of_project),('collective_partner', '=', rec.id)])
                    
    #                 for p in pro:
    #                     part.append(p.id)
    #     return {'domain': {'complete_project_name': [('id' , 'in', part)]}}  
    
    @api.multi
    @api.onchange('project_sectors')
    def _onchange_sector(self):
        localstates = []
        if self.project_sectors:            
            for lo in self.project_sectors:
                localState = self.env['local.states.sectors'].search([('local_state','=', lo.id)])
                for local in localState:
                    ls = self.env['zakat.local.state'].search([('id','=', local.sector_local_states.id)])
                    localstates.append(ls.id)
        return {'domain': {'project_local_state': [('id' , 'in', localstates)]}}  
    
    # @api.one
    # @api.depends('project_status')
    # def onchange_name(self):
    #     if self.project_status == 'complete':
    #         self.name_req = self.complete_project_name.project_conf.name
    #         # self.write({'name_req':self.project_conf}) 
    #     else:
    #         self.name_req = self.project_conf.name
    #         # self.write({'name_req':self.complete_project_name}) 
        
    address_id = fields.Many2one('addresses','Address')
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user, ondelete='restrict')
    date = fields.Date(string="Date", default=datetime.today())
    name = fields.Char(string="Reference Number", readonly=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id, ondelete='restrict')
    type_of_project = fields.Selection([('individual_production' ,'Individual Production') , 
     ('collective_production' , 'Collective Production') , 
     ('service' , 'Service')])
    service_type = fields.Selection([('water' ,'Water') , 
     ('health' , 'Health') , 
     ('education' , 'Education')])
    # project_status = fields.Selection([('new' ,'New') , 
    #  ('finance' , 'Finance') , 
    #  ('complete' , 'Complete')] , default="new"  )
    
    """
    res.partner
    """
    support_cancel_date = fields.Date(string="Date Of Caneling Social Support")
    individual_partner = fields.Many2one('zakat.aplication.form' , string="Beneficiary")
    collective_partner = fields.Many2many('zakat.aplication.form' , 'collective_fageer_tb' , 'project_id' , 'f_id' , string="Beneficiaries")
    service_partner = fields.Many2many('zakat.aplication.form' , 'service_fageer_tb' , 'project_id' , 'fageer_id' , string="Beneficiaries")
   
    
    # complete_project_name = fields.Many2one('dzc2.project.request',string="Complete Project Name" , domain="[('individual_partner.create_project','=','c_i')]")
    is_complete_project = fields.Boolean('Complete Project?')

    from_organization = fields.Selection([('yes' , 'Yes') , ('no' , 'No')], default="no")
    organization_name = fields.Many2one('dzc2.organizations' , string="Organizations")
    state = fields.Selection([('draft' , 'Draft') , ('applied' , 'Applied') , ('accepted' , 'Accepted'),('confirmed' , 'Confirmed') ,('recommended' , 'Recommended'),('cancel' , 'Cancel'),('done' , 'Done')], default='draft' , string="Status")
    state_description = fields.Text(string="Case Description")
   
    project_state = fields.Many2one('zakat.state' , string="Project State" )
    project_sectors = fields.Many2one('zakat.sectors' , string="Project Sector" )
    project_local_state = fields.Many2one('zakat.local.state' , string="Project Local State" )
    project_village = fields.Char(string="Project village" )
    support_organization_name = fields.Char(string="Supported Name")

    #############################
    # Page (** BASIC INFO **) FORM FIELDS
    ############################# 
  
    relation_of_benefitaries = fields.Many2many('dzc2.benefitaries.relation' , 'relation_between_benefitiries' , 'benefiter_id' , 'project_id',string="Relation Between Beneficiaries")
    staff_nums = fields.Integer(string="Project Staff Number" )
    other_type = fields.Char(string="Other")
    comment = fields.Text(string="Comment")
    organization_do_study = fields.Char(string='Organization Do Study')
    project_need = fields.Many2one('dzc2.project.need' , string='Need Of Project ?')
    other_supporter = fields.Char(string="Other Supporters")
    finance_type = fields.Many2one('dzc2.finance.type')
    created_in = fields.Selection([('wlaya','Alwlaya'),('amana','Alamana')],string ="Created In")
    #############################
    # Page (** PROJECT EXPERIENCE **) FORM FIELDS
    ############################# 
    project_experience = fields.Selection([('good' , 'Good') ,
     ('medium' , 'Medium') , ('there_is_no' , 'There Is No')], default="there_is_no")
    training_type = fields.Selection([('initial' , 'Initial') ,
     ('advance' , 'Advance')])
    training_organization = fields.Selection([('zakat' , 'Zakat') ,
     ('special' , 'Special')])
    
    #############################
    # Page (** FINANCE INFO **) FORM FIELDS
    ############################# 
    zakat_project_relation = fields.Many2one('dzc2.zakat.project.relation')
    society_acceptance = fields.Selection([('excellent' , 'Excellent') ,
     ('good' , 'Good') , ('medium' , 'Medium') 
     ,('week' , 'week') 
     , ('nothing' , 'Nothing')])
    
    #############################
    # Page (** SUPPORT INFO **) FORM FIELDS
    ############################# 
    support_type = fields.Selection([('monetary' , 'Monetary') ,
     ('material' , 'Material')] , default="monetary")

    monetary_amount = fields.Float(string="")
    label_money = fields.Char(string="SDG")
    label_material = fields.Char(string="Material Cost")


    # material_type = fields.Char(string="Type")
    operation_ores = fields.Selection([('local' , 'Local') ,
     ('imported' , 'Imported')] )
    part_cost  = fields.Float(string='Support Amount')
   
    #############################
    # Page (** ADVANCE INFO **) FORM FIELDS
    ############################# 
    legal_constrains = fields.Text()
   
    validity_period = fields.Char(string="Period of Validity")
    project_manager = fields.Selection([('by_himself' , 'By Himself'), ('one_of_family','On Of Family') , ('salary_worker' , 'Salary Worker')])
    comment_2 = fields.Text(string="Comment")
    zakat_pay_manner = fields.Selection([('monetary_by_dates' , 'Monetary By Dates'), ('material_contributions','Material Contributions') , ('facilities' , 'Facilities')])
    total_cost = fields.Float(string="Project Total Cost")
    
    #############################
    # Page (** DOCUMENTS **) FORM FIELDS
    ############################# 
    has_casestudy = fields.Selection([('yes' , 'Yes') , ('no' , 'No')] , default="no")
    feasibility_study = fields.Binary(string='Feasibility Study')
    r_managment_ability_confirmation = fields.Boolean(related='project_conf.managment_ability_confirmation')
    r_project_licence = fields.Boolean(related='project_conf.project_licence' , String = "Licence")
    r_implementation_contracts = fields.Boolean(related='project_conf.implementation_contracts')
    r_experience_certificate = fields.Boolean(related='project_conf.experience_certificate')
    r_practicing_certificate = fields.Boolean(related='project_conf.practicing_certificate')
    r_residence_certificate = fields.Boolean(related='project_conf.residence_certificate')
    managment_ability_confirmation = fields.Boolean( String = "Confirmation of the ability to manage the project")
    project_licence = fields.Boolean(String = "Licence")
    implementation_contracts = fields.Boolean(String = "Project Implementation Contracts")
    experience_certificate = fields.Boolean(String = "Experience Certificate")
    practicing_certificate = fields.Boolean(String = "Practicing Certificate")
    residence_certificate = fields.Boolean(String = "Residence Certificate")
    #############################
    # Page (** RECOMMENDATIONS **) FORM FIELDS
    ############################# 
    msaref_manager_comment = fields.Text(string='Masaref Manager in Local State Comment')
    lstate_manager_recommendation = fields.Text(string='Local State Manager Recommendation')
    project_manager_reco = fields.Text(string="Projects Manager Recommendation" ,domain="[('type_of_project','not in',('individual_production','collective_production'))]")
    project_manager_recommend = fields.Text(string="Projects Manager Recommendation" ,domain="[('type_of_project','in',('individual_production','collective_production'))]")
    state_secretary_decision = fields.Text(string="Secretary of State Decision" ,domain="[('type_of_project','in',('individual_production','collective_production'))]")
    state_secretary_rcom = fields.Text(string= "State Secretary Recommendation", domain="[('type_of_project','=','service')]")
    general_secretary_recom = fields.Text(string="General Secretary Decision", domain="[('type_of_project','=','service')]")
    
    ################## PLAN , Prepare #################
    
    plan_ids_request = fields.Many2one('dzc2.project.budget.plan_idsning')
    prepairing_support = fields.Many2one('dzc2.states.support')
    project_conf = fields.Many2one('dzc2.project' , string="Project Name")
    name_req  = fields.Char( string="Project Name")
    """
    Product of material request
    """
    product_id  =   fields.Many2many('product.product','project_product','p_id','pro_id',string='Product')

    _sql_constraints = [
        ('individual_id_uniq', 'unique (individual_partner)',
         'This Beneficiary Already has previouse support !')]

    _sql_constraints = [
        ('coll_id_uniq', 'unique (collective_partner)',
         'This Beneficiary Already has previouse support !')]

    _sql_constraints = [
        ('service_id_uniq', 'unique (service_partner)',
         'This Beneficiary Already has previouse support !')]
    product_e_ids = fields.One2many('request.e.products' , 'request_id')
    product_p_ids = fields.One2many('request.p.products' , 'request_id')
    require_exchange_order = fields.Boolean(related='project_conf.require_exchange_order')
    require_purchase_order = fields.Boolean(related='project_conf.require_purchase_order')
###################### form sequence number ###########
    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, vals):
        vals['name'] = self.sudo().env['ir.sequence'].sudo().next_by_code('dzc2.project.request.sequence') or '/'
        # plan_ids = []
        # if self.type_of_project in ('individual_production','collective_production'):
      
        #     plan_ids = self.env['dzc2.project.budget.planning'].search(['&',('state_plan_ids' , '=' , self.project_state.id),('project_plan_id.state','=','done') ,'&',('project_plan_id.duration_from' , '<=' , self.date),('project_plan_id.duration_to' , '>=' , self.date)])
        #     if len(plan_ids) > 0 :
        #         True
        #     else:
        #         raise exceptions.ValidationError(_('There is no plan set for this project'))

        # else :

        #     plan_ids =self.env['dzc2.states.support'].search([('state_ids','=',self.project_state.id),('projects.id','=',project_root.parent_ids.id),('prepairing_support_id.duration_from','<=',self.date),('prepairing_support_id.duration_to','>=',self.date)])
        #     if len(plan_ids) > 0 :
        #         True
        #     else:
        #         raise exceptions.ValidationError(_('There is no plan set for this project'))


        return super(dzc_2ProjectRequest, self).create(vals)
        


       
    #########################################
    # STATES FLOW
    #########################################
    @api.multi
    def apply(self):
        # if self.type_of_project == 'individual_production':
        #     self.individual_partner.case_study = False
        # if self.type_of_project == 'collective_production':
        #     for rec in self.collective_partner:
        #         rec.case_study = False

        self.write({'state': 'applied'})
    @api.multi
    @api.onchange('project_conf')
    def product_get(self):
        if self.project_conf.type_of_products == 'fixed':
            if self.project_conf.require_purchase_order:
                self.product_p_ids.unlink()
                for line in self.project_conf.product_p_ids:
                    x = self.env['request.p.products'].create({
                        'product_id':line.product_id.id ,
                        'request_id' : self._origin.id,
                        'product_qty' : line.product_qty
                    })
            if self.project_conf.require_exchange_order:
                self.product_e_ids.unlink()
                for line in self.project_conf.product_e_ids:
                    x = self.env['request.e.products'].create({
                        'product_id':line.product_id.id ,
                        'request_id' : self._origin.id,
                        'product_qty' : line.product_qty
                    })
            
                
    
    @api.multi
    def accept(self):
          self.write({'state': 'accepted'})
    @api.multi
    def confirm(self):
          self.write({'state': 'confirmed'})
    @api.multi
    def recommend(self):
          # if self.type_of_project == 'service':
          #   if self.service_partner:
          #       for rec in self.service_partner:
          #           rec.service_partner = False

            self.write({'state':'recommended'})

          # else:
          #   self.write({'state': 'confirm'})
    @api.multi
    def cancle(self):
        self.write({'state':'cancle'})

    @api.multi
    def set_to_draft(self):
        self.write({'state':'draft'})    
    @api.multi
    def approve(self):
    

        plan_ids = []
        plans = []
        project_root = []
        
        if self.created_in == 'amana':
            if self.type_of_project == 'service':
                project_root = self.env['dzc2.project'].search([('id','=',self.project_conf.id)])
                basic_root = 0
                while project_root.parent_ids:
                    if project_root.parent_ids.is_basic == True :
                        basic_root = project_root.parent_ids.id 
                        break 
                    else:
                        project_root = self.env['dzc2.project'].search([('id','=',project_root.parent_ids.id)])

                plan_ids = self.env['dzc2.states.support'].search([('state_ids','=',self.project_state.id),('projects.id','=',project_root.parent_ids.id),('prepairing_support_id.duration_from','<=',self.date),('prepairing_support_id.duration_to','>=',self.date)])
                if plan_ids :
                    plan_ids.excute_amount += self.part_cost
                else :
                    raise exceptions.ValidationError(_('There is no plan for this project type '))
            else :
                plan_ids = self.env['dzc2.prepairing.states.support'].search([('duration_from','<=',self.date),('duration_to','>=',self.date)])
                if plan_ids :
                    plan_ids.amana_execute_support += self.part_cost 
                else :
                    raise exceptions.ValidationError(_('There is no plan for this project type '))




        ################################################################
        plans = self.env['dzc2.project.budget.planning'].search(['&',('state_plan_ids' , '=' , self.project_state.id),('project_plan_id.state','=','done') ,'&',('project_plan_id.duration_from' , '<=' , self.date),('project_plan_id.duration_to' , '>=' , self.date)])
        pro = 0.0
        bud = 0.0
        ps = self.env['dzc2.project.planning'].search(['&',('state','=','done') ,'&',('duration_from' , '<=' , self.date),('duration_to' , '>=' , self.date)])
        self.env.context  = {'request_cont' : True}

        for r in ps.plan_ids:

            pro += r.execute_from_projects
            bud += r.execute_from_budget
            
        for rec in plans :
            rec.execute_from_projects += 1
            rec.execute_from_budget += self.part_cost
            rec.project_plan_id.total_execued_projects = pro + 1
            rec.project_plan_id.total_executed_budget = bud + self.part_cost

            if rec.execute_from_projects > 0.0 :
                rec.performance = rec.execute_from_projects / rec.share_from_projects * 100
            else:
                True

        if self.individual_partner:
            self.individual_partner.project = True
        elif self.collective_partner:
            for case in self.collective_partner:
                case.project = True
        elif self.service_partner:
            for case in self.service_partner:
                case.project = True

        partner_ids = []
        if self.type_of_project == 'individual_production':
            partner_ids.append(self.individual_partner.faqeer_id.id)
           # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',partner_ids)
        elif self.type_of_project == 'collective_production':
            for partner in self.collective_partner:
                partner_ids.append(partner.id)
           # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',partner_ids)
        elif self.type_of_project == 'service':
            for partner in self.service_partner:
                partner_ids.append(partner.faqeer_id.id)
       # print('+++++++++++++++++++++++',len(self.env['zakat.aplication.form'].search([('faqeer_id' , 'in' , partner_ids)])) )
        if len(self.env['zakat.aplication.form'].search(['&',('faqeer_id' , 'in' , partner_ids),('s_support' , '=' , True)])) > 0:
            self.write({'support_cancel_date' : datetime.today()})
        self.write({'state': 'done'})


   
    @api.multi
    def cancel(self):
          self.write({'state': 'cancel'}) 

    @api.multi
    def unlink(self):
        # check field state: all should be clear before we can unlink a field:
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_("You Can\'t Delete None Drafted Record"))
            else:
                return super(dzc_2ProjectRequest, self).unlink()



      #########################################
    # VALIDATION CONSTRAINS ON NUMARIC FIELDS
    #########################################
    @api.constrains('benefitaries' ,'staff_nums'  ,'total_cost' )
    def validate_numaric_values(self):
       
        if self.staff_nums < 0 :
            raise ValidationError(_('Sorry ! Staff Number Can Not Be Negative.'))
        
        elif self.total_cost <= 0.0 :
            raise ValidationError(_('Sorry ! Total Cost Can Not Be Negative Or Zero.'))
    
    # @api.constrains('project_status')
    # def project_status_validation(self):
    #     if self.type_of_project == 'service' and self.project_status == 'complete':
    #         raise ValidationError(_('Complete projects not allowed for service projects , please check project status type.'))
    
    
    #########################################
    # VALIDATION ON REQUIRED FIELDS
    #########################################
       ##### PROJECT VILLAGE #######
    # @api.constrains('project_village')
    # def village_validation(self):
    #     inc = 0
    #     if len(self.project_village) > 1 :
    #         for rec in self.project_village[1:]:
    #             if rec.isalpha() or rec.isdigit():
    #                 inc +=1

    #             if inc == 0 :
    #                 raise ValidationError(_("Sorry! Project Village Name Field is Required ."))

    #     elif len(self.project_village) <= 1 and self.project_village[0] == ' ':
    #         raise ValidationError(_("Sorry! Project Village Name Field is Required ."))


  ################## STATE DESCRIPTION ###############
    # @api.constrains('state_description')
    # def state_description_validation(self):
    #     inc = 0
    #     if len(self.state_description) > 1 :
    #         for rec in self.state_description[1:]:
    #             if rec.isalpha() or rec.isdigit():
    #                 inc +=1

    #             if inc == 0 :
    #                 raise ValidationError(_("Sorry! State Description Field is Required ."))

    #     elif len(self.state_description) <= 1 and self.state_description[0] == ' ':
    #         raise ValidationError(_("Sorry! State Description Field is Required ."))

   
######################################################################################################
# RELATION BETWEEN BENEFITERIES
######################################################################################################
class Benefetries_relation(models.Model):
    _name = 'dzc2.benefitaries.relation'

    name = fields.Char(string="Benefiter Name")
    company_id = fields.Many2one('res.company', invisible=True, string="Company", default=lambda self: self.env.user.company_id, ondelete='restrict')

##################################################################################################
# Need Of project
###################################################################################################
class project_need(models.Model):
    _name = 'dzc2.project.need'

    name = fields.Char(string="Need Name")
    company_id = fields.Many2one('res.company',invisible=True, string="Company", default=lambda self: self.env.user.company_id, ondelete='restrict')
##################################################################################################
# Finance Type
###################################################################################################
class finance_type(models.Model):
    _name = 'dzc2.finance.type'

    name = fields.Char(string="Finance Type Name")
    company_id = fields.Many2one('res.company',invisible=True, string="Company", default=lambda self: self.env.user.company_id, ondelete='restrict')
##################################################################################################
# Zakat project Relation
###################################################################################################
class zakat_relation(models.Model):
    _name = 'dzc2.zakat.project.relation'

    name = fields.Char(string="Relation Name")
    company_id = fields.Many2one('res.company',invisible=True, string="Company", default=lambda self: self.env.user.company_id, ondelete='restrict')
###################################################


class ApplicationForm(models.Model):
    _inherit = 'zakat.aplication.form'

    @api.multi
    @api.onchange('create_project')
    def project_domain(self):
        """
        Return Hospitl if type = it adn pharmacy if type = durgs
        :return:
        # """
        if self.create_project == 'e_c':
            project_ids = []
            for project in self.env['dzc2.project.request'].search([('type_of_project', '=', 'collective_production')]):
                project_ids.append(project.id)
            return {'domain':{'project_created':[('id', 'in', project_ids)]}}
        if self.create_project == 'e_s':
            project_ids = []
            for project in self.env['dzc2.project.request'].search([('type_of_project', '=', 'service')]):
                project_ids.append(project.id)
            return {'domain':{'project_created':[('id', 'in', project_ids)]}}
        if self.create_project == 'c_i':
            project_ids = []
            project = self.env['dzc2.project.request'].search([('type_of_project', '=', 'individual_production'),('individual_partner.faqeer_id.id','=',self.faqeer_id.id)])
            if project:
                project_ids.append(project.id)
                return {'domain':{'project_created':[('id', 'in', project_ids)]}}
            else:
                raise exceptions.ValidationError(_('Sorry ! this fageer has no previous project'))

    project_created = fields.Many2one('dzc2.project.request',string="The Project")


    # @api.multi
    # @api.constrains('create_project')
    # def complete_cons(self):
    #     if self.create_project == 'c_i':
    #         project = self.env['dzc2.project.request'].search([('type_of_project', '=', 'service'),('individual_partner','=',self.id)])
    #         if project:
    #             project_ids.append(project.id)
    #             return {'domain':{'project_created':[('id', 'in', project_ids)]}}
    #         else:
    #             raise exceptions.ValidationError(_('Sorry ! this fageer has no previous project'))

    @api.multi
    def action_done(self):
        """
        Change State To Done
        :return:
        """
        super(ApplicationForm,self).action_done()
        self._cr.execute('''
        select * from collective_fageer_tb
        where f_id = ''' + str(self.id))
        res = self._cr.fetchall()
        self._cr.execute('''
        select * from service_fageer_tb
        where fageer_id = ''' + str(self.id))
        ress = self._cr.fetchall()
        if self.case_type == 'project':
            # create urgent and emergency cases
            if self.create_project == 'e_c':
                if len(res) == 0:
                    self._cr.execute('''
                                        insert into collective_fageer_tb values(%s,%s)
                                    ''', [self.project_created.id,self.id])
                else:
                    raise ValidationError(_("this fageer is already added to this project"))
            elif self.create_project == 'e_s':
                if len(ress) == 0:
                    self._cr.execute('''
                                        insert into service_fageer_tb values(%s,%s)
                                    ''', [self.project_created.id,self.id])
                else:
                    raise ValidationError(_("this fageer is already added to this project"))
            elif self.create_project == 'n_c':
                the_id = self.env['dzc2.project.request'].create({
                    'collective_partner':[tuple(self)],
                    'type_of_project':'collective_production',
                })
                self._cr.execute('''
                                        insert into collective_fageer_tb values(%s,%s)
                                    ''', [the_id.id,self.id])
            elif self.create_project == 'n_s':
                the_id = self.env['dzc2.project.request'].create({
                    'service_partner':[tuple(self)],
                    'type_of_project':'service',
                })   
                self._cr.execute('''
                                        insert into service_fageer_tb values(%s,%s)
                                    ''', [the_id.id,self.id])                
            elif self.create_project == 'n_i':
                self.env['dzc2.project.request'].create({
                    'individual_partner':self.id,
                    'type_of_project':'individual_production',
                })

            elif self.create_project == 'c_i':
                self.env['dzc2.project.request'].create({
                    'individual_partner':self.id,
                    'type_of_project':'individual_production',
                    'is_complete_project' : True,
                })
            else:
                raise ValidationError(_("some text of the exception"))
        self.write({'state': 'done'})

class RequestProducsLines(models.Model):
    _name = 'request.p.products'
    product_id = fields.Many2one('product.product','Product')
    request_id = fields.Many2one('dzc2.project.request' , ' ')
    product_qty = fields.Integer(string='Quantity')
    @api.constrains('product_qty')
    def qty_check(self):
        if self.product_qty <= 0:
            raise ValidationError(_('Product Quantity must be grater than zero'))
class RequestsProducsLines(models.Model):
    _name = 'request.e.products'
    product_id = fields.Many2one('product.product','Product')
    request_id = fields.Many2one('dzc2.project.request' , ' ')
    product_qty = fields.Integer(string='Quantity')
    @api.constrains('product_qty')
    def qty_check(self):
        if self.product_qty <= 0:
            raise ValidationError(_('Product Quantity must be grater than zero'))

