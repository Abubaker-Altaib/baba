# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from mx import DateTime
import time
from datetime import datetime
from openerp.osv import osv, fields, orm
from openerp.tools.translate import _
import netsvc
import openerp.addons.decimal_precision as dp


class hr_commision(osv.Model):
    _name = "hr.commision"
    _description = "Commision "

    def name_get(self, cr, uid, ids, context=None):
        return ids and [(item.id, "%s-%s-%s" % (_('Commision '), item.employee_id.name, item.report_date)) for item in self.browse(cr, uid, ids, context=context)] or []

    _columns = {
        'name': fields.char('Name'),
        'hospital': fields.char('Hospital', required=True),
        'employee_id': fields.many2one('hr.employee', "Employee", domain="[('state','!=','refuse')]"),

        'department_id': fields.related('employee_id', 'department_id', string="Department", type="many2one", relation="hr.department"),

        'company_id': fields.related('employee_id', 'company_id', string="Company", type="many2one", relation="res.company"),

        'injury_id': fields.many2one('hr.injury', string='Injury'),
        'type': fields.selection([('in_service', 'In Service'), ('out_service', 'Out Service')],
                                 'Type'),
        'patient_state': fields.many2one('patient.state', "Patient State"),
        'date': fields.date("Date"),
        'report_date': fields.date("Report Date"),
        'description': fields.text('Description'),
        'associate': fields.text("Associate Information", size=15),
        'station': fields.many2one('hr.mission.category', 'Station'),
        'degree': fields.related('employee_id', 'degree_id', string="Degree", type="many2one", relation="hr.salary.degree"),
        'address_home_id': fields.related('employee_id', 'address_home_id', string="Home Address", type="many2one", relation="res.partner"),
        'work_phone': fields.related('employee_id', 'work_phone', string="Work Phone", type="char"),
        'recipient_name': fields.char('recipient Name', size=64, readonly=False),
        'invoice_no': fields.integer("Invoice No", required=True),
        'treatment_amount': fields.float("Treatment Amount", digits=(18, 2)),
        'acc_number': fields.many2one('account.voucher', "Accounting Number", readonly=True),
        'transfer': fields.boolean('Transfered', readonly=True),
        'move_order_id': fields.many2one('hr.move.order', string="Move Order", domain=[('commision_move_id', '=', False), ('type', '=', 'commision')]),
        'move_order_line_id': fields.many2one('hr.move.order.line', string="Move Order", domain=[('commision_id', '=', False), ('type', '=', 'commision')]),
        'state': fields.selection([('draft', 'Draft'), ('refuse', 'Refused'), ('validate3', 'Approved'), ('cancel', 'Cancelled')],
                                  'State', readonly=True),
    }

    def _check_date(self, cr, uid, ids, context=None):
        current_date = time.strftime('%Y-%m-%d')
        current_date = datetime.strptime(
            current_date, '%Y-%m-%d')

        for act in self.browse(cr, uid, ids, context):
            if datetime.strptime(act.report_date, "%Y-%m-%d") > current_date:
                raise osv.except_osv(_(''), _("Report date can not be after current date"))
        return True

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.hospital and (len(rec.hospital.replace(' ','')) <= 0):
                raise osv.except_osv(_('ValidateError'), _("hospital must not be spaces"))
        return True

    _constraints = [
        (_check_date, _(''), ['report_date']), 
        (_check_spaces, '', ['hospital']),      
    ]

    
   


    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context):
            if rec.state != 'draft':
                raise osv.except_osv(_('ValidateError'), _("this record is must be in draft state"))
            if rec.injury_id:
                raise osv.except_osv(_('ValidateError'), _("this record is linked or ther record"))
        super(hr_commision, self).unlink(cr, uid, ids, context=context)

    def create_move_order(self, cr, uid, ids, context={}):
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hr_custom_military', 'hr_move_order_with_footer')
        res = {
                    'name': _('Move Order'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id' : view_id ,
                    'res_model': 'hr.move.order',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }
        for rec in self.browse(cr, uid, ids, context):
            if not rec.move_order_id :
                data = {
                    'default_move_order_line_ids': [[0 , 0 , {'employee_id' : rec.employee_id.id ,'commision_id' : rec.id , 'type' : 'commision' , 'date' : rec.date}]],
                    'default_source': rec.department_id and rec.department_id.id or False,
                    #'default_destination': rec.hospital,
                    'commision_id': rec.id,
                    'default_type': 'commision',
                    'default_move_date': time.strftime('%Y-%m-%d'),
                    'default_out_source': True,
                }
                res['context'] = data
            else :
                res['res_id'] = rec.move_order_id.id
        return res

    def create(self, cr, uid, vals, context=None):
        """
        Method thats overwrite the create method and naming the commision by adding its sequence to the name.

        @param vals: Values that have been entered
        @return: super create method
        """
        if vals.get('employee_id'):
            employee = self.pool.get('hr.employee').browse(
                cr, uid, vals.get('employee_id'), context=context)
            vals.update({'name': self.pool.get('ir.sequence').get(
                cr, uid, 'hr.commision') + '/' + employee.name})
        return super(hr_commision, self).create(cr, uid, vals, context=context)

    def _default_company(self, cr, uid, context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id

        return company

    _defaults = {
        'date': lambda * a: time.strftime('%Y-%m-%d'),
        'company_id': _default_company,
        'state': 'draft',
    }

    def custom_validate(self, cr, uid, ids, context={}):
        """
        Workflow method that changes the state to 'validate3'.

        @return: Boolean True
        """
        vals = {'state': 'validate3'}
        for rec in self.browse(cr , uid , ids):
            if rec.move_order_line_id:
                self.pool.get('hr.move.order.line').write(cr , uid , [rec.move_order_line_id.id] , {'commision_id' : ids[0]})
                vals['move_order_id'] = rec.move_order_line_id.move_order_id.id
        return self.write(cr, uid, ids, vals, context=context)

    def refuse(self, cr, uid, ids, context={}):
        """
        Mehtod that sets the state to draft.

        @return: Boolean True
        """
        for rec in self.browse(cr,uid,ids,context=context):
            if rec.acc_number :
                    if rec.acc_number.state == 'draft' :
                        self.pool.get('account.voucher').unlink(cr,uid,[rec.acc_number.id])
                    elif rec.acc_number.state == 'cancel' :
                        self.write(cr,uid,ids,{'acc_number':False, 'transfer': False})
                    else : 
                        raise osv.except_osv(_('warning') , _('There is a voucher releted to this record, you must cancel it before set the record to draft'))
            self.write(cr, uid, [rec.id], {'state': 'refuse'}, context=context)
        return True

    def set_to_draft(self, cr, uid, ids, context={}):
        """
        Workflow method that changes the state to 'draft'.

        @return: Boolean True
        """
        for rec in self.browse(cr,uid,ids,context=context):
            if rec.move_order_id:
                    if rec.move_order_id.state == 'draft':
                        self.pool.get('hr.move.order').unlink(cr,uid,[rec.move_order_id.id])
                    else:
                        raise osv.except_osv(_('warning') , _('There is a Confirmed Move Order releted to this record, you must delete it before set the record to draft'))
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

    def on_change_injury_id(self, cr, uid, ids, injury_id, context={}):
        res = {
            'values': {}
        }

        if not injury_id:
            return res

        injury_obj = self.pool.get('hr.injury')
        data = injury_obj.read(cr, uid, injury_id, context={})
        return res

    def transfer_rec(self, cr, uid, ids, context={}):
        """
        Method that transfers employee injury from injury form to acounting voucher.

        @return: dictionary of action to close wizard
        """
        if not context:
            context = {}
        emp_injury_obj = self.pool.get('hr.commision')
        emp_injury_id = ids[0]
        injury = emp_injury_obj.browse(cr, uid, emp_injury_id, context=context)
        data = self.browse(cr, uid, ids[0], context=context)
        hr_setting = self.pool.get('hr.config.settings')
        config_ids = hr_setting.search(cr, uid, [])
        config_browse = hr_setting.browse(cr, uid, config_ids)
        lines = []
        date = time.strftime('%Y-%m-%d')
        reference = 'HR/Employee Commision/ ' + " / " + str(injury.report_date)
        if not injury.acc_number:
            if injury.treatment_amount > 0.0:
                if config_browse[0].hr_journal_id and injury.department_id.analytic_account_id and config_browse[0].treatment_account_id:
                    treatment_dict = {
                        'account_id': config_browse[0].treatment_account_id.id, 'amount': injury.treatment_amount, }
                    lines.append(treatment_dict)
                    voucher = self.pool.get('payroll').create_payment(
                        cr, uid, ids, {'reference': reference, 'lines': lines}, context=context)
                    emp_injury_obj.write(cr, uid, [emp_injury_id], {
                        'acc_number': voucher, 'transfer': True, }, context=context)
                else:
                    raise osv.except_osv(_('ERROR'), _(
                        'Please enter account,journal and analytic account'))
            else:
                raise osv.except_osv(_('ERROR'), _(
                    'Please enter amount for treatment'))
        else:
            raise osv.except_osv(_('ERROR'), _(
                'the amount already transfered'))

        return True

#----------------------------------------
# patient state types
#----------------------------------------


class patient_state_type(osv.Model):
    _name = 'patient.state'
    _columns = {
        'code': fields.char('Code', size=64),
        'name': fields.char('Name', size=64, required=True),
        'commision' : fields.one2many('hr.commision', 'patient_state', 'Commision')
    }

    def _check_spaces(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.name and (len(rec.name.replace(' ','')) <= 0):
                raise osv.except_osv(_('ValidateError'), _("name must not be spaces"))
            if rec.code and (len(rec.code.replace(' ','')) <= 0):
                raise osv.except_osv(_('ValidateError'), _("code must not be spaces"))
            if self.search(cr, uid, [('name','=',rec.name),('id','!=',rec.id)],  context=context):
                raise osv.except_osv(_('ValidateError'), _("you can not create same code !"))
            if self.search(cr, uid, [('code','=',rec.code),('id','!=',rec.id)],  context=context):
                raise osv.except_osv(_('ValidateError'), _("you can not create same code !"))
        return True
    _constraints = [
        (_check_spaces, '', ['code','name'])
    ]

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context):
            if rec.commision:
                raise osv.except_osv(_('ValidateError'), _("this record is linked or ther record"))
        super(patient_state_type, self).unlink(cr, uid, ids, context=context)

    _sql_constraints = [
        ('name_uniqe', 'unique(code)', 'you can not create same code !')
    ]


class hr_injury(osv.Model):
    _name = "hr.injury"
    _inherit = "hr.injury"
    _description = "Injury "
    _columns = {
        'name': fields.many2one('hr.employee', "Employee"),
        'commision_id': fields.many2one('hr.commision', "Commision"), 
        'manager_id' : fields.many2one('hr.employee' , 'Manger') ,
        'member_ids' : fields.many2many('hr.employee' , 'hr_injury_members',string='Memebers') ,
        'injury_place' : fields.char('Injury Place') ,
        'decision' : fields.char('Decision') , 
        'ref' : fields.char('Opreation Reference') , 
        'ref_date' : fields.date('Reference Date'),
        }

    _defaults = {
        'type': 'compensation',
    }

    def _check_date(self, cr, uid, ids, context=None):
        current_date = time.strftime('%Y-%m-%d %H:%M:%S')
        current_date = datetime.strptime(
            current_date, '%Y-%m-%d %H:%M:%S')

        for act in self.browse(cr, uid, ids, context):
            if datetime.strptime(act.injury_date, "%Y-%m-%d %H:%M:%S") > current_date:
                raise osv.except_osv(_(''), _("Injury date can not be after current date"))
            if datetime.strptime(act.inability_date, "%Y-%m-%d %H:%M:%S") > current_date:
                raise osv.except_osv(_(''), _("Inability date can not be after current date"))
        return True

    _constraints = [
        (_check_date, _(''), ['injury_date','inability_date']),        
    ]

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context):
            if rec.state != 'draft':
                raise osv.except_osv(_('ValidateError'), _("this record is must be in draft state"))
            if rec.commision_id:
                raise osv.except_osv(_('ValidateError'), _("this record is linked or ther record"))
        super(hr_injury, self).unlink(cr, uid, ids, context=context)
    def refuse(self, cr, uid, ids, context={}):
        """
        Mehtod that sets the state to draft.

        @return: Boolean True
        """
        for rec in self.browse(cr,uid,ids,context=context):
            if rec.inability_acc_number :
                    if rec.inability_acc_number.state == 'draft' :
                        self.pool.get('account.voucher').unlink(cr,uid,[rec.inability_acc_number.id])
                    elif rec.inability_acc_number.state == 'cancel' :
                        self.write(cr,uid,ids,{'inability_acc_number':False, 'compensation_transfer': False})
                    else : 
                        raise osv.except_osv(_('warning') , _('There is a voucher releted to this record, you must cancel it before set the record to draft'))
            self.write(cr, uid, [rec.id], {'state': 'refuse'}, context=context)
        return True


    def name_get(self, cr, uid, ids, context=None):
        return ids and [(item.id, "%s-%s-%s" % (_('Injury '), item.name.name, item.injury_date.split(' ')[0])) for item in self.browse(cr, uid, ids, context=context)] or []

    def custom_validate(self, cr, uid, ids, context={}):
        """
        Workflow method that changes the state to 'validate3'.

        @return: Boolean True
        """
        self.compute_compensation(cr, uid, ids, context={})
        return self.write(cr, uid, ids, {'state': 'validate3'}, context=context)

    def transfer_rec(self, cr, uid, ids, context={}):
        """
        Method that transfers employee injury from injury form to acounting voucher.

        @return: dictionary of action to close wizard
        """

        if not context:
            context = {}
        emp_injury_obj = self.pool.get('hr.injury')
        emp_injury_id = ids[0]
        injury = emp_injury_obj.browse(cr, uid, emp_injury_id, context=context)
        hr_setting = self.pool.get('hr.config.settings')
        config_ids = hr_setting.search(cr, uid, [])
        config_browse = hr_setting.browse(cr, uid, config_ids)
        lines = []
        date = time.strftime('%Y-%m-%d')
        reference = 'HR/Employee Injury/ ' + " / " + str(injury.injury_date)

        if not injury.inability_acc_number:
            if injury.inability_amount > 0.0:
                try:
                    if config_browse[0].hr_journal_id and injury.department_id.analytic_account_id and config_browse[0].treatment_account_id:
                        compensation_dict = {
                            'account_id': config_browse[0].treatment_account_id.id, 'amount': injury.inability_amount, }
                        lines.append(compensation_dict)
                        voucher = self.pool.get('payroll').create_payment(
                            cr, uid, ids, {'reference': reference, 'lines': lines}, context=context)
                        emp_injury_obj.write(cr, uid, [emp_injury_id], {
                            'inability_acc_number': voucher, 'compensation_transfer': True, }, context=context)
                    else:
                        raise osv.except_osv(_('ERROR'), _(
                            'Please enter account,journal and analytic account'))
                except:
                    raise osv.except_osv(_('ERROR'), _(
                        'Please enter account,journal and analytic account'))
            else:
                raise osv.except_osv(_('ERROR'), _(
                    'Please enter amount for inability amount'))
        else:
            raise osv.except_osv(_('ERROR'), _(
                'the amount already transfered'))

        return True
