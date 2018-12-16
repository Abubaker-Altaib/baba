from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class asset_report(osv.osv_memory):
    """ To print asset report """
    _name = "asset.report.wizard"

    _description = "Asset Report Wizard"

    _columns = {
        'company_id': fields.many2one('res.company', ' Company', required=True),
        'date_from': fields.date("Date From"),
        'date_to': fields.date("Date To"),
        'target_operation':fields.selection([('all','All'),('posted','Posted'),],string="Target Operation", required=True),
        'category_ids' :fields.many2many('account.asset.category',string='Category'),
    }
    _defaults = {
    	'target_operation' : 'posted',
    	'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'asset.report.wizard', context=c), 


    }

    def on_change_company(cr,uid,ids,context=None):
    	return {'value':{
    	'category_ids':False
    	}}

    def print_report(self, cr, uid, ids, context=None):
        """ 
        Print report.

        @return: Dictionary of print attributes
        """
        data = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': [],
             'model': 'account.asset.history',
             'form': data,
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'asset.report',
            'datas': datas,
            }