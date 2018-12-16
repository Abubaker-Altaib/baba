# -*- coding: utf-8 -*-
# Copyright 2018, AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, exceptions, _
import re
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from datetime import date


class dzc_1Channel(models.Model):
    _name = 'zakat.dzc1'


# this is the hospital support root
class HospitalRoof(models.Model):
    _name = "hospital.ceiling"
    _order = 'create_date desc'

    name = fields.Char(string="Name", required=True)
    start_date = fields.Date(string="Start Date", default=datetime.now())
    end_date = fields.Date(string="End Date", default=lambda self: self.set_end_date())
    hospital_sub_choice_ids = fields.One2many(
        'hospital.ceiling.subclass',
        'hospital_ceiling_id',
        string='Hospital',
    )
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], string="Status", default='draft')
    company_id = fields.Many2one("res.company", default=lambda self: self.env.user.company_id, string="Company",
                                 ondelete='cascade')
    @api.multi
    def copy(self, default=None):
        """
        Prevent duplicate
        :raise: exceptions
        """
        raise exceptions.ValidationError(_("Record Could not Be Duplicated"))

    @api.constrains('name')
    def check_name(self):
        if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.name.replace(" ","")):
            raise ValidationError(_('name Field must be Literal'))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("name must not be spaces"))
        if self.name and self.search([('id','!=',self.id),('name','=',self.name)]):
            raise exceptions.ValidationError(_("name must not be duplicated"))

    def start_state(self):
        self.write({'state': 'confirmed'})

    @api.multi
    def action_draft(self):
        """
        Set State To Draft
        :return: change state to draft
        """
        self.write({'state': 'draft'})

    def get_date(self,str):
        return datetime.strptime(str, "%Y-%m-%d")

    def daterange(self, date1, date2):
        dates = []
        for n in range(int ((date2 - date1).days)+1):
            temp = date1 + timedelta(n)
            dates.append( str(temp.year)+str(temp.month)+str(temp.day) )
        return dates

    def check_date_duration(self, start_date, end_date, ceiling):
        start_date = self.get_date(start_date)
        end_date = self.get_date(end_date)
        main_range = list(self.daterange(start_date, end_date))

        for rec in ceiling:
            temp_start_date = self.get_date(rec.start_date)
            temp_end_date = self.get_date(rec.end_date)
            temp_range = list(self.daterange(temp_start_date, temp_end_date))

            if start_date == temp_start_date or start_date == temp_end_date:
                return False
            if end_date == temp_start_date or end_date == temp_end_date:
                return False
            if bool(set(main_range) & set(temp_range)):
                return False
        return True
            
        
    @api.model
    def create(self, vals):
        """
        Check IF Thier other ceiling overlaps with other one ceiling
        :param vals:
        :return:
        """
        ceiling = self.env['hospital.ceiling'].search([])
        
        if not self.check_date_duration(vals['start_date'], vals['end_date'], ceiling):
            raise exceptions.ValidationError(_("You Have Other Ceiling Overlaps With The Current Ceiling"))
        if 'hospital_sub_choice_ids' not in vals:
            raise ValidationError(_("At least one Treatment Unit should be added"))
        return super(HospitalRoof, self).create(vals)
    
    @api.multi
    def write(self, vals):
        re = super(HospitalRoof, self).write(vals)
        self.check_details()
        return re

    @api.constrains('hospital_sub_choice_ids')
    def check_details(self):
        for rec in self:
            if not rec.hospital_sub_choice_ids:
                raise ValidationError(_("At least one Treatment Unit should be added"))

    @api.constrains('start_date', 'end_date')
    def compare_date(self):
        for rec in self:
            ceiling = self.env['hospital.ceiling'].search([('id','!=',rec.id)])
            if not self.check_date_duration(rec.start_date, rec.end_date, ceiling):
                raise exceptions.ValidationError(_("You Have Other Ceiling Overlaps With The Current Ceiling"))
            if rec.start_date < rec.end_date:
                return True
            if rec.start_date >= rec.end_date:
                raise ValidationError(_("Start Date must Be Before the End Date"))
            

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_("You Can\'t Delete None Drafted Record"))
            # if rec.hospital_sub_choice_ids:
            #     raise ValidationError(_("You Can\'t Delete with details"))
            else:
                return super(HospitalRoof, self).unlink()

    @api.onchange('start_date')
    def set_end_date(self):
        if self.start_date:
            self.end_date = (datetime.strptime(self.start_date, '%Y-%m-%d') + relativedelta(months=1))


class HospitalCeilingSubClass(models.Model):
    _name = "hospital.ceiling.subclass"
    _order = 'create_date desc'

    hospital_id = fields.Many2one('hospital.treatment', string='Hospital', ondelete="restrict")
    exceed_the_ceiling = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Allowed To Exceede The Ceiling?',
                                          default='no')
    overpass_ceiling = fields.Float(string="Overpass Ceiling")
    specified_monthly_amount = fields.Float(string="Specified Monthly Amount")
    monthly_amount = fields.Float(string="Monthly Amount", compute='_get_amount')
    taken_amount = fields.Float(string="Taken Amount")
    remaining_amount = fields.Float(string="Remaining Amount", compute='remaining_amount_compute', store=True)
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], string="Status", default='draft')
    hospital_ceiling_id = fields.Many2one('hospital.ceiling', ondelete="restrict")

    @api.depends('monthly_amount', 'taken_amount')
    def remaining_amount_compute(self):
        for record in self:
            if record.monthly_amount:
                if record.exceed_the_ceiling == 'yes':
                    tt = (record.monthly_amount + record.overpass_ceiling) - record.taken_amount
                if record.exceed_the_ceiling == 'no':
                    tt = record.monthly_amount - record.taken_amount
                if tt < 0:
                    raise ValidationError(_('Negative number is not Allowed in Monthly Amount'))
                else:
                    record.remaining_amount = tt
        return True

    @api.depends('specified_monthly_amount')
    def _get_amount(self):
        for record in self:
            if record.specified_monthly_amount:
                tt = record.specified_monthly_amount
                record.monthly_amount = tt
        return True

    @api.multi
    @api.constrains('specified_monthly_amount', 'overpass_ceiling', 'monthly_amount', 'taken_amount',
                    'remaining_amount')
    def _positive(self):
        for record in self:
            if record.specified_monthly_amount <= 0:
                raise ValidationError(_('Zero Negative numbers are not allowed'))
            if record.overpass_ceiling < 0:
                raise ValidationError(_('Negative numbers are not allowed'))
            if record.monthly_amount < 0:
                raise ValidationError(_('Negative numbers are not allowed'))
            if record.taken_amount < 0:
                raise ValidationError(_('Negative numbers are not allowed'))
            if record.remaining_amount < 0:
                raise ValidationError(_('Negative numbers are not allowed'))
        return True

    @api.constrains('overpass_ceiling', 'exceed_the_ceiling')
    def _required_ceiling(self):
        for record in self:
            if record.exceed_the_ceiling == 'yes':
                if record.overpass_ceiling <= 0:
                    raise ValidationError(_('Overpass Ceiling is Required and Cannot be Zero or Negative.'))


