# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import openerp.exceptions
import openerp.modules
from openerp import SUPERUSER_ID
from openerp.modules import loading
from datetime import datetime, timedelta
from lxml import etree
from openerp.modules import loading
import unicodedata
import openerp.pooler as pooler
import openerp.osv as osv 
from openerp.osv import fields
from openerp.osv import orm
from openerp.osv.orm import BaseModel
original_BaseModel = BaseModel.__init__

"""
To modify the __init__ function to modiffy selection fields to read from the 
client besid the python selection list """
    
def initiate_models(self, pool, cr):
        """ Initialize a model and make it part of the given registry.

        - copy the stored fields' functions in the osv_pool,
        - update the _columns with the fields found in ir_model_fields,
        - ensure there is a many2one for each _inherits'd parent,
        - update the children's _columns,
        - give a chance to each field to initialize itself.

        """
        original_BaseModel(self,pool, cr)
        cr.execute('SELECT * FROM ir_model_fields WHERE model=%s AND state=%s', (self._name, 'base'))
        base_fields = cr.dictfetchall()
        for field in base_fields:
            if field['ttype'] == 'selection' and field['selection']:
                name = unicodedata.normalize('NFKD', field['name']).encode('ascii','ignore')
                selection_list = self._columns[name].selection
                if type(selection_list) == list :
                    index = 1
                    values = field['selection'].split("'")
                    while(index != len(values)):
                        key=unicodedata.normalize('NFKD', values[index]).encode('ascii','ignore')
                        value = unicodedata.normalize('NFKD', values[index+2]).encode('ascii','ignore')
                        listt=(key,value)
                        if listt not in selection_list :
                            selection_list.append(listt)
                        index = index + 4
                        self._columns[name] = fields.selection(selection_list)

BaseModel.__init__= initiate_models 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
