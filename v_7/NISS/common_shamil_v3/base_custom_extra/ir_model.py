# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import logging
import re
import time
import types

import openerp
import openerp.modules.registry
from openerp import SUPERUSER_ID
from openerp import netsvc, pooler, tools
from openerp.osv import fields,osv
from openerp.osv.orm import Model
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools import config
from openerp.tools.translate import _
from openerp.osv.orm import except_orm, browse_record


class ir_model(osv.osv):

    _inherit='ir.model.data'

    def _update(self,cr, uid, model, module, values, xml_id=False, store=True, noupdate=False, mode='init', res_id=False, context=None):
        # customize _update function to skip csv file when upgrade module 

        model_obj = self.pool.get(model)
        base_config_settings_obj = self.pool.get('base.config.settings')
        if not context:
            context = {}
        # records created during module install should not display the messages of OpenChatter
        context = dict(context, install_mode=True)
        if xml_id and ('.' in xml_id):
            assert len(xml_id.split('.'))==2, _("'%s' contains too many dots. XML ids should not contain dots ! These are used to refer to other modules data, as in module.reference_id") % xml_id
            module, xml_id = xml_id.split('.')
        if (not xml_id) and (not self.doinit):
            return False
        action_id = False
        if xml_id:
            cr.execute('''SELECT imd.id, imd.res_id, md.id, imd.model
                          FROM ir_model_data imd LEFT JOIN %s md ON (imd.res_id = md.id)
                          WHERE imd.module=%%s AND imd.name=%%s''' % model_obj._table,
                          (module, xml_id))
            results = cr.fetchall()
            for imd_id2,res_id2,real_id2,real_model in results:
                if not real_id2:
                    self._get_id.clear_cache(self, uid, module, xml_id)
                    self.get_object_reference.clear_cache(self, uid, module, xml_id)
                    cr.execute('delete from ir_model_data where id=%s', (imd_id2,))
                    res_id = False
                else:
                    assert model == real_model, "External ID conflict, %s already refers to a `%s` record,"\
                        " you can't define a `%s` record with this ID." % (xml_id, real_model, model)
                    res_id,action_id = res_id2,imd_id2
        if action_id and res_id:
               if mode =='init' or (mode =='update' and  model_obj._table !='ir_model_access') :
                  model_obj.write(cr, uid, [res_id], values, context=context)
                  self.write(cr, uid, [action_id], {
                   'date_update': time.strftime('%Y-%m-%d %H:%M:%S'),
               },context=context)
        elif res_id:
            model_obj.write(cr, uid, [res_id], values, context=context)
            if xml_id:
                self.create(cr, uid, {
                    'name': xml_id,
                    'model': model,
                    'module':module,
                    'res_id':res_id,
                    'noupdate': noupdate,
                    },context=context)
                if model_obj._inherits:
                    for table in model_obj._inherits:
                        inherit_id = model_obj.browse(cr, uid,
                                res_id,context=context)[model_obj._inherits[table]]
                        self.create(cr, uid, {
                            'name': xml_id + '_' + table.replace('.', '_'),
                            'model': table,
                            'module': module,
                            'res_id': inherit_id.id,
                            'noupdate': noupdate,
                            },context=context)
        else:
            if mode=='init' or (mode=='update' and xml_id):
                res_id = model_obj.create(cr, uid, values, context=context)
                if xml_id:
                    self.create(cr, uid, {
                        'name': xml_id,
                        'model': model,
                        'module': module,
                        'res_id': res_id,
                        'noupdate': noupdate
                        },context=context)
                    if model_obj._inherits:
                        for table in model_obj._inherits:
                            inherit_id = model_obj.browse(cr, uid,
                                    res_id,context=context)[model_obj._inherits[table]]
                            self.create(cr, uid, {
                                'name': xml_id + '_' + table.replace('.', '_'),
                                'model': table,
                                'module': module,
                                'res_id': inherit_id.id,
                                'noupdate': noupdate,
                                },context=context)
        if xml_id and res_id:
               self.loads[(module, xml_id)] = (model, res_id)
               for table, inherit_field in model_obj._inherits.iteritems():
                 inherit_id = model_obj.read(cr, uid, res_id,
                        [inherit_field])[inherit_field]
                 self.loads[(module, xml_id + '_' + table.replace('.', '_'))] = (table, inherit_id)
        return res_id

