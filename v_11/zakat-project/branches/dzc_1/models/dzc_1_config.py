# -*- coding: utf-8 -*-
# Copyright 2018, AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, exceptions, api, _
import re
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import datetime



class dzc_1ChannelCommittee(models.Model):
    _name = 'zakat.dzc1.committee'
    _rec_name = 'committee_name'
    _description = ''
    _sql_constraints = [
        ('committee_name_uniq', 'unique (committee_name)', _('The committee_name must be unique !')),
    ]
    # sector name abut res.country 
    administrative_unit_id = fields.Many2one('zakat.admin.unit',
                                             string='Administrative Unit', ondelete="restrict")
    committee_name = fields.Char(string='Committee Name')
    head_of_committee = fields.Char(string='Head Of Committee Name')
    phone_number = fields.Char(string='Phone Number')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    member_ids = fields.One2many('zakat.dzc1.committee.member','committee_id')

    # validation phone number
    @api.constrains('phone_number')
    def _check_phone_number(self):
        for rec in self:
            if rec.phone_number and len(rec.phone_number) != 10:
                raise ValidationError(_("you phone must be 10 numeric number "))
            elif rec.phone_number and not str(rec.phone_number).isdigit():
                raise ValidationError(_("you phone must be digit not string"))
        return True

        
    # constrains in head of committee
    @api.multi
    @api.constrains('head_of_committee')
    def _check_hod_committee_name(self):

        for rec in self:
            if rec.head_of_committee.isalpha() or ' ':
                return True
            else:
                raise ValidationError(_("The name is entared in not valid"))
        return True


    @api.constrains('committee_name')
    def _check_committee_name(self):
        for record in self:
            if record.committee_name.isalpha() or ' ':
                return True
            else:
                raise ValidationError(_("The name is entared in not valid"))
        return True


class ZakatcommitteeMember(models.Model):
    _name = 'zakat.dzc1.committee.member'

    name = fields.Char()
    phone_number = fields.Char("Phone Number")

    @api.constrains('phone_number')
    def _check_phone_number(self):
        for rec in self:
            if rec.phone_number and len(rec.phone_number) != 10:
                raise ValidationError(_("you phone must be 10 numeric number "))
            elif rec.phone_number and not str(rec.phone_number).isdigit():
                raise ValidationError(_("you phone must be digit not string"))
        return True
    committee_id = fields.Many2one('zakat.dzc1.committee')
    
    @api.constrains('name')
    def fields_check(self):
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.name.replace(" ", "")):
            raise ValidationError(_('Member name Field must be Literal'))

class ZakatDiagnosticSectors(models.Model):
    _name = 'zakat.diagnostic.sectors'
    _rec_name = "name"
    _description = 'All diagnostic sectors for this channel'

    name = fields.Char(string='Diagnostic Sector Name')
    sector_no = fields.Char(string='Sector Number')
    illness_ids = fields.One2many('zakat.illness', 'sector_id')

    _sql_constraints = [('sector_name_uniq', 'unique (name)',
                         _('Sorry ! The Diagnosis Sector Name Must Be Unique .')),
                        ('sector_no_uniq', 'unique (sector_no)',
                         _('Sorry ! The Diagnosis Sector Number Must Be Unique .'))]

    @api.multi
    def unlink(self):
        """
        If sector hase an Illness should not be removed
        :raise exception
        """
        illiness = self.env['zakat.illness'].search([])
        for illi in illiness:
            if illi.sector_id.id in self.ids:
                raise exceptions.ValidationError(_("Diagnosis Sector Cannot Be Removed"))
        return super(ZakatDiagnosticSectors, self).unlink()

    @api.constrains('name', 'sector_no')
    def fields_check(self):
        """
        Check if name field contain an invalid value
        :raise exception
        """
        num_pattern = re.compile(r'\d', re.I | re.M)
        white_space = re.compile(r'^\s')

        if not re.match("^[0-9]*$", self.sector_no.replace(" ", "")):
            raise ValidationError(_('Diagnosis Sector Number Field must be number'))
        if self.sector_no.replace(" ", "") != self.sector_no:
            raise ValidationError(_('Diagnosis Sector Number Field must be number'))
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.name.replace(" ", "")):
            raise ValidationError(_('Diagnosis Sector name Field must be Literal'))

        if int(self.sector_no) < 0:
            raise exceptions.ValidationError(_("Diagnosis Sector Number Cannot Be Less Than Zero"))
        if self.sector_no == '0':
            raise exceptions.ValidationError(_("Diagnosis Sector Number Cannot Be Zero"))
        if num_pattern.search(self.name):
            raise exceptions.ValidationError(_("Name Field Cannot Accept Numbers or Special Character"))
        if white_space.search(self.name):
            raise exceptions.ValidationError(_("Name Field Is Required (Cannot Accept White Space)"))
        if not num_pattern.search(self.sector_no):
            raise exceptions.ValidationError(_("Diagnostic Sectors Cannot Be Character"))
        if white_space.search(self.sector_no):
            raise exceptions.ValidationError(_("Diagnostic Sectors Number (Cannot Accept White Space)"))

    # @api.constrains('sector_no')
    # def name_validation(self):
    #     for record in self:
    #         if record.sector_no >= 0 :
    #             return True
    #         else:
    #             raise ValidationError(_('Sorry ! Sector No Cannot Be negative .'))
    #
    # @api.constrains('name')
    # def name_validation(self):
    #     increment = 0
    #     if len(self.name) > 1 :
    #         for record in self.name[1:]:
    #             if record.isalpha() or record.isdigit():
    #                 increment +=1
    #             if increment == 0 :
    #                 raise ValidationError(_("Sorry! Sector Name Field is Required And cannot start with special character ."))
    #
    #     elif len(self.name) <= 1 and self.name[0] == ' ':
    #         raise ValidationError(_("Sorry! Sector Name Field is Required And cannot start with special character ."))


