# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2018-2019 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from odoo import api
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import babel.dates
from odoo.osv import expression
from odoo.models import BaseModel

@api.model
def _read_group_format_result_custom(self, data, annotated_groupbys, groupby, domain):
    """
        Helper method to format the data contained in the dictionary data by 
        adding the domain corresponding to its values, the groupbys in the 
        context and by properly formatting the date/datetime values.

    :param data: a single group
    :param annotated_groupbys: expanded grouping metainformation
    :param groupby: original grouping metainformation
    :param domain: original domain for read_group
    """

    sections = []
    for gb in annotated_groupbys:
        ftype = gb['type']
        value = data[gb['groupby']]

        # full domain for this groupby spec
        d = None
        if value:
            if ftype == 'many2one':
                value = value[0]
            elif ftype in ('date', 'datetime'):
                locale = self._context.get('lang') or 'en_US'
                if locale == "ar_SY":
                    locale = "ar"
                fmt = DEFAULT_SERVER_DATETIME_FORMAT if ftype == 'datetime' else DEFAULT_SERVER_DATE_FORMAT
                tzinfo = None
                range_start = value
                range_end = value + gb['interval']
                # value from postgres is in local tz (so range is
                # considered in local tz e.g. "day" is [00:00, 00:00[
                # local rather than UTC which could be [11:00, 11:00]
                # local) but domain and raw value should be in UTC
                if gb['tz_convert']:
                    tzinfo = range_start.tzinfo
                    range_start = range_start.astimezone(pytz.utc)
                    range_end = range_end.astimezone(pytz.utc)

                range_start = range_start.strftime(fmt)
                range_end = range_end.strftime(fmt)
                if ftype == 'datetime':
                    label = babel.dates.format_datetime(
                        value, format=gb['display_format'],
                        tzinfo=tzinfo, locale=locale
                    )
                else:
                    label = babel.dates.format_date(
                        value, format=gb['display_format'],
                        locale=locale
                    )
                data[gb['groupby']] = ('%s/%s' % (range_start, range_end), label)
                d = [
                    '&',
                    (gb['field'], '>=', range_start),
                    (gb['field'], '<', range_end),
                ]

        if d is None:
            d = [(gb['field'], '=', value)]
        sections.append(d)
    sections.append(domain)

    data['__domain'] = expression.AND(sections)
    if len(groupby) - len(annotated_groupbys) >= 1:
        data['__context'] = { 'group_by': groupby[len(annotated_groupbys):]}
    del data['id']
    return data

BaseModel._read_group_format_result = _read_group_format_result_custom