class ZakatApplicationForm(models.Model):
    _name = "zakat.aplication.form"
    _order = 'create_date desc'

    # 
    # this is the basic personal information
    # 
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        show only illness that is not selected
        :return: list of ids
        """
        if self._context.get('fageer_ids', []):
            illness_id = self.env['orphan.registration.order'].resolve_2many_commands('fageer_ids',
                                                                                      self._context.get('fageer_ids',
                                                                                                        []))
            args.append(('id', 'not in',
                         [isinstance(d['name'], tuple) and d['name'][0] or d['name']
                          for d in illness_id]))
        if self._context.get('beneficiaries_ids', []):
            illness_id = self.env['health.insurance.order'].resolve_2many_commands('beneficiaries_ids',
                            self._context.get('beneficiaries_ids',[]))
            args.append(('id', 'not in',
                         [isinstance(d['fageer_id'], tuple) and d['fageer_id'][0] or d['fageer_id']
                          for d in illness_id]))

        if self._context.get('new_beneficiaries_ids', []):
            illness_id = self.env['health.insurance.order'].resolve_2many_commands('beneficiaries_ids',
                            self._context.get('new_beneficiaries_ids',[]))
            args.append(('id', 'not in',
                         [isinstance(d['fageer_new_id'], tuple) and d['fageer_new_id'][0] or d['fageer_new_id']
                          for d in illness_id]))
            
        if self._context.get('f_ids', []):
            faqeers = self.env['social.support.registration.order'].resolve_2many_commands('fageer_ids',self._context.get('f_ids',[]))
            args.append(('id', 'not in',
                    [isinstance(d['fageer_new_id'], tuple) and d['fageer_new_id'][0] or d['fageer_new_id']
                    for d in faqeers]))
        if self._context.get('old_ids', []):
            faqeers = self.env['social.support.registration.order'].resolve_2many_commands('fageer_ids',self._context.get('old_ids',[]))
            args.append(('id', 'not in',
                    [isinstance(d['fageer_old_id'], tuple) and d['fageer_old_id'][0] or d['fageer_old_id']
                    for d in faqeers]))

        return super(ZakatApplicationForm, self).name_search(name, args=args, operator=operator, limit=limit)

    faqeer_id = fields.Many2one('res.partner', string="Faqeer")
    case_study = fields.Boolean("Case Study")
    name = fields.Char(string="Name", related='faqeer_id.name')
    national_number = fields.Char(string='National Number', related='faqeer_id.national_number')
    phone = fields.Char(string="Phone Number", related='faqeer_id.phone')
    gender = fields.Selection(string='Gender', related='faqeer_id.gender')
    father_alive = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Is The Father Alive?')
    mother_alive = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Is The Mother Alive?')
    birth_date = fields.Date(string="Birth Day", related='faqeer_id.birth_date')
    health_status = fields.Selection([('healthy', 'Healthy'), ('disabled', 'Disabled'), ('sick', 'Sick')],
                                     'Health Status')
    illness_type = fields.Selection([('chronic', 'Chronic'), ('severe', 'Severe'), ('accidental', 'Accidental')],
                                    'Type Of Illness')
    disability_status = fields.Selection([('mental', 'Mental Disability'), ('hearing', 'Hearing Disability'),
                                          ('visual', 'Visual Disability'), ('mobility', 'Mobility Disability')],
                                         'Type Of Disability')
    social_status = fields.Selection([('single', 'Single'), ('married', 'Married'),
                                      ('divorced', 'Divorced'), ('widowed', 'Widowed'), ('leave', 'Leave/Separated')],
                                     'Social Status')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('approval', 'Approved'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel')], string="Status", default='draft')
    # this ist he case type
    case_type = fields.Selection([('project','Project'),('garm','Garm'),('urgent','Fageer')])
    create_project = fields.Selection([('n_i','New Individual productive Project'),('c_i','Complete individual productive project'),('n_c','Create a Productive Collective project'),('e_c','Add to productive Collective project')
    ,('n_s','Create a Service Project'),('e_s','Add to Service Project')])
    # 
    # this is the Sakan information
    # 
    old_en = fields.Boolean(default=False)
    state_id = fields.Many2one(string='State', related='faqeer_id.zakat_state')
    sector = fields.Many2one(string='Sector', related='faqeer_id.sectors')
    local_state_id = fields.Many2one(string='Local State', related='faqeer_id.local_state_id')
    admin_unit_id = fields.Many2one(string='Administrative Unit', related='faqeer_id.admin_unit')
    city = fields.Char(string='City', related='faqeer_id.city')
    village = fields.Char(string='Village', related='faqeer_id.Village')
    house_number = fields.Char(string='House Number', related='faqeer_id.house_no')
    housing_ownership = fields.Selection([('owned', 'Owned'), ('rent', 'Rent'),
                                          ('inherited', 'Inherited'), ('gift', 'Gift'), ('possession', 'Possession'),
                                          ('mobile', 'Mobile'), ('government', 'Government'), ('hosting', 'Hosting'),
                                          ('family', 'With Family'), ], 'Type Of House Ownership')
    house_type = fields.Selection([('tent', 'Tent'), ('berish', 'Berish'), ('quttya', 'Quttya'),
                                   ('wood', 'Wood'), ('bricks', 'Bricks'), ('others', 'Others/Specify')],
                                  'Type Of House')
    other_house = fields.Char(string='Other Type Of House')
    type_toilet = fields.Selection([('gardl', 'Gardl'), ('local', 'Local'), ('siphon', 'Siphon'),
                                    ('absorber', 'Absorber'), ('normal', 'Normal Toilet'), ('no', 'Don\'t Have'),
                                    ('others', 'Others/Specify')], 'Type Of Toilet')
    other_toilet = fields.Char(string='Other Toilet')
    cooking_fule = fields.Selection([('wood', 'Wood'), ('grass', 'Grass'),
                                     ('coal', 'Coal'), ('gas', 'Gas'),
                                     ('electricity', 'Electricity'), ('others', 'Others/Specify')],
                                    'Type Of Cooking Fule')
    other_fule = fields.Char(string='Other Fule')
    # 
    # this is the educational information
    # 
    educational_status = fields.Selection([('illiterate', 'Illiterate'), ('sanctum', 'Sanctum'),
                                           ('kindergarten', 'Kindergarten'), ('primary', 'Primary'),
                                           ('secondary', 'Secondary'),
                                           ('university', 'University'), ('postgraduate', 'Postgraduate Studies'), ],
                                          'Educational Status')
    # 
    # this is the job information
    # 
    job = fields.Char(string='Job', related='faqeer_id.job',store=True)
    job_type =  fields.Selection(string='Gender', related='faqeer_id.job_type', store=True)
    other_job = fields.Char(string='Other Job')
    # 
    # this is the committee desision
    # 
    committee_des = fields.Selection([('support', 'Support'), ('apology', 'Apology'),
                                      ('transfer', 'Transfer'), ('return', 'The Request Returns')],
                                     'Committee Decision')
    transfer_entity = fields.Char(string='Transfer Entity')
    reason_apology = fields.Text(string='Reason Of The Apology')
    support_type = fields.Selection([('cash', 'Cash Support'), ('corporeal', 'Corporeal Support')], 'Type Of Support')
    corporeal_type = fields.Char(string='Corporeal Type')
    corporeal_quantity = fields.Integer(string='Quantity')
    cash_support_type = fields.Selection(
        [('cash', 'Cash Support'), ('check', 'Check'), ('account_number', 'Acount Number')], 'Type Of Cash Support')
    cash_amount = fields.Integer(string='Cash Amount')
    # 
    # this is the recommendation
    # 
    committee_recom = fields.Text(string='Committee Recommendation')
    disbursement_manager_recom = fields.Text(string='Disbursement Manager Recommendation')
    disbursement_committee_decision = fields.Text(string='Disbursement Committee Decision')
    # 
    # this is the family part
    # 
    family_ids = fields.One2many('zakat.family', 'fageer_id', string='Family',ondelete="restrict")
    # 
    # this is the family sponsorship
    # 
    family_sponsor = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Does The Family Have Sponsorship?')
    sponsor_type = fields.Selection([('health', 'Health Insurance'),
                                     ('old', 'Aged And Elderly'), ('student', 'Student Sponsorship'),
                                     ('orphan', 'Orphan Sponsorship'),
                                     ('social', 'Social Support'), ('project', 'Project'), ], 'Sponsorship Type')
    insurance_type = fields.Selection([('zakat', 'Zakat Insurance'),
                                       ('finance', 'Financial Insurance'), ('government', 'Government Insurance'),
                                       ('special', 'Special Insurance'), ], 'Insurance Type')
    # 
    # this is the student sponsorship part
    # 
    student_ids = fields.One2many('zakat.student.grantee', 'fageer_id', string='Students')
    # 
    # this is the orphan sponsorship part
    # 
    sponsor_cash_amount = fields.Integer(string='Sponsor Amount')
    orphan_sponsor_type = fields.Selection([('dewan', 'ALdewan'),
                                            ('organization', 'Organizations'), ('others', 'Others/Specify')],
                                           'Orphan Sponsorship Type')
    orphan_specify = fields.Char(string='Specify The Type')
    #
    #  this is the company information
    #
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    s_support = fields.Boolean(string="Social Support" , default=False)
    i_health = fields.Boolean(string="Insurance Health", default=False)
    student = fields.Boolean(string="Student", default=False)
    orphan = fields.Boolean(string="Orphan", default=False)
    status = fields.Selection([('i_m', 'Imam & Muezzin'),
                               ('sheikh', 'Sheikh'),
                               ('deaf', 'Deaf'),
                               ('blind', 'Blind'),
                               ('di_physically', 'disabled Physically'),
                               ('m_h', 'Mentally Handicapped')], default="i_m", string="Status")
    basal_drainage = fields.Boolean(string="Basal Drainage", default=False)
    social_amount = fields.Float(string="Social Support Amount")
    case_study_purpose = fields.Selection([('create_u_e_request','Create Urgent and Emergency Case Request') , ('add_to_fogara','Add To Fogara List')])

    # 7 , 8 , 9 , 13 , 14
    
    last_payment_date = fields.Date()
    monthly_support_amount = fields.Float()
    monthly_support = fields.Boolean()
    monthly_support_payment = fields.Many2one('zakat.monthly.support')
    monthly_income = fields.Float("Monthly Income")
    monthly_expenses = fields.Float("Monthly Expenses")
    family_left_education = fields.Selection([('yes','Yes'),('no','No'),('dont_have','Don\'t have Kids')]
    ,"Do You Have Kids That Left The School?")
    reason = fields.Selection([('unwillingness','The Unwillingness Of Children'),('fam_conditions','Family Conditions'),('culture','Cultural Reasons'),
    ('inability','The Inability To Provide For Their Education Requirements')])
    type_of_case_study = fields.Selection([('faqeer','Faqeer'),('project','Project')],"Type")
    project = fields.Boolean()
    # guarantee_id = fields.Many2one('zakat.guarantee.order')
    # end of data
    # 
    # this is the validation part

    # _sql_constraints = [
    #     ('unique_fageer_type', 'unique (faqeer_id,case_type)',
    #      'This Faqeer Have A Case Study From The Same Type!')
    # ]

    @api.multi
    @api.constrains('faqeer_id','case_type')
    def _unique_faqeer(self):
        if self.create_project != 'c_i':
            faq = self.env['zakat.aplication.form'].search(['&',('faqeer_id','=',self.faqeer_id.id),('case_type','=',self.case_type),('id','!=',self.id)])
            if len(faq) > 0:
                raise ValidationError(_("This Faqeer Have A Case Study From The Same Type!"))
        return True

    def print_report(self):
        """
        pass the data i need to get the report
        :return: report action
        """
        data = self.id
        datas = {
            'ids': [],
            'model': 'zakat.aplication.form',
            'dzc1': data,

        }
        return self.env.ref('dzc_1.certificate_of_entitlement_action').report_action(self, data=datas)


    @api.multi
    def action_confirm(self):
        """
        Change State To Confirmed
        :return:
        """
        self.write({'state': 'confirmed'})

    @api.multi
    def action_approve(self):
        """
        Change State To Approved
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
    def action_set_draft(self):
        """
        Set State To Draft
        :return:
        """
        self.write({'case_study':False})
        self.write({'state': 'draft'})

    @api.multi
    def action_done(self):
        """
        Change State To Done
        :return:
        """
        self.write({'case_study':True})
        if self.case_type == 'urgent' and self.case_study_purpose == 'create_u_e_request':
            # create urgent and emergency cases
            self.env['emergency.and.urgent.cases'].create({
                'partnrt_id':self.id,
            })
        if self.case_type == 'garm':
            # create urgent and emergency cases
            self.env['dzc_6.garm.request'].create({
                'faqeer_id':self.id,
            })
        self.write({'state': 'done'})
        self.old_en = True

    @api.constrains('birth_date')
    def check_date(self):
        """
        To check date fields
        :return: raise exceptions
        """
        birth_date = datetime.strptime(self.birth_date, '%Y-%m-%d')
        now = datetime.now()
        # if self.date_of_arrival < self.date:
        #     raise exceptions.ValidationError(_("Date Of Arrivals Must Be With In The Current Date"))
        if birth_date.year >= now.year:
            raise exceptions.ValidationError(_('Birth Date Must Be Less Than Current Date'))

    @api.constrains('phone', 'national_number', 'house_number')
    def checks(self):
        """
        Desc:Check format Phones and ID Numbers
        :return:
        """
        # Regex pattern to check all chars are integers
        pattern = re.compile(r'^[0]\d{9,9}$')
        if self.phone != False:
            if not pattern.search(str(self.phone)):
                raise exceptions.ValidationError(_('Phone 1 must be exactly 10 Numbers and Start with ZERO 0 .'))
        if self.national_number != False:
            if 11 < len(self.national_number) or 11 > len(self.national_number):
                raise exceptions.ValidationError(_('ID Number must be at least 11 Numbers.'))
        if self.house_number <= 0:
            raise exceptions.ValidationError(_("House Number Must Be Greater Than Zero"))

    # @api.constrains('name')
    # def name_constrains(self):
    #     for char in self.name:
    #         if not char.isalpha() and char != ' ':
    #             raise exceptions.ValidationError(_("None Valid Name"))  
    #     return True
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_("You Can\'t Delete None Drafted Record"))
            else:
                return super(ZakatApplicationForm, self).unlink()



