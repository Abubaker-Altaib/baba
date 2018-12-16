# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields,osv
from tools.translate import _

class res_users_inherit(osv.osv):
    """
    To add separated users between Supply Department and Techncial Services Department """

    _inherit = 'res.users'

    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
                     ]

    _columns = {

       'belong_to':fields.selection(USERS_SELECTION, 'Belongs To', select=True , help='Select Department Which this user belongs to it'),


              }
 

class stock_location_inherit(osv.osv):
    """
    To separate Stock between Supply Department and Techncial Services Department """

    _inherit = 'stock.location'

    USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),

                     ]

    _columns = {

       'executing_agency':fields.selection(USERS_SELECTION, 'executing_agency', select=True , help='Select Department Which this user belongs to it'),}
