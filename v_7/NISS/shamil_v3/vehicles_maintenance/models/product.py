# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields, osv
from tools.translate import _
import time
import datetime

#----------------------------------------
# Class product inherit
#----------------------------------------


class product_product(osv.osv):
    """
    To manage fuel products
    """

    def write(self, cr, uid, ids, vals, context={}):
        """
        """
        super(product_product, self).write(cr, uid, ids, vals, context)
        for rec in self.browse(cr, uid, ids, context):
            if 'name' in vals:
                x = self.pool.get('product.template').write(cr, uid, [rec.product_tmpl_id.id],{'name': vals['name']},context )
                cr.execute("update product_template set name=%s where id=%s",(vals['name'],rec.product_tmpl_id.id))

        return True


    def _check_unique_insesitive(self, cr, uid, ids, context=None):
        """ 
        Check uniqueness of product name.

        @return: Boolean of True or False
        """
        name = self.browse(cr, uid, ids[0], context=context).name
        e_name = self.browse(cr, uid, ids[0], context=context).e_name

        if len(self.search(cr, uid, [('name', '=ilike', name)],  context=context)) > 1:
            raise osv.except_osv(_('Constraint Error'),
                                 _("The Name Must Be Unique!"))
        if len(self.search(cr, uid, [('e_name', '=ilike', e_name)],  context=context)) > 1:
            raise osv.except_osv(_('Constraint Error'),
                                 _("The Name Must Be Unique!"))
        return True

    def _check_cost(self, cr, uid, ids, context=None):
        """ 
        Check the value of product standard price,
        if greater than zero or not.

        @return: Boolean of True or False
        """
        count = 0
        for product in self.browse(cr, uid, ids, context=context):
            if (product.standard_price <= 0):
                message = _("The Cost Must Be Greater Than Zero!")
                count += 1
        if count > 0:
            raise osv.except_osv(_('ValidateError'), _(message))
        return True

    _inherit = "product.product"

    _columns = {
        'spare_ok': fields.boolean('Spare Product', help="Determine This Product Is Spare"),
        'spare_constraints_ids': fields.many2many('spare.constraints', 'spare_spare_constraints_rel', string='Spare Constraints'),
        'location': fields.many2one('vehicle.place', "Vehicle Place"),
        'e_name': fields.char('English Name'),
        't_number': fields.char('Tranding Number'),
        'location_place': fields.char('Place in Location'),
        'mini_amount': fields.integer('Mini Amount'),
        'max_amount': fields.integer('Max Amount'),
        'vehicle_category': fields.many2one('vehicle.category', "Vehicle Category"),
        'vehicle_category_ids': fields.many2many('vehicle.category', 'product_vehicle_cat_rel', 'product_id', 'vehicle_cat_id', string='Vehicle Category'),
    }

    def onchange_name(self, cr, uid, ids, name, context={}):
        """
        to set name without space.

        @param name: Name of product
        @return: Dictionary of values 
        """
        vals = {}
        if name:
            vals['name']=name.strip()
        return {'value':vals}

    _constraints = [
        (_check_cost, '', ['']),
        #(_check_unique_insesitive, '', [''])
    ]

#----------------------------------------
# Spare constraints
#----------------------------------------


class spare_constraints(osv.osv):
    _name = "spare.constraints"

    _columns = {
        'type': fields.selection([('months', 'Months'), ('distance', 'Distance'), ('counter', 'Counter')], 'Type'),
        'count': fields.integer('Count'),
        'constraint': fields.integer('Constraint'),
        'need_maintenance_manager_approve': fields.boolean('Need Maintenance manager approve'),
        'odometer_unit': fields.selection([('kilometers', 'Kilometers'), ('miles', 'Miles')], 'Odometer Unit', help='Unit of the odometer '),
        'spares_ids': fields.many2many('product.product', 'spare_spare_constraints_rel', string='Spares'),
        'company_id': fields.many2one('res.company','company'),
        }

    def _default_company(self,cr,uid,context=None):
        List = []
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr ,uid, uid)
        company = False
        if user.company_id:
            company = user.company_id.id
        return company

    _defaults={
        'company_id' : _default_company,
        'count':1,
        'constraint':1,
    }

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            if rec.spares_ids:
                raise osv.except_osv(
                    _(''), _("can not delete record linked with other record"))
        return super(fleet_vehicle_ownership, self).unlink(cr, uid, ids, context=context)

    def _check_ints(self, cr, uid, ids, context=None):
        """
        Check if cost is greater than zero.

        @return: boolean true of false
        """
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.count <= 0:
                raise osv.except_osv(_(''), _('The count Must Be Bigger than Zero'))
            if rec.constraint <= 0:
                raise osv.except_osv(_(''), _('The constraint Must Be Bigger than Zero'))
        return True

    _constraints = [
        (_check_ints, '', ['count', 'constraint']),
    ]
