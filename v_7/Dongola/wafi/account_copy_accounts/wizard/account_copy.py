from osv import fields, osv
import time
from datetime import datetime,date,timedelta
from tools.translate import _



class account_copy(osv.osv_memory):
      _name = 'account.copy'
      _columns = {
               'from_company': fields.many2one('res.company', 'From', required=True),
               'to_company': fields.many2one('res.company', 'To', required=True),
                   }


      def get_accounts(self, cr, uid, ids, context=None):
		"""
		To get Accounts.
		"""
		rec = self.browse(cr, uid, ids, context=context)[0]
		if rec.from_company.id == rec.to_company.id:
		    raise osv.except_osv(_("ValidateError"),_('You Selected Same Company !'))
		
		acc_obj = self.pool.get('account.account')
                account_ids = acc_obj.search(cr,uid,[('company_id','=', rec.from_company.id )])
                print account_ids
                #res = []
                if not account_ids:
		    raise osv.except_osv(_("ValidateError"),_('The Selected Source Company hasnt Accounts!'))
                for acc in acc_obj.browse(cr,uid,account_ids):
                    exist_acc_code = acc_obj.search(cr,uid,[('company_id','=', rec.to_company.id),('code','=',acc.code)])
                    if not exist_acc_code:
                       record = {
                           'code' : acc.code,
                           'name' : acc.name,
                           'active' : True,
                           'company_id' : rec.to_company.id,
                           'type' : acc.type,
                           'user_type' : acc.user_type.id,
                           'currency_mode' : 'current'

                    

                               }
                       acc_id = acc_obj.create(cr,uid,record)
                       #res.append(record)
                #print "REEEEEEEEEEES",res
                return True
                
                