class PoorFamily(models.Model):
    _name = 'zakat.family'
    _order = 'create_date desc'

    _sql_constraints = [
        ('unique_nnational_number', 'unique(national_number)', _("This National Number is Exists"))
    ]

    name = fields.Char(string='Full Name', required=True)
    job_type = fields.Selection([('public', 'Public Sector'), ('private', 'Private Sector'),
                                 ('free', 'Free Businees'), ('vocational', 'Vocational'), ('handicraft', 'Handicraft'),
                                 ('farmer', 'farmer'),
                                 ('student', 'Student'), ('pension', 'Pension'), ('daily', 'Daily Business'),
                                 ('tradesman', 'Tradesman'), ('non', 'Non-Working')], 'Job')
    educational_status = fields.Selection([('illiterate', 'Illiterate'), ('sanctum', 'Sanctum'),
                                           ('kindergarten', 'Kindergarten'), ('primary', 'Primary'),
                                           ('secondary', 'Secondary'),
                                           ('university', 'University'), ('postgraduate', 'Postgraduate Studies'), ],
                                          'Educational Status')
    relation = fields.Selection(
        [('father', 'Father'), ('mother', 'Mother'), ('son', 'Son'), ('brother', 'Brother/sister')],
        string="Relative Relation", )
    health_status = fields.Selection([('healthy', 'Healthy'), ('disabled', 'Disabled'), ('sick', 'Sick')],
                                     'Health Status')
    age = fields.Integer(string='Age')
    is_orphan = fields.Boolean("Is Orphan")
    national_number = fields.Char(string="National Number", track_visibility='onchange')

    fageer_id = fields.Many2one('zakat.aplication.form',ondelete="restrict")
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user.id,
                              ondelete='restrict')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,)

    no_of_individual = fields.Integer(string="No. individual", store=True)

    @api.model
    def create(self,vals):
        fageer = vals['fageer_id']
        count = 0
        fagger = []
        data = self.env['zakat.family'].search([('fageer_id','=', fageer )])
        if data:
            i = data[-1].no_of_individual
            for rec in data:
                vals['no_of_individual'] = i + 1

        if not data :
            fagger = self.env['zakat.aplication.form'].search([('id','=',fageer)])
            for r in fagger:
                count = count + 1
                vals['no_of_individual'] = count

        return super(PoorFamily, self).create(vals)

    

    @api.constrains('name')
    def check_name(self):
        if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.name.replace(" ","")):
            raise ValidationError(_('name Field must be Literal'))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("name must not be spaces"))
        if self.name and self.search([('id','!=',self.id),('name','=',self.name)]):
            raise exceptions.ValidationError(_("name must not be duplicated"))
    
    @api.constrains('national_number','age')
    def check_national_number(self):
        if self.national_number != False:
                    if not re.match("^[0-9]*$", self.national_number.replace(" ", "")):
                        raise ValidationError(_('National Number Field must be number'))
                    if self.national_number.replace(" ", "") != self.national_number:
                        raise ValidationError(_('National Number Field must be number'))
                    if 11 < len(self.national_number) or 11 > len(self.national_number):
                        raise exceptions.ValidationError(_('ID Number must be at least 11 Numbers.'))
        values = self.env['zakat.family'].search([('national_number', '=', self.national_number),('id','!=',self.id)])
        for value in values:
            if len(value) > 0:
                message = "This National Number is assigned for " + value.name + " and he is the " + value.relation + " of " + value.fageer_id.faqeer_id.name
                raise exceptions.ValidationError(_(message))
        if self.age != False:
            if self.age < 0 or self.age >=120 :
                raise exceptions.ValidationError(_("The Age is not appropreat"))


