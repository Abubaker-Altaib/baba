# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
import openerp.exceptions
import openerp.modules
from openerp.modules import loading
from datetime import datetime, timedelta
from lxml import etree
import openerp.pooler as pooler
from openerp.tools.config import config
from openerp.tools import convert
from openerp.tools.convert import _eval_xml
from openerp.osv import osv,fields
unsafe_eval = eval
original_xml_import = convert.xml_import

class custom_config_settings(osv.osv):
    _name = 'custom.config.settings'
    _inherit = 'res.config.settings'
    _columns = {
      'module_base_custom_extra': fields.boolean('Skip Upgrade Models',
            help="""if this box is true the system will be skip workflow and security and csv files in particular module when upgrade it."""),
               }
    _defaults = {
        'module_base_custom_extra': False,
    }
    
class tagRecord(original_xml_import):

    # Override of xml import in tag_record method.
    # this function would be called when install or upgrade partcualer module.
    # it is skip all workflow and groups and rule in xml records

    def _tag_record(self, cr, rec, data_node=None):
        rec_model = rec.get("model").encode('ascii')
        model = self.pool.get(rec_model)
        skip_models=('workflow','workflow.activity','workflow.transition','res.groups','ir.rule','ir.model.access')
        base_config_settings_obj = self.pool.get('base.config.settings')
        assert model, "The model %s does not exist !" % (rec_model,)
        rec_id = rec.get("id",'').encode('ascii')
        rec_context = rec.get("context", None)
        if rec_context:
            rec_context = unsafe_eval(rec_context)
        self._test_xml_id(rec_id)
        if self.isnoupdate(data_node) and self.mode != 'init':
            # check if the xml record has an id string
            if rec_id:
                if '.' in rec_id:
                    module,rec_id2 = rec_id.split('.')
                else:
                    module = self.module
                    rec_id2 = rec_id
                id = self.pool.get('ir.model.data')._update_dummy(cr, self.uid, rec_model, module, rec_id2)
                # check if the resource already existed at the last update
                if id:
                    # if it existed, we don't update the data, but we need to
                    # know the id of the existing record anyway
                    self.idref[rec_id] = int(id)
                    return None
                else:
                    # if the resource didn't exist
                    if not self.nodeattr2bool(rec, 'forcecreate', True):
                        # we don't want to create it, so we skip it
                        return None
                    # else, we let the record to be created

            else:
                # otherwise it is skipped
                return None
        res = {}
        for field in rec.findall('./field'):
#TODO: most of this code is duplicated above (in _eval_xml)...
            f_name = field.get("name",'').encode('utf-8')
            f_ref = field.get("ref",'').encode('utf-8')
            f_search = field.get("search",'').encode('utf-8')
            f_model = field.get("model",'').encode('utf-8')
            if not f_model and model._columns.get(f_name,False):
                f_model = model._columns[f_name]._obj
            f_use = field.get("use",'').encode('utf-8') or 'id'
            f_val = False

            if f_search:
                q = unsafe_eval(f_search, self.idref)
                field = []
                assert f_model, 'Define an attribute model="..." in your .XML file !'
                f_obj = self.pool.get(f_model)
                # browse the objects searched
                s = f_obj.browse(cr, self.uid, f_obj.search(cr, self.uid, q))
                # column definitions of the "local" object
                _cols = self.pool.get(rec_model)._columns
                # if the current field is many2many
                if (f_name in _cols) and _cols[f_name]._type=='many2many':
                    f_val = [(6, 0, map(lambda x: x[f_use], s))]
                elif len(s):
                    # otherwise (we are probably in a many2one field),
                    # take the first element of the search
                    f_val = s[0][f_use]
            elif f_ref:
                if f_ref=="null":
                    f_val = False
                else:
                    if f_name in model._columns \
                              and model._columns[f_name]._type == 'reference':
                        val = self.model_id_get(cr, f_ref)
                        f_val = val[0] + ',' + str(val[1])
                    else:
                        f_val = self.id_get(cr, f_ref)
            else:
                f_val = _eval_xml(self,field, self.pool, cr, self.uid, self.idref)
                if model._columns.has_key(f_name):
                    import openerp.osv as osv
                    if isinstance(model._columns[f_name], osv.fields.integer):
                        f_val = int(f_val)
            res[f_name] = f_val

        if rec_model in skip_models and self.mode == 'update' and not rec_id : 
           id = self.pool.get('ir.model.data')._update_dummy(cr, self.uid, rec_model, self.module, rec_id)
        else:
           id = self.pool.get('ir.model.data')._update(cr, self.uid, rec_model, self.module, res, rec_id or False, not self.isnoupdate(data_node), noupdate=self.isnoupdate(data_node), mode=self.mode, context=rec_context )
        if rec_id:
            self.idref[rec_id] = int(id)
        if config.get('import_partial', False):
            cr.commit()
        return rec_model, id

convert.xml_import = tagRecord

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
