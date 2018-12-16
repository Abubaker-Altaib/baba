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


class hr_commite(osv.Model):
    _name = "hr.committe"
    _inherit = ['mail.thread']
    _description = "hr_committe "

    types_list = [('hr.movements.department', 'movements department'),
                  ('hr.movements.job', 'movements job'),
                  ('hr.movements.degree',
                   'movements degree'),
                  ('hr.movements.bonus', 'movements bonus')]
    
    def copy(self, cr, uid, id, default=None, context=None):
        """
        @return: super duplicate() method
        """
        raise osv.except_osv(_('Invalid Action Error'), _('can not duplicate a record linked'))
        return super(hr_commite, self).copy(cr, uid, id, default, context)

    def unlink(self, cr, uid, ids, context=None):
        """
        @return: super unlink() method
        """
        raise osv.except_osv(_('Invalid Action Error'), _('can not delete a record linked'))
        return super(hr_commite, self).unlink(cr, uid, ids, context=context)


    def name_get(self, cr, uid, ids, context=None):
        types_list = self.types_list
        types_list = {i[0]: i[1] for i in types_list}
        # get the translation of type field
        if context and 'lang' in context:
            translation_obj = self.pool.get('ir.translation')
            translation_ids = translation_obj.search(
                cr, uid, [('name', '=', 'hr.committe,details_type'), ('lang', '=', context['lang'])], context=context)
            translation_recs = translation_obj.read(
                cr, uid, translation_ids, [], context=context)
            
            tran_types_list = {x['source']:x['value'] for x in translation_recs}

            for rec in types_list:
                try:
                    types_list[rec] = tran_types_list[types_list[rec]]
                except:
                    pass

        return ids and [(item.id, "%s-%s" % (types_list[item.details_type], item.date)) for item in self.browse(cr, uid, ids, context=context)] or []

    def confirm(self,  cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            for line in rec.committe_details_ids_final:
                if line.state != 'draft':
                    continue
                line.confirm()
        return self.write(cr, uid, ids, {'state': 'confirmed'})

    def cancel(self,  cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            for line in rec.committe_details_ids_final:
                if line.state == 'cancel':
                    continue
                line.cancel()
        return self.write(cr, uid, ids, {'state': 'canceled'})

    def draft(self,  cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            for line in rec.committe_details_ids_final:
                if line.state == 'draft':
                    continue
                line.draft()
        return self.write(cr, uid, ids, {'state': 'draft'})

    def link(self,  cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            for line in rec.committe_details_ids_final:
                if line.state == 'draft':
                    continue
                line.link()
        return self.write(cr, uid, ids, {'state': 'draft'})
    _columns = {
        'committe_details_ids_manageral': fields.one2many('hr.committe.details', 'parent', string="Manageral Details", track_visibility="always"),
        'committe_details_ids_personal': fields.one2many('hr.committe.details', 'parent', string="Personal Details", track_visibility="always"),
        'committe_details_ids_final': fields.one2many('hr.committe.details', 'parent', string="Final Details", track_visibility="always"),
        'details_type': fields.selection(types_list, 'Type', track_visibility="always"),
        'date': fields.date('Date'),
        'company_id': fields.many2one('res.company', string='Company', ),
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('canceled', 'Canceled'), ], 'State'),
    }

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id

        return company


    _defaults = {
        'date': time.strftime('%Y-%m-%d'),
        'state': 'draft',
        'company_id' : _default_company,
    }

    def calculate(self, cr, uid, ids, context={}):
        line_obj = self.pool.get('hr.committe.details')
        for rec in self.browse(cr, uid, ids, context):
            for line in rec.committe_details_ids_manageral:
                line.write({'ferocity_months': line_obj._amount_total(cr, uid,
                                                                      [line.id], 'ferocity_months', {}, context=context)[line.id]})
                line.write({'operations_months': line_obj._amount_total(cr, uid,
                                                                        [line.id], 'operations_months', {}, context=context)[line.id]})
                line.write({'ferocity_months_degree': line_obj._amount_total(cr, uid,
                                                                             [line.id], 'ferocity_months_degree', {}, context=context)[line.id]})
                line.write({'operations_months_degree': line_obj._amount_total(cr, uid,
                                                                               [line.id], 'operations_months_degree', {}, context=context)[line.id]})
                line.write({'total_training': line_obj._sum_total_emp(cr, uid,
                                                                      [line.id], 'total_training', {}, context=context)[line.id]})
                line.write({'total_certificates': line_obj._sum_total_emp(cr, uid,
                                                                          [line.id], 'total_certificates', {}, context=context)[line.id]})

                line.write({'sum1': line_obj._sum_total(cr, uid,
                                                        [line.id], 'sum1', {}, context=context)[line.id]})

                line.write({'sum2': line_obj._sum_total(cr, uid,
                                                        [line.id], 'sum2', {}, context=context)[line.id]})

                line.write({'sum3': line_obj._sum_total(cr, uid,
                                                        [line.id], 'sum3', {}, context=context)[line.id]})
        return True


class hr_commite_details(osv.Model):
    _name = "hr.committe.details"
    def unlink(self, cr, uid, ids, context=None):
        """
        @return: super unlink() method
        """
        raise osv.except_osv(_('Invalid Action Error'), _('can not delete a record linked'))
        return super(hr_commite_details, self).unlink(cr, uid, ids, context=context)
    def _amount_total(self, cr, uid, ids, name, args, context=None):
        result = {}
        mission_obj = self.pool.get('hr.employee.mission')
        mission_line_obj = self.pool.get('hr.employee.mission.line')
        ferocity_months_factor = 4.0
        operations_months_factor = 12.0

        for id in ids:
            result[id] = 0.0
            ferocity = operations = 0.0
            data = self.browse(cr, uid, id, context=context)
            if data.employee_id:
                emp_missions = mission_line_obj.search(
                    cr, uid, [('employee_id', '=', data.employee_id.id)])
                emp_missions = mission_line_obj.browse(cr, uid, emp_missions)
                for mission in emp_missions:
                    if mission.emp_mission_id.state != 'approved':
                        continue
                    if mission.emp_mission_id.service_type.ferocity:
                        ferocity += mission.days
                    else:
                        operations += mission.days

                ferocity_months_factor = data.reference_object.company_id.ferocity_months_factor or ferocity_months_factor
                operations_months_factor = data.reference_object.company_id.operations_months_factor or operations_months_factor
            if name == 'ferocity_months':
                result[id] = ferocity / 30
            if name == 'operations_months':
                result[id] = operations / 30
            if name == 'ferocity_months_degree':
                result[id] = ferocity / 30 / ferocity_months_factor
            if name == 'operations_months_degree':
                result[id] = operations / 30 / operations_months_factor

        return result

    def _sum_total(self, cr, uid, ids, name, args, context=None):
        result = {}
        mission_obj = self.pool.get('hr.employee.mission')
        mission_line_obj = self.pool.get('hr.employee.mission.line')
        for id in ids:
            result[id] = 0.0
            sum1 = sum2 = 0.0
            data = self.browse(cr, uid, id)
            sum1 += data.degree_value
            sum1 += self._amount_total(cr, uid,
                                       [id], 'ferocity_months_degree', args, context=context)[id]
            sum1 += self._amount_total(
                cr, uid, [id], 'operations_months_degree', args, context=context)[id]
            sum1 += data.total_service_years
            sum1 += self._sum_total_emp(cr, uid,
                                        [id], 'total_training', args, context=context)[id]
            sum1 += self._sum_total_emp(cr, uid,
                                        [id], 'total_certificates', args, context=context)[id]

            sum2 = data.general_look + data.personality + \
                data.intelligence + data.express + data.self_confidence

            if name == 'sum1':
                result[id] = sum1
            if name == 'sum2':
                result[id] = sum2
            if name == 'sum3':
                result[id] = sum1 + sum2

        return result

    def _sum_total_emp(self, cr, uid, ids, name, args, context=None):
        result = {}
        employee_obj = self.pool.get('hr.employee')
        for id in ids:
            result[id] = 0.0
            training = certificates = 0.0
            data = self.browse(cr, uid, id, [])
            if data.employee_id:
                emp = employee_obj.browse(cr, uid, data.employee_id.id)
                for training_rec in emp.military_training_id:
                    training += training_rec.type and training_rec.type.degree_value or 0.0

                for cert in emp.qualification_ids:
                    if cert.state != 'approved':
                        continue
                    certificates += cert.emp_qual_id and cert.emp_qual_id.degree_value or 0.0
            if name == 'total_training':
                result[id] = training
            if name == 'total_certificates':
                result[id] = certificates

        return result

    def open_record(self,  cr, uid, ids, context=None):
        rec = self.browse(cr, uid, ids)[0]

        #form_view_id = rec.form_view_id and rec.form_view_id.id or False

        return {
            'type': 'ir.actions.act_window',
            'res_model': rec.reference_object._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': rec.reference_object.id,
            #'view_id': form_view_id,
            'target': 'new',
        }

    def confirm(self,  cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.reference_object.state == 'approved':
                continue
            rec.reference_object.write({'approve_date':rec.parent.date}) 
            rec.reference_object.do_approve()
        return self.write(cr, uid, ids, {'state': 'confirmed'})

    def cancel(self,  cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            rec.reference_object.write(
                {'committe_id': False, 'committe_details_id': False})
        return self.write(cr, uid, ids, {'state': 'canceled'})

    def draft(self,  cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.reference_object.state == 'draft':
                continue 
            rec.reference_object.set_to_draft()
        return self.write(cr, uid, ids, {'state': 'draft'})

    def link(self,  cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.reference_object.state != 'draft':
                raise orm.except_orm(_('Warning'), _(
                    "Connot Edit this record because it is Approved"))
            rec.reference_object.write(
                {'committe_id': rec.parent.id, 'committe_details_id': rec.id})
        return self.write(cr, uid, ids, {'state': 'draft'})

    Reference_selection = [('hr.movements.department', 'movements department'),
                           ('hr.movements.job', 'movements job'),
                           ('hr.movements.degree', 'movements degree'),
                           ('hr.movements.bonus', 'movements bonus'), ]

    _columns = {
        'parent': fields.many2one('hr.committe', string="Committe"),
        'reference_object': fields.reference('Reference', selection=Reference_selection, size=128),
        'employee_id': fields.many2one('hr.employee', string="employee"),
        'emp_code': fields.related('employee_id', 'emp_code', string="Code", type="char"),
        'degree': fields.related('employee_id', 'degree_id', string="Degree", type="many2one", relation="hr.salary.degree"),
        'degree_value': fields.related('employee_id', 'degree_value', string="Degree Value", type="float"),
        'total_service_years': fields.related('employee_id', 'total_service_years', string="Total Servicee Years", type="float"),

        'ferocity_months': fields.function(_amount_total, string='Ferocity Months', type='float',
                                           store=True,),

        'operations_months': fields.function(_amount_total, string='Operations Months', type='float',
                                             store=True,),

        'ferocity_months_degree': fields.function(_amount_total, string='Ferocity Months Degree', type='float',
                                                  store=True,),

        'operations_months_degree': fields.function(_amount_total, string='Operations Months Degree', type='float',
                                                    store=True,),

        'total_training': fields.function(_sum_total_emp, type='float', string='Training Degrees', store=True,),
        'total_certificates': fields.function(_sum_total_emp, type='float', string='Certificates Degrees', store=True,),

        'general_look': fields.float('General Look'),
        'personality': fields.float('Personality'),
        'intelligence': fields.float('Intelligence'),
        'self_confidence': fields.float('Self Confidence'),
        'express': fields.float('Express'),

        'midecal': fields.char('Midecal'),
        'self_securing': fields.char('Self Securing'),
        'notes': fields.char('Notes'),

        'sum1': fields.function(_sum_total, type='float', string='sum', store=True,),
        'sum2': fields.function(_sum_total, type='float', string='sum', store=True,),
        'sum3': fields.function(_sum_total, type='float', string='sum', store=True,),
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('canceled', 'Canceled'), ], 'State'),
    }
    _defaults = {
        'state': 'draft',
    }


class employee_movements_department(osv.Model):
    _name = "hr.movements.department"
    _inherit = "hr.movements.department"
    _columns = {
        'committe_id': fields.many2one('hr.committe', string="Committe"),
        'committe_details_id': fields.many2one('hr.committe.details', string="Committe Details"),
        'is_committe': fields.boolean("Have Committe"),
    }

    def unlink(self, cr, uid, ids, context=None):
        """
        @return: super unlink() method
        """
        payenrich = self.read(cr, uid, ids, ['state','committe_id'], context=context)
        for s in payenrich:
            if s['state'] != 'draft':
                raise osv.except_osv(_('Invalid Action Error'), _('Can not delete a record not in Draft state'))
            if s['committe_id']:
                raise osv.except_osv(_('Invalid Action Error'), _('can not delete a record linked with a committe'))
        return super(employee_movements_department, self).unlink(cr, uid, ids, context=context)




class employee_movements_job(osv.Model):
    _name = "hr.movements.job"
    _inherit = "hr.movements.job"
    _columns = {
        'committe_id': fields.many2one('hr.committe', string="Committe"),
        'committe_details_id': fields.many2one('hr.committe.details', string="Committe Details"),
        'is_committe': fields.boolean("Have Committe"),
    }

    def unlink(self, cr, uid, ids, context=None):
        """
        @return: super unlink() method
        """
        payenrich = self.read(cr, uid, ids, ['state','committe_id'], context=context)
        for s in payenrich:
            if s['state'] != 'draft':
                raise osv.except_osv(_('Invalid Action Error'), _('Can not delete a record not in Draft state'))
            if s['committe_id']:
                raise osv.except_osv(_('Invalid Action Error'), _('can not delete a record linked with a committe'))
        return super(employee_movements_job, self).unlink(cr, uid, ids, context=context)


class employee_movements_promotion(osv.Model):
    _name = "hr.movements.degree"
    _inherit = "hr.movements.degree"
    _columns = {
        'committe_id': fields.many2one('hr.committe', string="Committe"),
        'committe_details_id': fields.many2one('hr.committe.details', string="Committe Details"),
        'is_committe': fields.boolean("Have Committe"),
    }

    def unlink(self, cr, uid, ids, context=None):
        """
        @return: super unlink() method
        """
        payenrich = self.read(cr, uid, ids, ['state','committe_id'], context=context)
        for s in payenrich:
            if s['state'] != 'draft':
                raise osv.except_osv(_('Invalid Action Error'), _('Can not delete a record not in Draft state'))
            if s['committe_id']:
                raise osv.except_osv(_('Invalid Action Error'), _('can not delete a record linked with a committe'))
        return super(employee_movements_promotion, self).unlink(cr, uid, ids, context=context)


class employee_movements_bonus(osv.Model):
    _name = "hr.movements.bonus"
    _inherit = "hr.movements.bonus"
    _columns = {
        'committe_id': fields.many2one('hr.committe', string="Committe"),
        'committe_details_id': fields.many2one('hr.committe.details', string="Committe Details"),
        'is_committe': fields.boolean("Have Committe"),
    }
    def unlink(self, cr, uid, ids, context=None):
        """
        @return: super unlink() method
        """
        payenrich = self.read(cr, uid, ids, ['state','committe_id'], context=context)
        for s in payenrich:
            if s['state'] != 'draft':
                raise osv.except_osv(_('Invalid Action Error'), _('Can not delete a record not in Draft state'))
            if s['committe_id']:
                raise osv.except_osv(_('Invalid Action Error'), _('can not delete a record linked with a committe'))
        return super(employee_movements_bonus, self).unlink(cr, uid, ids, context=context)


class hr_salary_degree(osv.Model):
    _name = "hr.salary.degree"
    _inherit = "hr.salary.degree"
    _columns = {
        'degree_value': fields.float('Degree Value'),
    }


class hr_employee(osv.Model):
    _name = "hr.employee"
    _inherit = "hr.employee"
    _columns = {
        'degree_value': fields.related('degree_id', 'degree_value', string="Degree Value", type="float"),
    }


class hr_qualification(osv.Model):
    _name = "hr.qualification"
    _inherit = "hr.qualification"
    _columns = {
        'degree_value': fields.float('Qualification Degree Value'),
    }


class hr_military_training_category(osv.Model):
    _name = "hr.military.training.category"
    _inherit = "hr.military.training.category"
    _columns = {
        'degree_value': fields.float('Training Degree Value'),
    }


class hr_config_settings(osv.Model):

    _inherit = 'res.company'

    _columns = {
        'ferocity_months_factor': fields.float(string='Ferocity Months Factor'),
        'operations_months_factor': fields.float(string='Operations Months Factor'),
    }


class res_company(osv.Model):

    _inherit = 'hr.config.settings'

    _columns = {
        'ferocity_months_factor': fields.float(string='Ferocity Months Factor'),
        'operations_months_factor': fields.float(string='Operations Months Factor'),
    }

    def get_default_ferocity_months_factor(self, cr, uid, fields, context=None):
        """
        return default value 
        """
        company = self.pool.get("res.users").browse(cr, uid, uid).company_id
        return {'ferocity_months_factor': company.ferocity_months_factor}
        # return {'ferocity_months_factor': 50}

    def set_default_ferocity_months_factor(self, cr, uid, ids, context=None):
        """
        this method to write value in age pension field
        return True
        """
        company_obj = self.pool.get('res.company')
        config = self.browse(cr, uid, ids[0], context)
        ferocity_months_factor = config and config.ferocity_months_factor
        company = self.pool.get("res.users").browse(cr, uid, uid).company_id
        company.write({
            'ferocity_months_factor': ferocity_months_factor})
        return True

    def get_default_operations_months_factor(self, cr, uid, fields, context=None):
        """
        return default value 
        """
        company = self.pool.get("res.users").browse(cr, uid, uid).company_id
        return {'operations_months_factor': company.operations_months_factor}
        # return {'operations_months_factor': 50}

    def set_default_operations_months_factor(self, cr, uid, ids, context=None):
        """
        this method to write value in age pension field
        return True
        """
        company_obj = self.pool.get('res.company')
        config = self.browse(cr, uid, ids[0], context)
        operations_months_factor = config and config.operations_months_factor
        company = self.pool.get("res.users").browse(cr, uid, uid).company_id
        company.write({
            'operations_months_factor': operations_months_factor})
        return True