class HospitalTreatment(models.Model):
    _name = 'hospital.treatment'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        show only hospital that is not selected
        :return: list of ids
        """
        if self._context.get('hospital_sub_choice', False):
            if self._context.get('hospital_sub_choice', []):
                hospital_id = self.env['hospital.ceiling'].resolve_2many_commands('hospital_sub_choice_ids',
                                                                                  self._context.get(
                                                                                      'hospital_sub_choice', []))
                args.append(('id', 'not in',
                             [isinstance(d['hospital_id'], tuple) and d['hospital_id'][0] or d['hospital_id']
                              for d in hospital_id]))
                return super(HospitalTreatment, self).name_search(name, args=args, operator=operator, limit=limit)
        if not self._context.get('hospital_sub_choice', False):
            return super(HospitalTreatment, self).name_search(name, args=args, operator=operator, limit=limit)

    name = fields.Char(string='Therapeutic unit', size=164)
    main_owner = fields.Char(string='Owner Name')
    doc_image = fields.Binary(string='Image Certification')
    file_name = fields.Char()
    location_name = fields.Char(string=' Location Name  ')
    staff_ids = fields.One2many(
        'staff.staff',
        'hospital_treatment_id',
        string='Staff Member',
    )
    establish_date = fields.Date(string='Date of Establishment')
    contract_date = fields.Date(string='Date of Zakat Contract', default=datetime.now())
    hospital_roof = fields.One2many('hospital.ceiling.subclass', 'hospital_id')
    op_fees_ids = fields.One2many('zakat.operations.fees', 'hospital_name_id', string="Operation Fees")
    Type = fields.Selection([('hospital', 'Hospital'), ('pharmacy', 'Pharmacy'), ('medical_center', 'Medical Center')])
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approve'), ('cancel', 'Cancel')], string='Status', default='draft')
    contract = fields.Boolean('Contractor', default=True)
    position = fields.Selection([('int', 'Internal'), ('ex', 'External')],default='int')

    @api.constrains('name', 'main_owner')
    def _uniqueness(self):
        if self.env['hospital.treatment'].search(
                ['&', ('name', '=', self.name), ('main_owner', '=', self.main_owner), ('id', '!=', self.id)]):
            raise ValidationError(
                _("this hospital with the same name and same owner name and establishment date is already exist"))

    @api.constrains('name', 'location_name', 'main_owner')
    def check_name(self):
        if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.name.replace(" ","")):
            raise ValidationError(_('name Field must be Literal'))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("name must not be spaces"))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("name must not be spaces"))
        if self.contract:
            if not re.match(
                    "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                    self.location_name.replace(" ", "")):
                raise ValidationError(_('Location Name Field must be Literal'))
            if self.name and (len(self.location_name.replace(' ', '')) <= 0):
                raise exceptions.ValidationError(_("Location Name must not be Spaces"))
            if self.name and (len(self.location_name.replace(' ', '')) <= 0):
                raise exceptions.ValidationError(_("Location  must not be Spaces"))
            if not re.match(
                    "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                    self.main_owner.replace(" ", "")):
                raise ValidationError(_('Owner Name Field must be Literal'))
            if self.name and (len(self.main_owner.replace(' ', '')) <= 0):
                raise exceptions.ValidationError(_("Owner Name must not be Spaces"))
            if self.name and (len(self.main_owner.replace(' ', '')) <= 0):
                raise exceptions.ValidationError(_("Owner Name must not be Spaces"))

    @api.constrains('file_name', 'doc_image')
    def check_file(self):
        """
        Check if file extination is not valid
        :raise
        """
        name = str(self.file_name)
        ext = name.split('.', 1)
        if self.file_name:
            if ext[1] not in ['jpg', 'jpeg', 'pdf']:
                raise exceptions.ValidationError(_("Invalid File Format You Can Upload (PDF/JPG/JPEG)"))

    @api.constrains('establish_date', 'contract_date')
    def compare_date(self):
        if self.establish_date and self.contract_date:
            for rec in self:
                if rec.establish_date < rec.contract_date:
                    return True
                else:
                    raise ValidationError(_("Contract Date must be after the Establishment Date"))

    @api.multi
    def approve(self):
        self.write({'state': 'approve'})

    @api.multi
    def set_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def contract_termination(self):
        self.write({'state': 'cancel'})

    @api.multi
    def unlink(self):
        """
        Prevent unlink record if it state not in draft
        :return:
        """
        for record in self:
            if record.state != 'draft':
                raise exceptions.ValidationError(_("This Record Could not Be Removed it's not in draft state"))
            else:
                return super(HospitalTreatment, self).unlink()

    @api.multi
    def copy(self, default=None):
        """
        Prevent duplicate
        :raise: exceptions
        """
        raise exceptions.ValidationError(_("Record Could not Be Duplicated"))


class HospitalStaff(models.Model):
    _name = 'staff.staff'
    _description = ''
    # staff member in hospital 
    name = fields.Char(string='Staff Member Name ')

    hospital_treatment_id = fields.Many2one('hospital.treatment',
                                            string='Field Label', ondelete="restrict")
    phone_number = fields.Char("Phone Number")
    title = fields.Selection([
        ('medical', 'Medical Director'),
        ('account', 'Account Manager'),
        ('delegate', 'Delegate'),
        ('general', 'General'),
    ])

    @api.constrains('name')
    def _check_staff_member_name(self):
        for rec in self:
            if rec.name.isalpha() or ' ':
                return True
            else:
                raise ValidationError(_("The name is Entered is not valid"))

    @api.constrains('phone_number')
    def _check_phone_number(self):
        for rec in self:
            if rec.phone_number and len(rec.phone_number) != 10:
                raise ValidationError(_("you phone must be 10 numeric number "))
            elif rec.phone_number and not str(rec.phone_number).isdigit():
                raise ValidationError(_("you phone must be digit not string"))
        return True


class Zakat_illness(models.Model):
    _name = 'zakat.illness'

    _rec_name = 'name'

    _sql_constraints = [
        ('illness_name_constraints', 'unique(name)', _('The Illness name must not be repeated'))
    ]

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        show only illness that is not selected
        :return: list of ids
        """
        if self._context.get('op_fees_ids', []):
            illness_id = self.env['hospital.treatment'].resolve_2many_commands('op_fees_ids',
                                                                               self._context.get('op_fees_ids', []))
            args.append(('id', 'not in',
                         [isinstance(d['illness_id'], tuple) and d['illness_id'][0] or d['illness_id']
                          for d in illness_id]))
        return super(Zakat_illness, self).name_search(name, args=args, operator=operator, limit=limit)

    name = fields.Char(string="Illness Name")
    sector_id = fields.Many2one('zakat.diagnostic.sectors', 'Diagnostic Sector', ondelete="restrict")
    operation_ids = fields.One2many('zakat.operations.fees', 'illness_id', string="Operation Fees")

    @api.constrains('name')
    def fields_check(self):
        """
        Check if name field contain an invalid value
        :raise exception
        """
        num_pattern = re.compile(r'\d', re.I | re.M)
        white_space = re.compile(r'^\s')

        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.name.replace(" ", "")):
            raise ValidationError(_('name Field must be Literal'))

        if num_pattern.search(self.name):
            raise exceptions.ValidationError(_("Name Field Cannot Accept Numbers"))
        if white_space.search(self.name):
            raise exceptions.ValidationError(_("Name Field Is Required (Cannot Accept White Space)"))


