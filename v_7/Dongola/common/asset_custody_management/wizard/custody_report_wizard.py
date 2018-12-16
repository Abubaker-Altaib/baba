
from openerp.osv import fields, osv
import time
from openerp.tools.translate import _
from openerp import netsvc



class custody_report(osv.osv_memory):
    """ 
    Class to Print Custodies From wizard """

    _description='Print Custodies From wizard'
    _name = 'custody.report'
    _columns = {
                'department_id' : fields.many2one('hr.department','Department',),
                'category_company_id' : fields.many2one('custody.company' , 'Company of Category' ),
                'category_id' : fields.many2one('account.asset.category' ,'Parent Category' ,),
                'version_id' : fields.many2one('custody.category.models' , 'Version'),
                'report_type' : fields.selection([('sum','Summation'),('detail','Detail')],  'Report Type' , required=True,),
                'custody_type' : fields.selection([('in_stock','Custody In stock'),('in_user','Custody In User')],  'Custody Type' , required=True,),
                'with_childern' : fields.boolean('With Childern') ,         

                }
    
    def onchange_company(self , cr, uid , ids , category_company_id ,context=None) :
          """
           Onchange company put the restrict domain on category field

	  @return: 
			"""
          category_ids = []
          for category_id in self.pool.get("custody.company").browse(cr,uid,category_company_id).category_ids :
              if category_id :
                 category_ids.append(category_id.id)
          return { 'domain' : { 'category_id' : [( 'id' , 'in' , category_ids )] }}



    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'account.asset.asset',
             'form': data
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'custody_report',
            'datas': datas,
            }

