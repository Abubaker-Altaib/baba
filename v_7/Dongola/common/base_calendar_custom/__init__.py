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
import datetime
import operator
import pickle
import re
import time


from openerp.tools.translate import _

from openerp.osv import osv
class BaseModelExtend(osv.AbstractModel):
   _name = 'basemodel.extend'

   def _register_hook(self, cr):            

      def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False):
        """
        Get the list of records in list view grouped by the given ``groupby`` fields

        :param cr: database cursor
        :param uid: current user id
        :param domain: list specifying search criteria [['field_name', 'operator', 'value'], ...]
        :param list fields: list of fields present in the list view specified on the object
        :param list groupby: fields by which the records will be grouped
        :param int offset: optional number of records to skip
        :param int limit: optional max number of records to return
        :param dict context: context arguments, like lang, time zone
        :param list orderby: optional ``order by`` specification, for
                             overriding the natural sort ordering of the
                             groups, see also :py:meth:`~osv.osv.osv.search`
                             (supported only for many2one fields currently)
        :return: list of dictionaries(one dictionary for each record) containing:

                    * the values of fields grouped by the fields in ``groupby`` argument
                    * __domain: list of tuples specifying the search criteria
                    * __context: dictionary with argument like ``groupby``
        :rtype: [{'field_name_1': value, ...]
        :raise AccessError: * if user has no read rights on the requested object
                            * if user tries to bypass access rules for read on the requested object

        """
        context = context or {}
        self.check_access_rights(cr, uid, 'read')
        if not fields:
            fields = self._columns.keys()

        query = self._where_calc(cr, uid, domain, context=context)
        self._apply_ir_rules(cr, uid, query, 'read', context=context)

        # Take care of adding join(s) if groupby is an '_inherits'ed field
        groupby_list = groupby
        qualified_groupby_field = groupby
        if groupby:
            if isinstance(groupby, list):
                groupby = groupby[0]
            qualified_groupby_field = self._inherits_join_calc(groupby, query)

        if groupby:
            assert not groupby or groupby in fields, "Fields in 'groupby' must appear in the list of fields to read (perhaps it's missing in the list view?)"
            groupby_def = self._columns.get(groupby) or (self._inherit_fields.get(groupby) and self._inherit_fields.get(groupby)[2])
            assert groupby_def and groupby_def._classic_write, "Fields in 'groupby' must be regular database-persisted fields (no function or related fields), or function fields with store=True"

        # TODO it seems fields_get can be replaced by _all_columns (no need for translation)
        fget = self.fields_get(cr, uid, fields)
        select_terms = []
        groupby_type = None
        if groupby:
            if fget.get(groupby):
                groupby_type = fget[groupby]['type']
                if groupby_type in ('date', 'datetime'):
                    qualified_groupby_field = "to_char(%s,'yyyy-mm')" % qualified_groupby_field
                elif groupby_type == 'boolean':
                    qualified_groupby_field = "coalesce(%s,false)" % qualified_groupby_field
                select_terms.append("%s as %s " % (qualified_groupby_field, groupby))
            else:
                # Don't allow arbitrary values, as this would be a SQL injection vector!
                raise except_orm(_('Invalid group_by'),
                                 _('Invalid group_by specification: "%s".\nA group_by specification must be a list of valid fields.')%(groupby,))

        aggregated_fields = [
            f for f in fields
            if f not in ('id', 'sequence', groupby)
            if fget[f]['type'] in ('integer', 'float')
            if (f in self._all_columns and getattr(self._all_columns[f].column, '_classic_write'))]
        for f in aggregated_fields:
            group_operator = fget[f].get('group_operator', 'sum')
            qualified_field = self._inherits_join_calc(f, query)
            select_terms.append("%s(%s) AS %s" % (group_operator, qualified_field, f))

        order = orderby or groupby or ''
        groupby_terms, orderby_terms = self._read_group_prepare(order, aggregated_fields, groupby, qualified_groupby_field, query, groupby_type)

        from_clause, where_clause, where_clause_params = query.get_sql()
        if len(groupby_list) < 2 and context.get('group_by_no_leaf'):
            count_field = '_'
        else:
            count_field = groupby

        prefix_terms = lambda prefix, terms: (prefix + " " + ",".join(terms)) if terms else ''
        prefix_term = lambda prefix, term: ('%s %s' % (prefix, term)) if term else ''

        query = """
            SELECT min(%(table)s.id) AS id, count(%(table)s.id) AS %(count_field)s_count
                   %(extra_fields)s
            FROM %(from)s
            %(where)s
            %(groupby)s
            %(orderby)s
            %(limit)s
            %(offset)s
        """ % {
            'table': self._table,
            'count_field': count_field,
            'extra_fields': prefix_terms(',', select_terms),
            'from': from_clause,
            'where': prefix_term('WHERE', where_clause),
            'groupby': prefix_terms('GROUP BY', groupby_terms),
            'orderby': prefix_terms('ORDER BY', orderby_terms),
            'limit': prefix_term('LIMIT', int(limit) if limit else None),
            'offset': prefix_term('OFFSET', int(offset) if limit else None),
        }
        cr.execute(query, where_clause_params)
        alldata = {}
        fetched_data = cr.dictfetchall()

        data_ids = []
        for r in fetched_data:
            for fld, val in r.items():
                if val is None: r[fld] = False
            alldata[r['id']] = r
            data_ids.append(r['id'])
            del r['id']

        if groupby:
            data = self.read(cr, uid, data_ids, [groupby], context=context)
            # restore order of the search as read() uses the default _order (this is only for groups, so the footprint of data should be small):
            data_dict = dict((d['id'], d[groupby] ) for d in data)
            result = [{'id': i, groupby: data_dict[i]} for i in data_ids]
        else:
            result = [{'id': i} for i in data_ids]

        for d in result:
            if groupby:
                d['__domain'] = [(groupby, '=', alldata[d['id']][groupby] or False)] + domain
                if not isinstance(groupby_list, (str, unicode)):
                    if groupby or not context.get('group_by_no_leaf', False):
                        d['__context'] = {'group_by': groupby_list[1:]}
            if groupby and groupby in fget:
                if d[groupby] and fget[groupby]['type'] in ('date', 'datetime'):
                    dt = datetime.datetime.strptime(alldata[d['id']][groupby][:7], '%Y-%m')
                    days = calendar.monthrange(dt.year, dt.month)[1]

                    date_value = datetime.datetime.strptime(d[groupby][:10], '%Y-%m-%d')
                    locale=context.get('lang', 'en_US')
                    #use arabic instade of arabic syria
                    if locale == "ar_SY":
                        locale = "ar"
                    d[groupby] = babel.dates.format_date(
                        date_value, format='MMMM yyyy', locale=locale)
                    d['__domain'] = [(groupby, '>=', alldata[d['id']][groupby] and datetime.datetime.strptime(alldata[d['id']][groupby][:7] + '-01', '%Y-%m-%d').strftime('%Y-%m-%d') or False),\
                                     (groupby, '<=', alldata[d['id']][groupby] and datetime.datetime.strptime(alldata[d['id']][groupby][:7] + '-' + str(days), '%Y-%m-%d').strftime('%Y-%m-%d') or False)] + domain
                del alldata[d['id']][groupby]
            d.update(alldata[d['id']])
            del d['id']

        if groupby and groupby in self._group_by_full:
            result = self._read_group_fill_results(cr, uid, domain, groupby, groupby_list,
                                                   aggregated_fields, result, read_group_order=order,
                                                   context=context)

        return result

      osv.osv.read_group = read_group
      osv.osv_memory.read_group = read_group
      osv.osv_abstract.read_group = read_group
      return super(BaseModelExtend, self)._register_hook(cr)




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
