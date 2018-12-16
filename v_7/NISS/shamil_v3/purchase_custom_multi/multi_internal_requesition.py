#coding:utf-8
from tools.translate import _
from osv import osv
from osv import fields
import decimal_precision as dp
import netsvc
import time
from datetime import datetime
#from common_tools.voucher import action_move_line_create as action_move_line_create

class multi_ireq_m(osv.osv):
    _inherit = 'ireq.m'
    _columns = {
        'multi' : fields.boolean('Multi Purchase Orders', help="The active field allows you to didcate if you wont to make more than one Purchase Order from this requisiton."),
              
    }
multi_ireq_m()