class ir_model_fields(osv.osv):
    _inherit = 'ir.model.fields'

    def write(self, cr, user, ids, vals, context=None):
        updated = False
        updated_records =[]
        if vals['selection']: 
            if len(vals.keys()) <= 1:
                for record in self.browse(cr,user,ids):
                    cr.execute("UPDATE ir_model_fields SET state = 'manual' WHERE id = %s" % record.id)
                    updated = True
                    updated_records.append(record.id)
        res = super(ir_model_fields,self).write(cr, user, ids, vals, context=context)
        if updated:
            column_rename = None # if set, *one* column can be renamed here
            obj = None
            models_patch = {}    # structs of (obj, [(field, prop, change_to),..])
                                 # data to be updated on the orm model

            # static table of properties
            model_props = [ # (our-name, fields.prop, set_fn)
                ('field_description', 'string', str),
                ('required', 'required', bool),
                ('readonly', 'readonly', bool),
                ('domain', '_domain', eval),
                ('size', 'size', int),
                ('on_delete', 'ondelete', str),
                ('translate', 'translate', bool),
                ('view_load', 'view_load', bool),
                ('selectable', 'selectable', bool),
                ('select_level', 'select', int),
                ('selection', 'selection', eval),
                ]

            if vals and ids:
                checked_selection = False # need only check it once, so defer

                for item in self.browse(cr, user, ids, context=context):
                    if not (obj and obj._name == item.model):
                        obj = self.pool.get(item.model)

                    if item.state != 'manual':
                        raise except_orm(_('Error!'),
                            _('Properties of base fields cannot be altered in this manner! '
                              'Please modify them through Python code, '
                              'preferably through a custom addon!'))

                    if item.ttype == 'selection' and 'selection' in vals \
                            and not checked_selection:
                        self._check_selection(cr, user, vals['selection'], context=context)
                        checked_selection = True

                    final_name = item.name
                    if 'name' in vals and vals['name'] != item.name:
                        # We need to rename the column
                        if column_rename:
                            raise except_orm(_('Error!'), _('Can only rename one column at a time!'))
                        if vals['name'] in obj._columns:
                            raise except_orm(_('Error!'), _('Cannot rename column to %s, because that column already exists!') % vals['name'])
                        if vals.get('state', 'base') == 'manual' and not vals['name'].startswith('x_'):
                            raise except_orm(_('Error!'), _('New column name must still start with x_ , because it is a custom field!'))
                        if '\'' in vals['name'] or '"' in vals['name'] or ';' in vals['name']:
                            raise ValueError('Invalid character in column name')
                        column_rename = (obj, (obj._table, item.name, vals['name']))
                        final_name = vals['name']

                    if 'model_id' in vals and vals['model_id'] != item.model_id:
                        raise except_orm(_("Error!"), _("Changing the model of a field is forbidden!"))

                    if 'ttype' in vals and vals['ttype'] != item.ttype:
                        raise except_orm(_("Error!"), _("Changing the type of a column is not yet supported. "
                                    "Please drop it and create it again!"))

                    # We don't check the 'state', because it might come from the context
                    # (thus be set for multiple fields) and will be ignored anyway.
                    if obj:
                        models_patch.setdefault(obj._name, (obj,[]))
                        # find out which properties (per model) we need to update
                        for field_name, field_property, set_fn in model_props:
                            if field_name in vals:
                                property_value = set_fn(vals[field_name])
                                if getattr(obj._columns[item.name], field_property) != property_value:
                                    models_patch[obj._name][1].append((final_name, field_property, property_value))
                            # our dict is ready here, but no properties are changed so far

            # These shall never be written (modified)
            for column_name in ('model_id', 'model', 'state'):
                if column_name in vals:
                    del vals[column_name]

            res = super(ir_model_fields,self).write(cr, user, ids, vals, context=context)

            if column_rename:
                cr.execute('ALTER TABLE "%s" RENAME COLUMN "%s" TO "%s"' % column_rename[1])
                # This is VERY risky, but let us have this feature:
                # we want to change the key of column in obj._columns dict
                col = column_rename[0]._columns.pop(column_rename[1][1]) # take object out, w/o copy
                column_rename[0]._columns[column_rename[1][2]] = col

            if models_patch:
                # We have to update _columns of the model(s) and then call their
                # _auto_init to sync the db with the model. Hopefully, since write()
                # was called earlier, they will be in-sync before the _auto_init.
                # Anything we don't update in _columns now will be reset from
                # the model into ir.model.fields (db).
                ctx = dict(context, select=vals.get('select_level', '0'),
                           update_custom_fields=True)

                for __, patch_struct in models_patch.items():
                    obj = patch_struct[0]
                    for col_name, col_prop, val in patch_struct[1]:
                        selc = obj._columns[col_name].selection
                        if val not in obj._columns[col_name].selection :
                            for item in val:
                                selc.append(item)
                        setattr(obj._columns[col_name], col_prop, selc)

                    obj._auto_init(cr, ctx)
                    obj._auto_end(cr, ctx) # actually create FKs!
                openerp.modules.registry.RegistryManager.signal_registry_change(cr.dbname)
            for record_id in updated_records:
                cr.execute("UPDATE ir_model_fields SET state = 'base' WHERE id = %s" % record_id)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
