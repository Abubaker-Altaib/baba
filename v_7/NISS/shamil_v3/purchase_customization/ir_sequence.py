
from osv import osv,fields


class ir_sequence(osv.osv):
  
  
  
  _inherit = 'ir.sequence'
  
  USERS_SELECTION = [
        ('admin', 'Supply Department'),
        ('tech', 'Techncial Services Department'),
        ('arms', 'Arms Department'),
                     ]
  
  _columns = {
        'executing_agency':fields.selection(USERS_SELECTION, 'Executing Agency', help='Department Which this request will executed it'),
            }    