class StudentGrantee(models.Model):
    _name = 'zakat.student.grantee'

    # @api.model
    # def get_student(self):
    #     """
    #     Domain To return only Student and with the same fageer
    #     :return:
    #     """
    #     print(">>>>>>>>>>>>>>>>>>>>>>>>>>>> ??-->>", self._context)
    #     if self._context.get('id', []):
    #         print(">>>>>>>>>>>>>>>>>>>>>>>> We are Good")
    #     return [('id', '=', 1)]

    family_id = fields.Many2one('zakat.family', string='Family')
    fageer_id = fields.Many2one('zakat.aplication.form')
    name = fields.Char(string='Full Name', related="")
    national_number = fields.Char(string="National Number", track_visibility='onchange')
    card_no = fields.Char(string="Card ID", track_visibility='onchange')
    card_extraction = fields.Date(string='Date Of Extraction')
    card_expiration = fields.Date(string='Date Of Expiration')
    educational_year = fields.Date(string='Educational Year')
    collage = fields.Char(string='Collage')
    university = fields.Char(string='University')

    @api.constrains('card_no')
    def checks(self):
        """
        Desc:Check format card_id and ID Numbers
        :return:
        """
        # Regex pattern to check all chars are integers
        if not re.match("^[0-9]*$", self.card_no.replace(" ", "")):
            raise ValidationError(_('Card No Field must be number'))
        if self.card_no.replace(" ", "") != self.card_no:
            raise ValidationError(_('Card No Field must be number'))

    @api.constrains('card_extraction')
    def check_date(self):
        """
        To check date fields
        :return: raise exceptions
        """
        card_extraction = datetime.strptime(self.extract_date, '%Y-%m-%d')
        now = datetime.now()
        if card_extraction.year >= now.year:
            raise exceptions.ValidationError(_('Card extraction date must be less than current date'))


