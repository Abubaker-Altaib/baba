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
    To add separated users between Supply Departments   """

    _inherit = 'res.users'

    USERS_SELECTION = [
		('admin', 'Supply Department'),
		('tech', 'Techncial Services Department'),
		('arms', 'Arms Department'),
		('veichles', 'Veichles Department'),
		('medic', 'Medic Department'),
		('maintainance', 'Maintainance Department'),
					 ]

    _columns = {

       'belong_to':fields.selection(USERS_SELECTION, 'Belongs To', select=True , help='Select Department Which this user belongs to it'),


              }
 
