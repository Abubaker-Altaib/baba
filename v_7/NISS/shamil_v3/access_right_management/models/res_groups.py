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
from openerp import SUPERUSER_ID
from openerp.addons.audittrail.audittrail import audittrail_objects_proxy
from openerp import pooler
from .log import create_log


class module_category(osv.osv):
    _inherit = "ir.module.category"

    _columns = {
        'users': fields.many2many('res.users', 'res_module_cat_users_rel', 'cat_id', 'uid', 'Users'),
    }


    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        
        if context is None:
            context = {}
        
        
        if 'it_access' in context and context['it_access'] == True:
            ids = []
            args.append(('users','in',[uid]))
            ids = super(module_category, self).search(cr, uid, args, offset, limit,
            order, context=context, count=count)

        else:

            ids = super(module_category, self).search(cr, uid, args, offset, limit,
                order, context=context, count=count)

        return ids
   



class res_groups(osv.osv):
    _inherit = 'res.groups'



    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        
        if context is None:
            context = {}
        
        
        if 'it_access' in context and context['it_access'] == True:
            ids = []
            module_cat_obj = self.pool.get('ir.module.category')
            idss = module_cat_obj.search(cr, uid, [('users','in', [uid])])
            if idss:
                args.append(('category_id','in',idss))
                ids = super(res_groups, self).search(cr, uid, args, offset, limit,
                order, context=context, count=count)

        else:

            ids = super(res_groups, self).search(cr, uid, args, offset, limit,
                order, context=context, count=count)

        return ids



    def get_user_groups_view(self, cr, uid, context=None):
        if context is None:
            context = {}
        if 'it_access' in context and context['it_access'] == True:
            try:
                view = self.pool.get('ir.model.data').get_object(cr, SUPERUSER_ID, 'access_right_management', 'user_groups_view', context)
                assert view and view._table_name == 'ir.ui.view'
            except Exception:
                view = False
        else:

            view = super(res_groups, self).get_user_groups_view(cr, uid, context)

        
        return view



    def get_application_groups(self, cr, uid, domain=None, context=None):
        """
        """
        if context is None:
            context = {}

        if domain is None:
            domain=[]
        if 'it_access' in context and context['it_access'] == True:
            module_cat_obj = self.pool.get('ir.module.category')
            cat_ids = module_cat_obj.search(cr, uid, [('users','in', [uid])])
            idss = []
            if cat_ids:
                domain.append(('category_id','in',cat_ids))
                idss =  self.search(cr, uid, domain or [])

        else:
            idss =  self.search(cr, uid, domain or [])
        
        return idss


    def create(self, cr, uid, values, context=None):
        if context is None:
            context = {}
        res = super(res_groups, self).create(cr, uid, values, context)
        ######### for log ##############
        new_vals = {}
        old_vals = {}
        model = self._name 
        method = 'create'
        fields = values.keys()
        new_rec = self.read(cr, uid, [res], values.keys())
        for x in values.keys():
            new_vals[x] = new_rec[0][x]

        create_log(self, cr, uid, res, model, old_vals, new_vals, fields, method, context=context)
        
        return res



    def write(self, cr, uid, ids, values, context=None):
        if context is None:
            context = {}
        model = self._name 
        method = 'write'
        for rec in self.browse(cr, uid, ids, context):
            old_rec = self.read(cr, uid, [rec.id], values.keys())
            fields = values.keys()
            super(res_groups, self).write(cr, uid, [rec.id], values, context)
            new_rec = self.read(cr, uid, [rec.id], values.keys())
            
            new_vals = {}
            old_vals = {}
            for x in values.keys():
                new_vals[x] = new_rec[0][x]
                old_vals[x] = old_rec[0][x]

            create_log(self, cr, uid, rec.id, model, old_vals, new_vals, fields, method, context=context)

        return True

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for rec in self.browse(cr, uid, ids, context):
            new_vals = {}
            old_vals = {}
            model = self._name 
            method = 'unlink'
            old_rec = self.read(cr, uid, [rec.id], [])
            name = self.name_get(cr, uid, [rec.id], context)[0][1]
            fields = old_rec[0].keys()
            old_vals = old_rec[0]

            super(res_groups, self).unlink(cr, uid, [rec.id], context)
            context['rec_name'] = name
            create_log(self, cr, uid, rec.id, model, old_vals, new_vals, fields, method, context=context)

        return True


def name_selection_groups(ids): return 'sel_groups_' + '_'.join(map(str, ids))
def name_boolean_group(id): return 'in_group_' + str(id)


