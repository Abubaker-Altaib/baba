# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
#from openerp import osv.models, api
import babel.dates
import calendar
import collections
import copy
import datetime
import itertools
import logging
import operator
import re
import simplejson
import time
import traceback
import types
from collections import defaultdict

import psycopg2
from lxml import etree
from openerp import SUPERUSER_ID
import pickle
import re
_logger = logging.getLogger(__name__)

from openerp.tools import SKIPPED_ELEMENT_TYPES



from openerp.tools.translate import _

from openerp.osv import osv,orm

# Deprecated.
class except_orm(Exception):
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.args = (name, value)
class BaseModelExtend_custom(osv.AbstractModel):
    _name = 'basemodel.extend_custom_rule_disable'
    
    def _register_hook(self, cr):
        def _check_record_rules_result_count(self, cr, uid, ids, result_ids, operation, context=None):
            """Verify the returned rows after applying record rules matches
            the length of `ids`, and raise an appropriate exception if it does not.
            """
            ids, result_ids = set(ids), set(result_ids)
            missing_ids = ids - result_ids
            if missing_ids:
                # Attempt to distinguish record rule restriction vs deleted records,
                # to provide a more specific error message - check if the missinf
                cr.execute('SELECT id FROM ' + self._table + ' WHERE id IN %s', (tuple(missing_ids),))
                if cr.rowcount:
                    # the missing ids are (at least partially) hidden by access rules
                    if uid == SUPERUSER_ID:
                        return

                    if context is None: context = {}
                    if context.get('rules', False):
                        return
                    _logger.warning('Access Denied by record rules for operation: %s, uid: %s, model: %s', operation, uid, self._name)
                    raise except_orm(_('Access Denied'),
                                    _('The requested operation cannot be completed due to security restrictions. Please contact your system administrator.\n\n(Document type: %s, Operation: %s)') % \
                                        (self._description, operation))
                else:
                    # If we get here, the missing_ids are not in the database
                    if operation in ('read','unlink'):
                        # No need to warn about deleting an already deleted record.
                        # And no error when reading a record that was deleted, to prevent spurious
                        # errors for non-transactional search/read sequences coming from clients 
                        return
                    _logger.warning('Failed operation on deleted record(s): %s, uid: %s, model: %s', operation, uid, self._name)
                    raise except_orm(_('Missing document(s)'),
                                    _('One of the documents you are trying to access has been deleted, please try again after refreshing.'))

        def check_access_rule(self, cr, uid, ids, operation, context=None):
            

            if context is None: context = {}
            if context.get('rules', False):
                return
            """Verifies that the operation given by ``operation`` is allowed for the user
            according to ir.rules.

            :param operation: one of ``write``, ``unlink``
            :raise except_orm: * if current ir.rules do not permit this operation.
            :return: None if the operation is allowed
            """
            if uid == SUPERUSER_ID:
                return

            if self.is_transient():
                # Only one single implicit access rule for transient models: owner only!
                # This is ok to hardcode because we assert that TransientModels always
                # have log_access enabled so that the create_uid column is always there.
                # And even with _inherits, these fields are always present in the local
                # table too, so no need for JOINs.
                cr.execute("""SELECT distinct create_uid
                            FROM %s
                            WHERE id IN %%s""" % self._table, (tuple(ids),))
                uids = [x[0] for x in cr.fetchall()]
                if len(uids) != 1 or uids[0] != uid:
                    raise except_orm(_('Access Denied'),
                                    _('For this kind of document, you may only access records you created yourself.\n\n(Document type: %s)') % (self._description,))
            else:
                where_clause, where_params, tables = self.pool.get('ir.rule').domain_get(cr, uid, self._name, operation, context=context)
                if where_clause:
                    where_clause = ' and ' + ' and '.join(where_clause)
                    for sub_ids in cr.split_for_in_conditions(ids):
                        cr.execute('SELECT ' + self._table + '.id FROM ' + ','.join(tables) +
                                ' WHERE ' + self._table + '.id IN %s' + where_clause,
                                [sub_ids] + where_params)
                        returned_ids = [x['id'] for x in cr.dictfetchall()]
                        self._check_record_rules_result_count(cr, uid, sub_ids, returned_ids, operation, context=context)



        def _apply_ir_rules(self, cr, uid, query, mode='read', context=None):
            """Add what's missing in ``query`` to implement all appropriate ir.rules
            (using the ``model_name``'s rules or the current model's rules if ``model_name`` is None)

            :param query: the current query object
            """
            if context is None: context = {}
            if context.get('rules', False):
                return

            if uid == SUPERUSER_ID:
                return

            def apply_rule(added_clause, added_params, added_tables, parent_model=None, child_object=None):
                """ :param string parent_model: string of the parent model
                    :param model child_object: model object, base of the rule application
                """
                if added_clause:
                    if parent_model and child_object:
                        # as inherited rules are being applied, we need to add the missing JOIN
                        # to reach the parent table (if it was not JOINed yet in the query)
                        parent_alias = child_object._inherits_join_add(child_object, parent_model, query)
                        # inherited rules are applied on the external table -> need to get the alias and replace
                        parent_table = self.pool.get(parent_model)._table
                        added_clause = [clause.replace('"%s"' % parent_table, '"%s"' % parent_alias) for clause in added_clause]
                        # change references to parent_table to parent_alias, because we now use the alias to refer to the table
                        new_tables = []
                        for table in added_tables:
                            # table is just a table name -> switch to the full alias
                            if table == '"%s"' % parent_table:
                                new_tables.append('"%s" as "%s"' % (parent_table, parent_alias))
                            # table is already a full statement -> replace reference to the table to its alias, is correct with the way aliases are generated
                            else:
                                new_tables.append(table.replace('"%s"' % parent_table, '"%s"' % parent_alias))
                        added_tables = new_tables
                    query.where_clause += added_clause
                    query.where_clause_params += added_params
                    for table in added_tables:
                        if table not in query.tables:
                            query.tables.append(table)
                    return True
                return False

            # apply main rules on the object
            rule_obj = self.pool.get('ir.rule')
            rule_where_clause, rule_where_clause_params, rule_tables = rule_obj.domain_get(cr, uid, self._name, mode, context=context)
            apply_rule(rule_where_clause, rule_where_clause_params, rule_tables)

            # apply ir.rules from the parents (through _inherits)
            for inherited_model in self._inherits:
                rule_where_clause, rule_where_clause_params, rule_tables = rule_obj.domain_get(cr, uid, inherited_model, mode, context=context)
                apply_rule(rule_where_clause, rule_where_clause_params, rule_tables,
                            parent_model=inherited_model, child_object=self)


#-----------------------------------------------------------------------
        


        osv.osv._check_record_rules_result_count = _check_record_rules_result_count
        osv.osv_memory._check_record_rules_result_count = _check_record_rules_result_count
        osv.osv_abstract._check_record_rules_result_count = _check_record_rules_result_count

        osv.osv.check_access_rule = check_access_rule
        osv.osv_memory.check_access_rule = check_access_rule
        osv.osv_abstract.check_access_rule = check_access_rule

        osv.osv._apply_ir_rules = _apply_ir_rules
        osv.osv_memory._apply_ir_rules = _apply_ir_rules
        osv.osv_abstract._apply_ir_rules = _apply_ir_rules

        
        return super(BaseModelExtend_custom, self)._register_hook(cr)




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