#############################
# Hospital Operations Fees
#############################
class Operation_fees(models.Model):
    _name = 'zakat.operations.fees'

    name = fields.Char()
    operation_fees = fields.Float(string='Operation Fees', store=True)
    illness_id = fields.Many2one('zakat.illness', ondelete="restrict", store=True)
    hospital_name_id = fields.Many2one('hospital.treatment', ondelete="restrict")
    discount = fields.Float(string="Discount")

    @api.onchange('illness_id')
    def _onchange_(self):
        self.name = self.illness_id.name

    ############ SQL VALIDATION CONSTRAINS ############
    # @api.one
    @api.constrains('operation_fees')
    def _check_fees(self):
        if self.operation_fees <= 0.0:
            raise ValidationError(_('Sorry! Fees cannot be negative or Zero.'))


############## =========================##########

class ZakatGuarantees(models.Model):
    _name = 'zakat.guarantees'

    name = fields.Char()
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 ondelete='restrict')
    type = fields.Selection([('s_support', 'Social Support'),
                             ('i_health', 'Insurance Health'),
                             ('student', 'Student'),
                             ('orphan', 'Orphan')], default='s_support')
    amount = fields.Float(string="Amount")
    property_account_id = fields.Many2one('account.account', string="Guarantees Account", company_dependent=True)
    property_analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account",
                                                   company_dependent=True)
    journal_id = fields.Many2one('account.journal', string="Guarantees Journal", company_dependent=True)

    classification = fields.Selection([('i_m', 'Imam & Muezzin'), ('sheikh', 'Sheikh'),
                                       ('deaf', 'Deaf'), ('blind', 'Blind'), ('di_physically', 'Disabled Physically'),
                                       ('m_h', 'Mentally Handicapped')])
    support_type = fields.Selection([('fixed', 'Fixed'), ('not_fixed', 'Not Fixed')])
    card_validity = fields.Integer(string="Card Validity(Years)")

    _sql_constraints = [('uniq_company_type', 'unique(company_id,type)',
                         _("The Company and it's Type must be unique !"))]

    @api.model
    def create(self, vals):
        """
        assign Name To Guarantess
        :param vals: field
        :return:
        """
        vals.update({'company_id': self.env.user.company_id.id})
        company = self.env['res.company'].search([('id', '=', vals['company_id'])])
        vals['name'] = company.name + '-' + dict(self.fields_get(allfields=['type'])['type']['selection'])[vals['type']]
        return super(ZakatGuarantees, self).create(vals)


