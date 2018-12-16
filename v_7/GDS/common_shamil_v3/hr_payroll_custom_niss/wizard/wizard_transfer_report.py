from osv import fields, osv


class wizard_transfer(osv.osv_memory):
   _name = "wizard.transfer"        


   _columns = {
    'company_id': fields.many2one('res.company', 'Company'),
    'process_type':fields.selection([('in','In'),('out','Out')] ,
                                   "Process Type", required=True),
    'destin' : fields.many2one("process.destin",'Destination'),
    'number' : fields.char("Number"),
    'date_from':fields.date('From'),
    'date_to':fields.date('To')

      }
   def _get_companies(self, cr, uid, context=None): 
        return self.pool.get('res.users').browse(cr,uid,uid).company_id.id


   _defaults = {
        'company_id': _get_companies,
        'process_type':'in',
                } 
   def print_report(self, cr, uid, ids, context={}):
        data ={'form': self.read(cr, uid, ids, [])[0]}
        return {'type': 'ir.actions.report.xml', 'report_name': 'hr.employee.transfer', 'datas': data}