class StudentSponsorship(models.Model):
    _name = 'zakat.student.sponsorship'
    _order = 'create_date desc'

    name = fields.Char(string='Full Name', required=True)
    national_number = fields.Char(string="National Number", track_visibility='onchange')
    card_id = fields.Char(string="Card ID", track_visibility='onchange')
    extract_date = fields.Date(string='Date Of Extraction')
    expire_date = fields.Date(string='Date Of Expiration')
    collage = fields.Char(string='Collage')
    university = fields.Char(string='University')
    study_years = fields.Selection([(num, str(num)) for num in range(1900, (datetime.now().year) + 1)], 'Study Year')
    fageer_id = fields.Many2one('zakat.aplication.form')
    family_ids = fields.One2many('zakat.family', 'fageer_id', string='Family')

    _sql_constraints = [
        ('number_uniq', 'unique (national_number)',
         'The National Number Is Exist !')
    ]



class GuaranteesOrder(models.Model):
    _name = 'zakat.guarantee.order'
    _description = "Guarantee Order"
    _order = "create_date desc"

    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user, ondelete='restrict')
    name = fields.Char(string="Order Number", default="/", readonly='True')
    order_date = fields.Date(string="Order Date", default=datetime.today())
    # guarantees_conf_id = fields.Many2one('zakat.guarantees')
    type = fields.Selection([('s_support', 'Social Support'),
                             ('i_health', 'Insurance Health'),
                             ('student', 'Student'),
                             ('orphan', 'Orphan')], default='s_support')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('approve', 'Approved'),
                              ('done', 'Done'),
                              ('cancel', 'Canceled')], string="Status", default='draft')
    description = fields.Char(string="Description")


class InsuranceHealth(models.Model):
    _name = 'zakat.insurance.health'
    _inherits = {'zakat.guarantee.order': 'order_id'}
    _order = "create_date desc"
    _description = 'Insurance Health Guarantee Order'

    order_id = fields.Many2one('zakat.guarantee.order', ondelete='cascade')
    partner_id = fields.Many2one('res.partner')
    ref = fields.Char(string="Reference")
    amount = fields.Float(string="Amount", compute="get_info")
    no_active_card = fields.Char(compute="get_info")
    insurance_ids = fields.One2many('zakat.insurance.lines', 'insurance_order')
    voucher_id = fields.Many2one('account.voucher', ondelete="restrict")
    state_id = fields.Many2one('zakat.state')

    @api.multi
    def unlink(self):
        """
        prevent Record Remove if it not in draft state
        :return:
        """
        for record in self:
            if record.state != 'draft':
                raise exceptions.ValidationError(_("You Cannot Remove Record If it not in Dratf State"))
            elif record.state == 'draft':
                self.order_id.unlink()
                return super(InsuranceHealth, self).unlink()

    @api.multi
    def action_confirm(self):
        """
        change state To Confirm
        :return:
        """
        self.write({'state': 'confirm'})

    @api.multi
    def action_approve(self):
        """
        change state To Approve
        :return:
        """
        if not self.insurance_ids:
            raise exceptions.ValidationError(_("Please Make Sure You Have Insurance Guaranteed"))
        self.write({'state': 'approve'})

    @api.multi
    def action_done(self):
        """
        change state To Done
        :return:
        """
        line = []
        guarantees = self.env['zakat.guarantees'].search([('company_id', '=', self.env.user.company_id.id),
                                                          ('type', '=', self.type)])
        line += [(0, 6, {
            'name': _('Health Insurance'),
            'account_id': guarantees.property_account_id.id,
            'account_analytic_id': guarantees.property_analytic_account_id.id,
            'quantity': 1,
            'price_unit': self.amount,
        })]

        voucher_id = self.env['account.voucher'].create(
            {
                'name': '',
                'partner_id': self.partner_id.id,
                'journal_id': guarantees.journal_id.id,
                'pay_now': 'pay_later',
                'reference': _('Health Insurance Payment'),
                'voucher_type': 'purchase',
                'company_id': self.env.user.company_id.id,
                'line_ids': line,

            })
        self.voucher_id = voucher_id.id
        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        """
        change state To Confirm
        :return:
        """
        self.write({'state': 'cancel'})

    @api.multi
    def action_draft(self):
        """
        change state To Confirm
        :return:
        """
        self.write({'state': 'draft'})

    @api.model
    def get_seq_to_view(self):
        """
        Get sequence in code filed in form view
        :return:
        """
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, vals):
        """
        create sequence
        :param vals: fields values from view
        :return: dict
        """
        # set new sequence number in code for every new record
        vals['name'] = self.env['ir.sequence'].get(self._name) or '/'
        return super(InsuranceHealth, self).create(vals)

    @api.one
    @api.depends('insurance_ids')
    def get_info(self):
        """
        To Get The Number of Social Supported Number and The Total Amount
        :return:
        """
        total = 0
        count = 0
        for record in self.insurance_ids:
            count += 1
            total += record.insurance_amount
        self.amount = total
        self.no_active_card = count

    @api.multi
    def get_data(self):
        """
        To get Data From Al-faqir Model who have Health Insurance
        :return:
        """
        amount = 0
        if self.type == 'i_health':
            guarantees = self.env['zakat.guarantees'].search([('company_id', '=', self.env.user.company_id.id),
                                                              ('type', '=', self.type)])
            if not guarantees:
                raise exceptions.ValidationError(_("You Must have Health Insurance Guarantess in Configuration!!"))
            amount = guarantees.amount
            data = self.env['zakat.aplication.form'].search([('company_id', '=', self.env.user.company_id.id), ('i_health', '=', True), ('insurance_end_date', '>', self.order_date)])
            if not data:
                raise exceptions.ValidationError(_("There is no Data"))
            for faqir in data:
                self.insurance_ids.create({
                    'guaranteed_id': faqir.id,
                    'insurance_amount': amount,
                    'insurance_order': self.id
                })


class InsuranceLines(models.Model):
    _name = 'zakat.insurance.lines'
    _order = 'create_date desc'

    insurance_amount = fields.Float()
    guaranteed_id = fields.Many2one('zakat.aplication.form')
    i_enddate = fields.Date(related="guaranteed_id.insurance_end_date")
    insurance_order = fields.Many2one('zakat.insurance.health', ondelete='cascade')

    _sql_constraints = [('uniq_guaranteed_insurance_order', 'unique(guaranteed_id,insurance_order)',
                         _("Guarantee Cannot Be Given To the Same Person Twice !"))]