class UrgentEmergencyType(models.Model):
    _name = 'zakat.urgentemergencytype'

    name = fields.Char(string="Name", size=256)
    journal_id = fields.Many2one('account.journal', 'Journal', company_dependent=True)
    property_account_id = fields.Many2one('account.account', string="Account", company_dependent=True)
    property_analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account",
                                                   company_dependent=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id)
    document_ids = fields.One2many('needed.document','emergency_type_id',string='Documents')

    _sql_constraints = [('uniq_company_type', 'unique(company_id,name)',
                         _("The Company and it's Type must be unique !"))]

    @api.constrains('name')
    def check_name(self):
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.name.replace(" ", "")):
            raise ValidationError(_('Name Field must be Literal'))


class DocumentCommentedInDemo(models.Model):
    _name = 'needed.document'

    name = fields.Char()
    emergency_type_id = fields.Many2one('zakat.urgentemergencytype')

#####################################
#
#
# Configuration Of Ratification list
#
#
#####################################


class RatificationType(models.Model):
    _name = 'zakat.ratification.type'

    type = fields.Selection([('it', 'Internal Treatment'),
                             ('at', 'Abroad Treatment'),
                             ('drugs', 'Drugs, Treatments And Tests')],
                            string="Type", required=True)
    name = fields.Char(string="Name")
    contribution = fields.Selection([('p', 'Percentage'), ('fi', 'Fixed Amount')])
    _sql_constraints = [
        ('type', 'unique(name,type)', _('This Ratification Type Must Be Unique.')),
    ]

    @api.constrains('contribution')
    def check_contribution(self):
        """
        Check if the contribution is selected ot not
        :raise:
        """
        if self.type == 'it':
            if self.contribution == False:
                raise exceptions.ValidationError(_("Please Select The Contribution Type"))

    @api.constrains('name')
    def check_name(self):
        if not re.match("^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$", self.name.replace(" ","")):
            raise ValidationError(_('Name Field must be Literal'))
        if self.name and (len(self.name.replace(' ', '')) <= 0):
            raise exceptions.ValidationError(_("Name must not be spaces"))


