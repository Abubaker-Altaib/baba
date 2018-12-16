# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import res_config
import os
if 'TZ' in os.environ:
    os.environ.pop('TZ') # Remove UTC timezone...
import base
import ps_list
import amount_to_text_ar
#import basic_state_obj



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