class SocialSupportGuarantess(models.Model):
    _name = 'zakat.social.support'
    _inherits = {'zakat.guarantee.order': 'order_id'}
    _order = "create_date desc"
    _description = 'Social Support Guarantee Order'

    order_id = fields.Many2one('zakat.guarantee.order', ondelete='cascade')
    name = fields.Char(string='Order Number')
    # name = fields.Char(string='Order Number', default=lambda self: self.get_seq_to_view())
    guaranteed_ids = fields.One2many('zakat.social.lines', 'social_order')
    social_lines = fields.Integer(string="No Of Social", compute='get_info')
    amount = fields.Float(string="Amount", compute='get_info')

    @api.multi
    def unlink(self):
        """
        prevent Record Remove if it not in draft state
        :return:
        """
        for record in self:
            if record.state != 'draft':
                raise exceptions.ValidationError(_("You Cannot Remove Record If it not in Dratf State"))
            elif record.state == 'draft':
                self.order_id.unlink()
                return super(SocialSupportGuarantess, self).unlink()

    @api.multi
    def action_confirm(self):
        """
        change state To Confirm
        :return:
        """
        self.write({'state': 'confirm'})

    @api.multi
    def action_approve(self):
        """
        change state To Approve
        :return:
        """
        self.write({'state': 'approve'})

    @api.multi
    def action_done(self):
        """
        change state To Done
        :return:
        """
        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        """
        change state To Confirm
        :return:
        """
        self.write({'state': 'cancel'})

    @api.multi
    def action_draft(self):
        """
        change state To Confirm
        :return:
        """
        self.write({'state': 'draft'})

    @api.model
    def get_seq_to_view(self):
        """
        Get sequence in code filed in form view
        :return:
        """
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, vals):
        """
        create sequence
        :param vals: fields values from view
        :return: dict
        """
        # set new sequence number in code for every new record
        vals['name'] = self.env['ir.sequence'].get(self._name) or '/'
        return super(SocialSupportGuarantess, self).create(vals)

    @api.one
    @api.depends('guaranteed_ids')
    def get_info(self):
        """
        To Get The Number of Social Supported Number and The Total Amount
        :return:
        """
        total = 0
        count = 0
        for record in self.guaranteed_ids:
            count += 1
            total +=record.salary
        self.amount = total
        self.social_lines = count


    @api.multi
    def get_data(self):
        """
        To get Data From Al-faqir Model who have social support
        :return:
        """

        amount = 0
        if self.type == 's_support':
            guarantees = self.env['zakat.guarantees'].search([('company_id', '=', self.env.user.company_id.id),
                                                              ('type', '=', self.type)])
            if not guarantees:
                raise exceptions.ValidationError(_("You Must have Social Support Guarantess in Configuration!!"))
            amount = guarantees.amount
            data = self.env['zakat.aplication.form'].search([('s_support', '=', True)])
            if not data:
                raise exceptions.ValidationError(_("There is no Data"))
            for faqir in data:
                self.guaranteed_ids.create({
                    'guaranteed_id': faqir.id,
                    'salary': amount,
                    'social_order': self.id
                })


class SocialSupportLines(models.Model):
    _name = 'zakat.social.lines'
    _order = 'create_date desc'

    guaranteed_id = fields.Many2one('zakat.aplication.form')
    social_order = fields.Many2one('zakat.social.support', ondelete='cascade')
    status = fields.Selection(related='guaranteed_id.status')
    salary = fields.Float(string="Salary")

    _sql_constraints = [('uniq_guaranteed_social_order', 'unique(guaranteed_id,social_order)',
                         _("Guarantee Cannot Be Given To the Same Person Twice !"))]


class EmergencyandUrgentCases(models.Model):
    _name = 'emergency.and.urgent.cases'
    _order = 'create_date desc'

    name = fields.Char(string='Ref')
    partnrt_id = fields.Many2one('zakat.aplication.form', 'Fageer')
    order_date = fields.Date(string="Order Date", default=datetime.today())
    state_id = fields.Many2one('zakat.state', 'State')
    local_state_id = fields.Many2one('zakat.local.state')
    case_type = fields.Selection([('emergency', 'Emergency'), ('urgent', 'Urgent')])
    case_classification = fields.Many2one('zakat.urgentemergencytype')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, ondelete='restrict')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirmed'), ('approve', 'Approved'), ('social_research', 'Social Research'),
         ('zakat_commitee', 'Zakat Commitee'), ('done', 'Done'), ('cancel', 'Canceled')], default='draft',
        string='Status')
    category = fields.Selection('Category',related='company_id.category')
    case_description = fields.Text(string='Case Description')
    masaref_manger_decision = fields.Text(string='Masaref Manger Decision')
    committe_date = fields.Date(string='Committe Date')
    decision = fields.Selection([('agree', 'Agree'), ('apology', 'Apology'),('monthly','Transfare to Monthly Support')])
    monthly_support = fields.Float()
    initial_amount = fields.Float()
    amount = fields.Float(string='Aproved Amount')
    committe_decision = fields.Text(string='Committe Decision')
    voucher_id = fields.Many2one(comodel_name='account.voucher',string='voucher')
    address_id = fields.Many2one('addresses','Address')


    def print_social_status(self):
        """
        pass the data i need to get the report
        :return: report action
        """
        data = self.id
        datas = {
            'ids': [],
            'model': 'emergency.and.urgent.cases',
            'emergency': data,

        }
        return self.env.ref('dzc_1.emergency_form_action').report_action(self, data=datas)

    _sql_constraints = [
        ('case_unique', 'unique (partnrt_id,committe_date)',
         'Sorry ! This Fageer is Already hade a case in this commitee')]

    @api.constrains('case_description','masaref_manger_decision','committe_decision','name')
    def string_validation(self):
        if self.case_description:
            if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.case_description.replace(" ","")):
                raise ValidationError(_('Case Description Can not begin with white space or special charector'))
            if self.case_description and (len(self.case_description.replace(' ', '')) <= 0):
                raise exceptions.ValidationError(_("Case Description Can not begin with white space or special charector"))
        if self.masaref_manger_decision:
            if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.masaref_manger_decision.replace(" ","")):
                raise ValidationError(_('Masaref Manager Decision Should contain just Charactors or numbers and can not begin with white Space or special charactor'))
            if self.masaref_manger_decision and (len(self.masaref_manger_decision.replace(' ', '')) <= 0):
                raise exceptions.ValidationError(_("Masaref Manager Decision Should contain just Charactors or numbers and can not begin with white Space or special charactor"))
        if self.committe_decision:
            if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.committe_decision.replace(" ","")):
                raise ValidationError(_('Committe Decision Field must be Literal'))
            if self.committe_decision and (len(self.committe_decision.replace(' ', '')) <= 0):
                raise exceptions.ValidationError(_("Committe Decision must not be spaces"))
        
    
    @api.constrains('committe_date')
    def validation(self):
        if self.case_type == 'urgent':
           if self.committe_date <= self.order_date:
              raise ValidationError(_('Committe Date MUST Be After Order Date'))
    
    @api.constrains('amount','monthly_support','initial_amount')
    def amam(self):
        if self.amount:
            if self.amount <= 0.0:
                raise ValidationError(_("Amount MUST be Greater Than Zero"))
        if self.monthly_support:
            if self.monthly_support <= 0.0:
                raise ValidationError(_("Monthly Support MUST be Greater Than Zero"))
        if self.initial_amount <= 0.0:
            raise ValidationError(_("Initial Amount MUST be Greater Than Zero"))
    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.sequence.number_next_actual

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('emergency.and.urgent.cases') or '/'
        return super(EmergencyandUrgentCases, self).create(vals)

    @api.multi
    def confirm(self):
        if not self.state_id and not self.local_state_id:
            raise exceptions.UserError(_('Sorry! You must Select at least One State or Local State '))
        else:
            self.write({'state': 'confirm'})

    @api.multi
    def approve(self):
        if self.case_type == 'emergency':
            payment_lines = []
            payment_lines += [(0, 6, {
                'name': self.name,
                'account_id': self.case_classification.property_account_id.id,
                'quantity': 1,
                'name': _('Emergency'),
                'price_unit': self.amount,
                'journal_id': self.case_classification.journal_id.id,
            })]
            voucher = self.env['account.voucher'].create(
                {
                    'name': self.name,
                    'journal_id': self.case_classification.journal_id.id,
                    'analytic_account_id':self.case_classification.property_analytic_account_id.id,
                    'company_id': self.company_id.id,
                    'amount': self.amount,
                    'pay_now': 'pay_later',
                    'reference': self.name,
                    'voucher_type': 'purchase',
                    'description': "Emergency",
                    'partner_id': self.partnrt_id.faqeer_id.id,
                    'line_ids': payment_lines
                })
            self.voucher_id = voucher.id
            self.write({'state': 'done'})
        else:
            self.write({'state': 'approve'})

    @api.multi
    def cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def draft(self):
        self.write({'state': 'draft'})

    def done(self):
        self.partnrt_id.write({
            'monthly_support':True,
            'monthly_support_amount':self.monthly_support,
        })
        self.write({'state': 'done'})
        self.partnrt_id.case_study = False

    @api.multi
    def social_research(self):
        if self.partnrt_id.state != 'done' or not self.partnrt_id.case_study:
            raise exceptions.Warning('Sorry you must Do Case Study For This Fageer')
        else:
            self.write({'state': 'social_research'})

    @api.multi
    def zakat_commitee(self):
        self.write({'state': 'zakat_commitee'})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state not in ('draft'):
                raise exceptions.UserError(_('Sorry! You Cannot Delete not Draft Order'))
        return models.Model.unlink(self)


