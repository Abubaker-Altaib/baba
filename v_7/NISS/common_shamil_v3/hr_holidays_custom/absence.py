# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import fields, osv
import mx
import datetime
import time

#----------------------------------------
#holiday status(inherit)
#----------------------------------------
class  hr_holidays_status_absence(osv.Model):
    """Inherits hr.holidays.status and add absence field 
    """
    _inherit = "hr.holidays.status"

    _columns = {
        'absence': fields.boolean('Absence', help="If True the configuration is for absence."),
        'permission': fields.boolean('Permission', help="If True the configuration is for permission."),
        'number_hour': fields.float('Number Of Hours'),
    }

    _defaults = {
        'number_hour': 3,
        #'number_of_days': 3,
        'absence':0,
        'permission':0,
    }



#----------------------------------------
#holiday(inherit)
#----------------------------------------

class hr_holidays(osv.osv):

    _inherit = "hr.holidays"

    


    _columns = {
        'number_hours': fields.float('Numbers Of Hours'),
    }

    _defaults = {
        'employee_id': False, #To call onchange_employee
        'date_from': fields.datetime.now,
        'name': '/',
        #'number_hour': 3
    }


    def onchange_date_to(self, cr, uid, ids, date_to, date_from):
        """
        Update the number_of_days and number of hours.
        """
        res = super(hr_holidays, self).onchange_date_to(cr, uid, ids, date_to, date_from)
        if date_from and date_to:
            date_from = mx.DateTime.Parser.DateTimeFromString(date_from )
            date_to = mx.DateTime.Parser.DateTimeFromString(date_to )
            hours = (date_to - date_from).hours
            res['value'].update({'number_hours': hours})
        return res

    def onchange_number_hours(self, cr, uid, ids, date_from, number_hours ):
        """
        Update the date_to.
        """
        vals = {}
        if date_from and number_hours:
            date_from = mx.DateTime.Parser.DateTimeFromString(date_from)
            date_to = date_from + datetime.timedelta(hours= number_hours)
            #date_to = mx.DateTime.Parser.DateTimeFromString(date_to )
            #hours = (date_to - date_from).hours
            date_to =  date_to.strftime("%Y-%m-%d %H:%M:%S")
            vals.update({'date_to': date_to})
        return {'value':vals}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