class res_users(osv.osv):
    _inherit = 'res.users'



    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        
        if context is None:
            context = {}
        
        

        if 'it_access' in context and context['it_access'] == True:
            args.append( ('id','!=',SUPERUSER_ID) )
            self.pool.get('res.groups').update_user_groups_view(cr, uid, context)
        ids = super(res_users, self).search(cr, uid, args=args, offset=offset, limit=limit,
                order=order, context=context, count=count)
        return ids



    def create(self, cr, uid, values, context=None):
        if context is None:
            context = {}
        res = super(res_users, self).create(cr, uid, values, context)
        self._set_reified_groups(values)
        ######### for log ##############
        new_vals = {}
        old_vals = {}
        model = self._name 
        method = 'create'
        fields = values.keys()
        new_rec = self.read(cr, uid, [res], values.keys())
        for x in values.keys():
            new_vals[x] = new_rec[0][x]

        create_log(self, cr, uid, res, model, old_vals, new_vals, fields, method, context=context)
        if 'it_access' in context and context['it_access'] == True:
            self.pool.get('res.groups').update_user_groups_view(cr, uid, context)
        return res

    def write(self, cr, uid, ids, values, context=None):
        if context is None:
            context = {}
        model = self._name 
        method = 'write'
        self._set_reified_groups(values)
        for rec in self.browse(cr, uid, ids, context):
            old_rec = self.read(cr, uid, [rec.id], values.keys())
            fields = values.keys()
            super(res_users, self).write(cr, uid, [rec.id], values, context)
            new_rec = self.read(cr, uid, [rec.id], values.keys())
            
            new_vals = {}
            old_vals = {}
            for x in values.keys():
                new_vals[x] = new_rec[0][x]
                old_vals[x] = old_rec[0][x]

            create_log(self, cr, uid, rec.id, model, old_vals, new_vals, fields, method, context=context)

        if 'it_access' in context and context['it_access'] == True:
            self.pool.get('res.groups').update_user_groups_view(cr, uid, context)
        return True

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for rec in self.browse(cr, uid, ids, context):
            new_vals = {}
            old_vals = {}
            model = self._name 
            method = 'unlink'
            old_rec = self.read(cr, uid, [rec.id], [])
            name = self.name_get(cr, uid, [rec.id], context)[0][1]
            fields = old_rec[0].keys()
            old_vals = old_rec[0]
            super(res_users, self).unlink(cr, uid, [rec.id], context)
            context['rec_name'] = name
            create_log(self, cr, uid, rec.id, model, old_vals, new_vals, fields, method, context=context)
        
        if 'it_access' in context and context['it_access'] == True:
            self.pool.get('res.groups').update_user_groups_view(cr, uid, context)
        
        return True


    def fields_get(self, cr, uid, allfields=None, context=None, write_access=True):

        res = super(res_users, self).fields_get(cr, uid, allfields, context, write_access)
        # add reified groups fields
        if uid != SUPERUSER_ID and not (self.pool['res.users'].has_group(cr, uid, 'base.group_erp_manager') or self.pool['res.users'].has_group(cr, uid, 'access_right_management.group_it_access_user')):
            return res
        for app, kind, gs in self.pool.get('res.groups').get_groups_by_application(cr, uid, context):
            if kind == 'selection':
                # selection group field
                tips = ['%s: %s' % (g.name, g.comment) for g in gs if g.comment]
                res[name_selection_groups(map(int, gs))] = {
                    'type': 'selection',
                    'string': app and app.name or _('Other'),
                    'selection': [(False, '')] + [(g.id, g.name) for g in gs],
                    'help': '\n'.join(tips),
                    'exportable': False,
                    'selectable': False,
                }
            else:
                # boolean group fields
                for g in gs:
                    res[name_boolean_group(g.id)] = {
                        'type': 'boolean',
                        'string': g.name,
                        'help': g.comment,
                        'exportable': False,
                        'selectable': False,
                    }
        return res


class audittrail_objects_proxy_custom(audittrail_objects_proxy):
    """ Uses Object proxy for auditing changes on object of subscribed Rules"""

    def get_value_text(self, cr, uid, pool, resource_pool, method, field, value):
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
            data = pool.get(field_obj._obj).name_get(cr, uid, value)
            #return the modifications on x2many fields as a list of names
            res = u''
            for x in data:
                res += u' ' + x[1]
                if x != data[len(data)-1]:
                    res += u',' + u' '
            #res = map(lambda x: x[1], data)
        elif field_obj._type == 'many2one':
            #return the modifications on a many2one field as its value returned by name_get()
            #res = value and value[1] or value
            res = value and (type(value) == type(1) and pool.get(field_obj._obj).name_get(cr, uid, [value])[0][1] or value[1]) or value
        else:
            res = value
        return res

    
    audittrail_objects_proxy.get_value_text = get_value_text

    