class ListOfRatifications(models.Model):
    _name = "zakat.ratification"

    name = fields.Char(string="Ratification Name", required=True)
    type = fields.Selection([('it', 'Internal Treatment'),
                             ('at', 'Abroad Treatment'),
                             ('drugs', 'Drugs, Treatments And Tests')],
                            string="Type", required=True)
    ratification_type = fields.Many2one('zakat.ratification.type')
    contribution = fields.Selection([('p', 'Percentage'), ('fi', 'Fixed Amount')],
                                    related="ratification_type.contribution")
    ratification_list = fields.Selection([('dtt', 'Drugs, Treatments And Tests'),
                                          ('is', 'Internal Surgery (Internal Treatment)'),
                                          ('as', 'Abroad Surgery (Abroad Treatment)')],
                                         string='Ratification List', required=True, default='dtt')
    # IS_type = fields.Selection([('gov', 'Government'),
    #                             ('spe', 'Special'),
    #                             ('kck', 'Knee Surgery To Change The knee Joint')], string="Type")
    # AS_type = fields.Selection([('general', 'General'),
    #                             ('ctc', 'Cancerous Tumors And Military Commission'),
    #                             ('ppc', 'Police And Protocol Commission')], string="Types Of Abroad Treatment")
    ceiling_ids = fields.One2many('zakat.ceiling', 'ratification_id', string="Ceiling")
    ceiling_ids_is = fields.One2many('zakat.ceiling', 'ratification_id', string="Ceiling")
    ceiling_ids_as = fields.One2many('zakat.ceiling', 'ratification_id', string="Ceiling")
    ceiling_ids_kck = fields.One2many('zakat.ceiling', 'ratification_id', string="Ceiling")
    property_zakat_account_id = fields.Many2one('account.account', ondelete="restrict", string="Zakat Account",
                                                company_dependent=True)
    property_financial_account_id = fields.Many2one('account.account', ondelete="restrict", string="Financial Account",
                                                    company_dependent=True)
    property_analytic_account_id = fields.Many2one('account.analytic.account', ondelete="restrict",
                                                   string="Analytic Account",
                                                   company_dependent=True)
    zakat_journal = fields.Many2one('account.journal', ondelete="restrict", string="Zakat Journal",
                                    company_dependent=True)
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('cancel', 'Canceled')], default='draft',
                             string="Status")
    year = fields.Char(string="Period")
    months = fields.Char()

    _sql_constraints = [
        ('ratification_type', 'unique(ratification_type,name)', _('This Ratification List Is Already Exist.')),
    ]

    @api.constrains('name')
    def fields_check(self):
        """
        Check if name field contain an invalid value
        :raise exception
        """
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.name.replace(" ", "")):
            raise ValidationError(_('Name Field Must be Literal'))

    @api.multi
    def unlink(self):
        """
        To prevent recode delete if it link with federal treatment model
        or in approve state
        :return:
        """
        federal_treatment = self.env['zkate.federaltreatment'].search([])
        for treatment in federal_treatment:
            if treatment.ratification_id.id in self.ids:
                raise exceptions.ValidationError(
                    _('Sorry , this ratification list is already used you can not delete it.'))
        for ratification in self:
            if ratification.state != 'draft':
                raise exceptions.ValidationError(_("Ratification List Cannot Be Removed When it not in Draft State"))
            if ratification.state == 'draft':
                return super(ListOfRatifications, self).unlink()

    @api.constrains('year', 'months')
    def check_period(self):
        """
        One of period field must have value
        :return:
        """
        if self.year:
            if not re.match("^[0-9]*$", self.year.replace(" ", "")):
                raise ValidationError(_('Year Field must be number'))
            if self.year.replace(" ", "") != self.year:
                raise ValidationError(_('Year Number Field must be number'))
        if self.months:
            if not re.match("^[0-9]*$", self.months.replace(" ", "")):
                raise ValidationError(_('Months Field must be number'))
            if self.months.replace(" ", "") != self.months:
                raise ValidationError(_('Months Number Field must be number'))
            if int(self.months) > 11:
                raise exceptions.ValidationError(_('Months Field Cannot Be Greater Than 11'))
        if not self.months and not self.year:
            raise exceptions.ValidationError(_("You Must Enter The Period"))

    @api.constrains('ceiling_ids', 'ceiling_ids_is', 'ceiling_ids_as', 'ceiling_ids_kck')
    def check_ceiling(self):
        """
        To check ceiling Data that we must have one greater than
        and raise exception if we have more or less than one
        :return: raise exception
        """
        check = 0
        if self.ceiling_ids:
            for ceiling in self.ceiling_ids:
                if ceiling.greater == 'yes':
                    check += 1
            if check > 1:
                raise exceptions.ValidationError(_("Sorry !! You cannot have More Than One Ceiling"
                                                   " Allowed To Exceeding The Limit"))
            elif check == 0:
                raise exceptions.ValidationError(_("You Must Have One Ceiling  That Allow You To Exceed The Limit"))

            # elif check == 1:
            #     raise exceptions.ValidationError(
            #         _("You Must Remove the Previous ability To Exceed The Limit, To Add New Ceiling"))

        elif self.ceiling_ids_as:
            for ceiling in self.ceiling_ids_as:
                if ceiling.greater == 'yes':
                    check += 1
            if check > 1:
                raise exceptions.ValidationError(_("Sorry !! You cannot have More Than One Ceiling"
                                                   "Allowed To Exceeding The Limit"))
            elif check == 0:
                raise exceptions.ValidationError(_("You Must Have One Ceiling  That Allow You To Exceed The Limit"))
        elif self.ceiling_ids_is:
            for ceiling in self.ceiling_ids_is:
                if ceiling.greater == 'yes':
                    check += 1
            if check > 1:
                raise exceptions.ValidationError(_("Sorry !! You cannot have More Than One Ceiling"
                                                   "Allowed To Exceeding The Limit"))
            elif check == 0:
                raise exceptions.ValidationError(_("You Must Have One Ceiling  That Allow You To Exceed The Limit"))
        elif self.ceiling_ids_kck:
            for ceiling in self.ceiling_ids_kck:
                if ceiling.greater == 'yes':
                    check += 1
            if check > 1:
                raise exceptions.ValidationError(_("Sorry !! You cannot have More Than One Ceiling"
                                                   "Allowed To Exceeding The Limit"))
            elif check == 0:
                raise exceptions.ValidationError(_("You Must Have One Ceiling  That Allow You To Exceed The Limit"))

    @api.constrains('period')
    def check_field(self):
        """
        To check any field in constrains decorator
        :return: raise exception
        """
        if self.period <= 0:
            raise exceptions.ValidationError(_('Period Cannot Be Zero  Or Less Than Zero'))

    @api.constrains('ceiling_ids', 'ceiling_ids_is', 'ceiling_ids_as', 'ceiling_ids_kck')
    def _check_member(self):
        count = 0
        if not self.ceiling_ids:
            for record in self.ceiling_ids:
                count += 1
            if count == 0:
                raise exceptions.ValidationError(_("The Ceiling For The Ratification Cannot Be empty"))
        elif not self.ceiling_ids_is:
            for record in self.ceiling_ids_is:
                count += 1
            if count == 0:
                raise exceptions.ValidationError(_("The Ceiling For The Ratification Cannot Be empty"))
        elif not self.ceiling_ids_as:
            for record in self.ceiling_ids_as:
                count += 1
            if count == 0:
                raise exceptions.ValidationError(_("The Ceiling For The Ratification Cannot Be empty"))
        elif not self.ceiling_ids_kck:
            for record in self.ceiling_ids_kck:
                count += 1
            if count == 0:
                raise exceptions.ValidationError(_("The Ceiling For The Ratification Cannot Be empty"))

    @api.multi
    def action_approve(self):
        """
        Change state to approve
        :return:
        """
        self._check_member()
        self.write({'state': 'approve'})

    @api.multi
    def action_draft(self):
        """
        Change state to approve
        :return:
        """
        self.write({'state': 'draft'})

    @api.multi
    def action_cancel(self):
        """
        change state to cancel
        :return:
        """
        self.write({'state': 'cancel'})

    @api.onchange('ratification_list')
    def chcange_type(self):
        """
        Chanege Type When Ratification list is changed
        :return:
        """
        if self.ratification_list == 'dtt':
            self.type = 'drugs'
        elif self.ratification_list == 'is':
            self.type = 'it'
        elif self.ratification_list == 'as':
            self.type = 'at'

    @api.model
    def create(self, vals):
        """
        To check if the ratification list is already exist
        :param vals: field value in the ui
        :return: dict
        """
        if vals['ratification_list'] == 'dtt':
            vals.update({'type': 'drugs'})
        elif vals['ratification_list'] == 'is':
            vals.update({'type': 'it'})
        elif vals['ratification_list'] == 'as':
            vals.update({'type': 'at'})
        if 'ceiling_ids' not in vals and 'ceiling_ids_is' not in vals and 'ceiling_ids_as' not in vals and 'ceiling_ids_kck' not in vals:
            raise exceptions.ValidationError(_("The Ceiling For The Ratification Cannot Be empty"))
        return super(ListOfRatifications, self).create(vals)

    def get_appropriate_ceiling(self, cost):
        max_ceiling = False
        min_ceiling = False
        for rec in self.ceiling_ids:
            if not min_ceiling:
                min_ceiling = rec
            if min_ceiling:
                if rec.From < min_ceiling.From:
                    min_ceiling = rec
            if rec.greater == 'yes':
                max_ceiling = rec
            if (cost >= rec.From and cost < rec.To):
                return rec, max_ceiling, min_ceiling
        return False, max_ceiling, min_ceiling