class UrgentCasesPayments(models.Model):
    _name = 'urgent.cases.payments'
    _order = 'create_date desc'

    name = fields.Char(string='Ref')
    order_date = fields.Date(string="Order Date", default=datetime.today())
    committe_date = fields.Date(string="Committe Date", default=datetime.today())
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, ondelete='restrict')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    cases_ids = fields.Many2many('emergency.and.urgent.cases', string='Cases')
    amount = fields.Float(string='Amount')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('done', 'Done'), ('cancel', 'Cancel')],
                             default='draft', string="Status")
    subject = fields.Text(string='Description')
    _sql_constraints = [
        ('committe_date_uniq', 'unique (committe_date)',
         'Sorry ! You Can NOT Create More Than One payment for the Same Committe Date')]
    
    @api.constrains('subject')
    def string_validation(self):
        if self.subject:
            if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.subject.replace(" ","")):
                raise ValidationError(_('Subject Can not begin with white space or special charector'))
            if self.subject and (len(self.subject.replace(' ', '')) <= 0):
                raise exceptions.ValidationError(_("Subject Can not begin with white space or special charector"))
    
    # @api.onchange('cases_ids')
    # def fixedDate(self):


    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.sequence.number_next_actual

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('urgent.cases.payments') or '/'
        return super(UrgentCasesPayments, self).create(vals)

    @api.multi
    def confirm(self):
        if not self.cases_ids:
            raise exceptions.UserError(_('Sorry! You MUST add at least one Case'))
        else:
            self.write({'state': 'confirm'})
            for case in self.cases_ids:
                self.amount += case.amount

    @api.multi
    def cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def done(self):
        for c in self.cases_ids:
            payment_lines = []
            payment_lines += [(0, 6, {
                'name': c.name,
                'account_id': c.case_classification.property_account_id.id,
                'quantity': 1,
                'name': _('Urgent Cases Payment'),
                'price_unit': c.amount,
            })]
            voucher = self.env['account.voucher'].create(
                {
                    'name': c.name,
                    'company_id': self.company_id.id,
                    'journal_id': c.case_classification.journal_id.id,
                    'analytic_account_id':c.case_classification.property_analytic_account_id.id,
                    'company_id': self.company_id,
                    'amount': c.amount,
                    'company_id': self.company_id.id,
                    'pay_now': 'pay_later',
                    'reference': c.name,
                    'voucher_type': 'purchase',
                    'description': self.subject,
                    'partner_id': c.partnrt_id.faqeer_id.id,
                    'line_ids': payment_lines
                })
            c.voucher_id = voucher.id
            self.write({'state': 'done'})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state not in ('draft'):
                raise exceptions.UserError(_('Sorry! You Cannot Delete not Draft Order'))
        return models.Model.unlink(self)


class OrphanGranteePlanning(models.Model):
    _name = 'orphang.rantee.planning'
    _order = 'create_date desc'

    name = fields.Char(string='Name of Plan', size=256)
    code = fields.Char(string='Ref')
    order_date = fields.Date(string="Order Date", default=datetime.today())
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                ondelete='restrict')
    local_state_id = fields.Many2one('zakat.local.state' , 'Local State' )
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'),('done', 'Done'), ('cancel', 'Cancel')],
        default='draft', string="Status")
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    sector_ids = fields.One2many(comodel_name='orphan.grantee.plan.sub', inverse_name='plan_id')
    type = fields.Selection([('a_u', 'Administrative Unit '), ('z_c', 'Zakat Committee')], string="Type", default="a_u")

    @api.model
    def get_seq_to_view(self):
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('basal.drainage.sequence') or '/'
        return super(OrphanGranteePlanning, self).create(vals)
    @api.constrains('name','sector_ids')
    def name_validation(self):
        notvalid =False
        for letter in self.name:
            if (not letter.isalpha() and not letter.isdigit()):
               notvalid =True
        if notvalid:
           raise ValidationError(_('Name Should contain Only Charactors or numbers and can not begin with white space or apecial charactor'))
        if not self.sector_ids:
           raise ValidationError('Sorry! you must Select at least one admin unit')
    @api.multi
    def confirm(self):
        if not self.sector_ids:
           raise UserError('you Must select at least one adminstrative unit')
        self.write({'state': 'confirm'})

    @api.multi
    def cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def done(self):
        self.write({'state': 'done'})

   
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state not in ('draft'):
                raise exceptions.UserError(_('Sorry! You Cannot Delete not Draft Order'))
        return models.Model.unlink(self)

    @api.constrains('date_from', 'date_to')
    def duration_vslidstion(self):
        for rec in self:
            if rec.date_from < rec.date_to:
                return True
            else:
                raise ValidationError(_("Start Date must be befor the End Date"))


