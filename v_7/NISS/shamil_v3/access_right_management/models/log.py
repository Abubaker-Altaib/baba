# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.osv.osv import object_proxy
from openerp.tools.translate import _
from openerp import pooler
import time
from openerp import tools
from openerp import SUPERUSER_ID

def create_log(self, cr, uid, res_id, model, old_vals, new_vals, fields, method, context={}):
    """
    """
    log_obj = self.pool.get('access.right.log')
    log_line_obj = self.pool.get('access.right.log.line')
    log_line_list = []
    resource_pool = self.pool.get(model)
    pool = self.pool
    field_pool = self.pool.get('ir.model.fields')
    lang = 'lang' in context and context['lang'] or False

    object_id = self.pool.get('ir.model').search(cr, SUPERUSER_ID, [('model','=',self._name.decode('utf-8'))])
    if method == 'unlink':
        name = context['rec_name']
    else:
        name = resource_pool.name_get(cr, uid, [res_id])[0][1]

    name = translate_name_fn(self, cr, uid, name, context)
    method_name = method
    if lang == 'ar_SY':
        method_name = (method == 'write' and u'تعديل') or (method == 'unlink' and u'حذف') or (method == 'create' and u'انشاء') or ''
    log_vals = {
        'name': name,
        'object_id': object_id and object_id[0] or False,
        'user_id': uid,
        'method': method_name,
        'res_id': res_id,
    }
    log_id = log_obj.create(cr, SUPERUSER_ID, log_vals)

    for field in fields:
        if not (field in resource_pool._all_columns.keys()):
            continue
        field_id = field_pool.search(cr, uid, [('name', '=', field), ('model_id', 'in', [object_id])])
        if field_id :
            field_obj = (resource_pool._all_columns.get(field)).column
            old_text = ''
            new_text = ''
            if method == 'write':
                #old_text = get_value_text(self, cr, SUPERUSER_ID, pool, resource_pool, method, field, old_vals[1][field])
                #new_text = get_value_text(self, cr, SUPERUSER_ID, pool, resource_pool, method, field, new_vals[0][field])
                old_text = get_value_text(self, cr, SUPERUSER_ID, pool, resource_pool, method, field, old_vals[field], context)
                new_text = get_value_text(self, cr, SUPERUSER_ID, pool, resource_pool, method, field, new_vals[field], context)
            if method == 'create':
                new_text = get_value_text(self, cr, SUPERUSER_ID, pool, resource_pool, method, field, new_vals[field], context)

            if method == 'unlink':
                old_text = get_value_text(self, cr, SUPERUSER_ID, pool, resource_pool, method, field, old_vals[field], context)
            
            field_name = translate_name_fn(self, cr, uid, field_obj.string, context)
            new_text = new_text and translate_name_fn(self, cr, uid, new_text, context) or new_text
            old_text = old_text and translate_name_fn(self, cr, uid, old_text, context) or old_text


            log_line_vals = {
                'field_id': field_id and field_id[0] or False,
                'log_id': log_id,
                'new_value_text': new_text and new_text or '' ,
                'old_value_text': old_text and old_text or '' ,
                'field_description': field_name,

            }
            log_line_obj.create(cr, SUPERUSER_ID, log_line_vals)


def get_value_text(self, cr, uid, pool, resource_pool, method, field, value, context={}):
        """
        Gets textual values for the fields.
            If the field is a many2one, it returns the name.
            If it's a one2many or a many2many, it returns a list of name.
            In other cases, it just returns the value.
        :param cr: the current row, from the database cursor,
        :param uid: the current user’s ID for security checks,
        :param pool: current db's pooler object.
        :param resource_pool: pooler object of the model which values are being changed.
        :param field: for which the text value is to be returned.
        :param value: value of the field.
        :param recursive: True or False, True will repeat the process recursively
        :return: string value or a list of values(for O2M/M2M)
        """
        field_obj = (resource_pool._all_columns.get(field)).column
        if field_obj._type in ('one2many','many2many'):
            data = pool.get(field_obj._obj).name_get(cr, uid, value, context)
            #return the modifications on x2many fields as a list of names
            res = u''
            for x in data:
                res += u' ' + x[1]
                if x != data[len(data)-1]:
                    res += u',' + u' '
            #res = map(lambda x: x[1], data)
        elif field_obj._type == 'many2one':
            #return the modifications on a many2one field as its value returned by name_get()
            res = value and value[1] or value
        else:
            res = value
        return res


def translate_name_fn(self, cr, uid, name, context={}):
    """
    """
    translation_obj = self.pool.get('ir.translation')
    lang = 'lang' in context and context['lang'] or False

    translate_name = name
    if name and lang == 'ar_SY':
        translation_ids = translation_obj.search(
            cr, SUPERUSER_ID, [('src','=', name), ('lang', '=', 'ar_SY')])
        translation_recs = translation_obj.read(
            cr, SUPERUSER_ID, translation_ids, [])
        translate_name = translation_recs and translation_recs[0]['value'] or name

    return translate_name


class access_right_log(osv.osv):
    """
    For Access Right Log
    """
    _name = 'access.right.log'
    _description = "Access Right Log"

    def _name_get_resname(self, cr, uid, ids, *args):
        data = {}
        for resname in self.browse(cr, uid, ids,[]):
            model_object = resname.object_id
            res_id = resname.res_id
            if model_object and res_id:
                model_pool = self.pool.get(model_object.model)
                res = model_pool.read(cr, uid, res_id, ['name'])
                data[resname.id] = res['name']
            else:
                 data[resname.id] = False
        return data

    _columns = {
        "name": fields.char("Resource Name",size=64),
        "object_id": fields.many2one('ir.model', 'Object'),
        "user_id": fields.many2one('res.users', 'User'),
        "method": fields.char("Method", size=64),
        "timestamp": fields.datetime("Date"),
        "res_id": fields.integer('Resource Id'),
        "line_ids": fields.one2many('access.right.log.line', 'log_id', 'Log lines'),
    }

    _defaults = {
        "timestamp": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S")
    }
    _order = "timestamp desc"

class access_right_log_line(osv.osv):
    """
    Access Right Log Line.
    """
    _name = 'access.right.log.line'
    _description = "Log Line"
    _columns = {
          'field_id': fields.many2one('ir.model.fields', 'Fields', required=True),
          'log_id': fields.many2one('access.right.log', 'Log'),
          'log': fields.integer("Log ID"),
          'old_value': fields.text("Old Value"),
          'new_value': fields.text("New Value"),
          'old_value_text': fields.text('Old value Text'),
          'new_value_text': fields.text('New value Text'),
          'field_description': fields.char('Field Description', size=64),
        }



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