class TreatmentCeiling(models.Model):
    _name = 'zakat.ceiling'

    @api.multi
    def get_to_value(self):
        """
        To get To field value in the previous record and set it in the next from
        :return: int
        """
        i = 0
        if self._context.get('ceiling'):
            last = self._context.get('ceiling')[-1]
            if last[2] != False:
                if 'To' in last[2]:
                    i = last[2]['To']
                    return i
                elif 'To' not in last[2]:
                    item = self.env['zakat.ratification'].search([('id', '=', self.ratification_id.id)])
                    ceiling = self.env['zakat.ceiling'].search(
                        [('id', '!=', self.id), ('ratification_id', '=', item.id)], order='id desc', limit=1)
                    i = ceiling.To
                    return i

    @api.model
    def default_get(self, fields_list):
        """
        modify default_get to set new default value
        :param fields_list:fields that have a default value
        :return: int
        """
        res = super(TreatmentCeiling, self).default_get(fields_list)
        check = 0
        if self._context.get('ceiling', False):
            for item in self._context.get('ceiling'):
                if item[2]:
                    check = 1
        if check == 0:
            item = self.env['zakat.ratification'].search([('id', '=', self._context.get('ra'))])
            if item:
                p_ceiling = max(ci.id for ci in item.ceiling_ids if ci.id)
                ceiling = self.env['zakat.ceiling'].search([('id', '=', p_ceiling)])
                res.update({'From': ceiling.To})
        return res

    name = fields.Char()
    From = fields.Integer(string="Greater than or equals", required=True, default=get_to_value)
    To = fields.Integer(string="less than", required=True)
    zakat_pre = fields.Float(string="Zakat Percentage")
    financial_pre = fields.Float(string="Financial Percentage")
    zakat_amount = fields.Integer(string="Zakat Amount")
    financial_amount = fields.Integer(string="Financial Amount")
    greater = fields.Selection([('yes', 'Yes'), ('no', 'NO')], default='no', string="Greater")
    In = fields.Integer(string="In")
    give = fields.Integer(string="Give")
    ratification_id = fields.Many2one('zakat.ratification')
    rat_type = fields.Selection(related='ratification_id.type')

    @api.model
    def create(self, vals):
        if 'From' in vals:
            if vals['From'] <= 0:
                raise exceptions.ValidationError(_('From Can Not Be Zero or Less'))
        if 'To' in vals:
            if vals['To'] <= 0:
                raise exceptions.ValidationError(_('To Can Not Be Zero or Less'))
        if 'zakat_pre' in vals:
            if vals['zakat_pre'] <= 0.0:
                raise exceptions.ValidationError(_("Zakat Percentage Cannot Be Zero or Less"))
            if vals['zakat_pre'] < 0.0:
                raise exceptions.ValidationError(_('Zakat Percentage Can not Be Less Than zero'))
        if 'financial_pre' in vals:
            if vals['financial_pre'] < 0.0:
                raise exceptions.ValidationError(_('Financial Percentage Can not Be Less Than zero'))
        if 'zakat_pre' in vals:
            if vals['zakat_pre'] > 100:
                raise exceptions.ValidationError(_("Zakat Percentage Cannot Be More Than 100 %"))
        if 'financial_pre' in vals:
            if vals['financial_pre'] > 100:
                raise exceptions.ValidationError(_("Financial Percentage Cannot Be More Than 100 %"))
        if 'financial_pre' in vals:
            if vals['financial_pre'] == 0.0:
                raise exceptions.ValidationError(_("Financial Percentage Cannot Be Zero or Less"))
        if 'zakat_pre' in vals and 'financial_pre' in vals:
            if vals['zakat_pre'] != vals['financial_pre']:
                raise exceptions.ValidationError(_("Zakat and Financial Percentage Should Be Equal"))
        if 'zakat_amount' in vals:
            if vals['zakat_amount'] > vals['To']:
                raise exceptions.ValidationError(_("Zakat Amount Cannot Be More Than To"))
            elif vals['zakat_amount'] <= 0:
                raise exceptions.ValidationError(_("Zakat Amount Cannot Be Zero or Less"))
        if 'financial_amount' in vals:
            if vals['financial_amount'] > vals['To']:
                raise exceptions.ValidationError(_("Financial Amount Cannot Be More Than To"))
            elif vals['financial_amount'] <= 0:
                raise exceptions.ValidationError(_("Financial Amount Cannot Be Zero or Less "))
        return super(TreatmentCeiling, self).create(vals)

    @api.multi
    def write(self, vals):
        """
        Modify Write To check if any changed field value violate the constraint and
        :raise exception
        :return:
        """
        if 'From' in vals:
            if vals['From'] <= 0:
                raise exceptions.ValidationError(_('From Can Not Be Zero or Less'))
        if 'To' in vals:
            if vals['To'] <= 0:
                raise exceptions.ValidationError(_('To Can Not Be Zero or Less'))
        if 'zakat_pre' in vals:
            if vals['zakat_pre'] <= 0.0:
                raise exceptions.ValidationError(_("Zakat Percentage Cannot Be Zero or Less"))
            if vals['zakat_pre'] < 0.0:
                raise exceptions.ValidationError(_('Zakat Percentage Can not Be Less Than zero'))
        if 'financial_pre' in vals:
            if vals['financial_pre'] < 0.0:
                raise exceptions.ValidationError(_('Financial Percentage Can not Be Less Than zero'))
        if 'In' in vals:
            if vals['In'] <= 0 and self.greater == 'yes' and self.ratification_id.type != 'at':
                raise exceptions.ValidationError(_('In Can Not Be Zero or Less'))
        if 'give' in vals:
            if vals['give'] <= 0 and self.greater == 'yes' and self.ratification_id.type != 'at':
                raise exceptions.ValidationError(_('Give Can Not Be Zero or Less'))
        if 'give' in vals:
            if vals['give'] > self.In and self.greater == 'yes' and self.ratification_id.type != 'at':
                raise exceptions.ValidationError(_('Give Cannot  Be Greater Than In Value'))
        if 'zakat_pre' in vals:
            if vals['zakat_pre'] > 100:
                raise exceptions.ValidationError(_("Zakat Percentage Cannot Be More Than 100 %"))
        if 'financial_pre' in vals:
            if vals['financial_pre'] > 100:
                raise exceptions.ValidationError(_("Financial Percentage Cannot Be More Than 100 %"))
        if 'financial_pre' in vals:
            if vals['financial_pre'] == 0.0:
                raise exceptions.ValidationError(_("Financial Percentage Cannot Be Zero or Less"))
        if 'zakat_pre' in vals and 'financial_pre' in vals:
            if vals['zakat_pre'] != vals['financial_pre']:
                raise exceptions.ValidationError(_("Zakat and Financial Percentage Should Be Equal"))
        if 'zakat_amount' in vals:
            if vals['zakat_amount'] > self.To:
                raise exceptions.ValidationError(_("Zakat Amount Cannot Be More Than To"))
            elif vals['zakat_amount'] <= 0:
                raise exceptions.ValidationError(_("Zakat Amount Cannot Be Zero or Less"))
        if 'financial_amount' in vals:
            if vals['financial_amount'] > self.To:
                raise exceptions.ValidationError(_("Financial Amount Cannot Be More Than To"))
            elif vals['financial_amount'] <= 0:
                raise exceptions.ValidationError(_("Financial Amount Cannot Be Zero or Less "))
        return super(TreatmentCeiling, self).write(vals)

    @api.constrains('To', 'From')
    def check_from_to(self):
        if self.To < self.From:
            raise exceptions.ValidationError(_("To Value Cannot Be Less Than From"))
        check = 0
        if self._context.get('ceiling', False):
            for item in self._context.get('ceiling'):
                if item[2]:
                    check = 1
        if self.ratification_id and check == 0:
            item = self.env['zakat.ratification'].search([('id', '=', self.ratification_id.id)])
            ceiling = self.env['zakat.ceiling'].search([('id', '!=', self.id), ('ratification_id', '=', item.id)],
                                                       order='id desc', limit=1)
            if len(ceiling) != 0:
                if ceiling.To != self.From:
                    raise exceptions.ValidationError(_("From Value Cannot Be More or Less Than Previous To Value"))
                if ceiling.greater == 'yes':
                    raise exceptions.ValidationError(
                        _("You Must Remove the Previous ability To Exceed The Limit, To Add New Ceiling"))

    @api.constrains('From', 'To', 'zakat_pre', 'financial_pre', 'In', 'give', 'zakat_amount', 'financial_amount')
    def check_fields(self):
        """
        Check if field have zero value or less than zero
        :return: raise exception
        """
        if self.From:
            if self.From <= 0:
                raise exceptions.ValidationError(_('From Can Not Be Zero or Less'))
        if self.To:
            if self.To <= 0:
                raise exceptions.ValidationError(_('To Can Not Be Zero or Less'))
        if self.zakat_pre:
            if self.zakat_pre < 0.0:
                raise exceptions.ValidationError(_('Zakat Percentage Can not Be Less Than zero'))
        if self.financial_pre:
            if self.financial_pre < 0.0:
                raise exceptions.ValidationError(_('Financial Percentage Can not Be Less Than zero'))
        if self.In <= 0 and self.greater == 'yes' and self.ratification_id.type != 'at':
            raise exceptions.ValidationError(_('In Can Not Be Zero or Less'))
        if self.give <= 0 and self.greater == 'yes' and self.ratification_id.type != 'at':
            raise exceptions.ValidationError(_('Give Can Not Be Zero or Less'))
        if self.give > self.In and self.greater == 'yes' and self.ratification_id.type != 'at':
            raise exceptions.ValidationError(_('Give Cannot  Be Greater Than In Value'))
        if self.zakat_amount:
            if self.zakat_amount > self.To:
                raise exceptions.ValidationError(_("Zakat Amount Cannot Be More Than To"))
        if self.financial_amount:
            if self.financial_amount > self.To:
                raise exceptions.ValidationError(_("Financial Amount Cannot Be More Than To"))
        if self.zakat_amount:
            if self.zakat_amount <= 0:
                raise exceptions.ValidationError(_("Zakat Amount Cannot Be Zero or Less"))
        if self.financial_amount:
            if self.financial_amount <= 0:
                raise exceptions.ValidationError(_("Financial Amount Cannot Be Zero or Less "))
        if self.zakat_pre > 100:
            raise exceptions.ValidationError(_("Zakat Percentage Cannot Be More Than 100 %"))
        if self.financial_pre > 100:
            raise exceptions.ValidationError(_("Financial Percentage Cannot Be More Than 100 %"))
        if self.zakat_pre:
            if self.zakat_pre <= 0:
                raise exceptions.ValidationError(_("Zakat Percentage Cannot Be Zero or Less"))
        if self.financial_pre:
            if self.financial_pre <= 0:
                raise exceptions.ValidationError(_("Financial Percentage Cannot Be Zero or Less"))
        if self.zakat_pre and self.financial_pre:
            if self.zakat_pre != self.financial_pre:
                raise exceptions.ValidationError(_("Zakat and Financial Percentage Should Be Equal"))