class OrphanGranteePlanning2(models.Model):
    _name = 'orphan.grantee.plan.sub'
    _order = 'create_date desc'

    plan_id = fields.Many2one('orphang.rantee.planning', '')
    unit_of_adminstrative_id = fields.Many2one('zakat.admin.unit', 'Admin Unit')
    no_of_families = fields.Integer(string='Number of Families')
    executing_actual = fields.Integer(string="Executing Actual")
    percentage = fields.Float(string='Percentage')
    zakat_committe_id = fields.Many2one('zakat.dzc1.committe','Zakat Committe')
    committee = fields.Many2one('zakat.dzc1.committee', string="Committee")

    _sql_constraints = [
        ('unique_plan_a_c', 'unique(plan_id,admin_unit_id,committee)', _('You Cannot Have The Same Committee'))

    ]

    @api.constrains('no_of_families')
    def validation(self):
        if self.no_of_families <= 0 :
           raise ValidationError('No of Families MUST be greater than ZERO')


"""
Faqir insurance health 
"""


class FaqirInsuranceHealth(models.Model):
    _inherit = 'zakat.aplication.form'
    _order = 'create_date desc'

    no_insurance = fields.Char(string="No.Insurance")
    no_head_of_family = fields.Integer(string="No. Head of Family")
    insurance_start_date = fields.Date(string=" Insurance start date")
    insurance_end_date = fields.Date(compute="set_end_date", string="Insurance end date",store=True,)
    guarntee_id = fields.Many2one('zakat.guarantees')

    _sql_constraints = [('uniq_insurance', 'unique(no_insurance)',
                         _("Sorry !No Of Insurance Must be Uniqu"))]

    @api.depends('insurance_start_date')
    def set_end_date(self):
        if self.insurance_start_date:
            validity = self.env['zakat.guarantees'].search([('type', '=', 'i_health')])
            if validity:
                for valid in validity:
                    end = valid.card_validity
                    self.insurance_end_date = (
                                datetime.strptime(self.insurance_start_date, '%Y-%m-%d') + relativedelta(years=end))
            else:
                raise ValidationError(_("There is No Guarntee Configuration for Health Insurance."))


class monthlySupport(models.Model):
    _name = 'zakat.monthly.support'
    _inherits = {'zakat.guarantee.order': 'order_id'}
    _order = "create_date desc"
    _description = 'Case Study Monthly Support Payment'

    order_id = fields.Many2one('zakat.guarantee.order', ondelete='cascade')
    partner_id = fields.Many2one('res.partner')
    ref = fields.Char(string="Reference")
    amount = fields.Float(string="Amount", compute="get_info")
    no_active_card = fields.Char(compute="get_info")
    insurance_ids = fields.One2many('zakat.monthly.lines', 'insurance_order')
    voucher_id = fields.Many2one('account.voucher', ondelete="restrict")
    state_id = fields.Many2one('zakat.state')

    @api.multi
    def unlink(self):
        """
        prevent Record Remove if it not in draft state
        :return:
        """
        for record in self:
            if record.state != 'draft':
                raise exceptions.ValidationError(_("You Cannot Remove Record If it not in Dratf State"))
            elif record.state == 'draft':
                self.order_id.unlink()
                return super(monthlySupport, self).unlink()

    @api.multi
    def action_confirm(self):
        """
        change state To Confirm
        :return:
        """
        self.write({'state': 'confirm'})

    @api.multi
    def action_approve(self):
        """
        change state To Approve
        :return:
        """
        if not self.insurance_ids:
            raise exceptions.ValidationError(_("Please Make Sure You Have Insurance Guaranteed"))
        self.write({'state': 'approve'})

    @api.multi
    def action_done(self):
        """
        change state To Done
        :return:
        """
        line = []
        guarantees = self.env['zakat.guarantees'].search([('company_id', '=', self.env.user.company_id.id),
                                                          ('type', '=', self.type)])
        line += [(0, 6, {
            'name': _('Health Insurance'),
            'account_id': guarantees.property_account_id.id,
            'account_analytic_id': guarantees.property_analytic_account_id.id,
            'quantity': 1,
            'price_unit': self.amount,
        })]

        voucher_id = self.env['account.voucher'].create(
            {
                'name': '',
                'partner_id': self.partner_id.id,
                'journal_id': guarantees.journal_id.id,
                'pay_now': 'pay_later',
                'reference': _('Health Insurance Payment'),
                'voucher_type': 'purchase',
                'company_id': self.env.user.company_id.id,
                'line_ids': line,

            })
        self.voucher_id = voucher_id.id
        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        """
        change state To Confirm
        :return:
        """
        self.write({'state': 'cancel'})

    @api.multi
    def action_draft(self):
        """
        change state To Confirm
        :return:
        """
        self.write({'state': 'draft'})

    @api.model
    def get_seq_to_view(self):
        """
        Get sequence in code filed in form view
        :return:
        """
        sequence = self.env['ir.sequence'].search([('code', '=', self._name)])
        return sequence.get_next_char(sequence.number_next_actual)

    @api.model
    def create(self, vals):
        """
        create sequence
        :param vals: fields values from view
        :return: dict
        """
        # set new sequence number in code for every new record
        vals['name'] = self.env['ir.sequence'].get(self._name) or '/'
        return super(monthlySupport, self).create(vals)

    @api.one
    @api.depends('insurance_ids')
    def get_info(self):
        """
        To Get The Number of Social Supported Number and The Total Amount
        :return:
        """
        total = 0
        count = 0
        for record in self.insurance_ids:
            count += 1
            total += record.insurance_amount
        self.amount = total
        self.no_active_card = count

    @api.multi
    def get_data(self):
        """
        To get Data From Al-faqir Model who have Health Insurance
        :return:
        """
        data = self.env['zakat.aplication.form'].search([('company_id', '=', self.env.user.company_id.id),
            ('monthly_support', '=', True),('state_id', '=', self.state_id.id),('state','=','done')])
        if not data:
            raise exceptions.ValidationError(_("There is no Data"))
        for faqir in data:
            self.insurance_ids.create({
                'guaranteed_id': faqir.id,
                'insurance_amount': faqir.monthly_support_amount,
                'insurance_order': self.id
                })
            data.write({
                'monthly_support_payment':self.id,
            })


class InsuranceLines(models.Model):
    _name = 'zakat.monthly.lines'
    _order = 'create_date desc'

    insurance_amount = fields.Float()
    guaranteed_id = fields.Many2one('zakat.aplication.form')
    i_enddate = fields.Date(related="guaranteed_id.insurance_end_date")
    insurance_order = fields.Many2one('zakat.monthly.support', ondelete='cascade')

    _sql_constraints = [('uniq_guaranteed_insurance_order', 'unique(guaranteed_id,insurance_order)',
                         _("Guarantee Cannot Be Given To the Same Person Twice !"))]