class State(models.Model):
    _name = 'zakat.country'
    _inherit = 'zakat.country'
    _sql_constraints = [
        ('name', 'unique(name)', _('The country name must not be repeated')),
        ('number', 'unique(country_number)', _('The country number must not be repeated')),
    ]
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 readonly=True, ondelete='restrict')
    name = fields.Char(string="Country Name", required=True)
    country_number = fields.Char(string="Country Number", required=True)

    @api.multi
    def copy(self, default=None):
        raise UserError(_('You cannot duplicate state record.'))

    @api.constrains('country_number', 'name')
    def fields_check(self):
        num_pattern = re.compile(r'\d', re.I | re.M)
        white_space = re.compile(r'^\s')

        if not re.match("^[0-9]*$", self.country_number.replace(" ", "")):
            raise ValidationError(_('Country Number Field must be number'))
        if self.country_number.replace(" ", "") != self.country_number:
            raise ValidationError(_('Country Number Field must be number'))
        if not re.match(
                "^[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z]+[\u0600-\u065F\u066A-\u06EF\u06FA-\u06FFa-zA-Z-_]*$",
                self.name.replace(" ", "")):
            raise ValidationError(_('Country name Field must be Literal'))

        if white_space.search(self.country_number):
            raise ValidationError(_('Country Number Field is Required (Cannot Accept White Space or symbols)'))
        if self.country_number == '0':
            raise exceptions.ValidationError(_("Country Number Cannot Be Zero"))
        if int(self.country_number) < 0:
            raise exceptions.ValidationError(_("Country Number Cannot Be Less Than Zero"))
        if len(self.country_number) >= 10:
            raise exceptions.ValidationError(_("Country Number Must Be Less Than 10 Digites"))
        if num_pattern.search(self.name):
            raise exceptions.ValidationError(_('Country Name Field Cannot Accept Numbers'))
        if not num_pattern.search(self.country_number):
            raise ValidationError(_('Country Number Field Cannot Accept Charter'))

     
    
