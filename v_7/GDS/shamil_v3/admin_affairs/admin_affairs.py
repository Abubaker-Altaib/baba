# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv, fields
from tools.translate import _
import time

class account_analytic_account(osv.Model):


    _inherit = 'account.analytic.account'

    _columns = {
        'project': fields.boolean('Project'),
    }


#----------------------------------------
# Class admin_affairs model
#----------------------------------------
class admin_affairs_model(osv.osv):
    """
    To prepare which admin affairs model that you want to set account details """
     
    _name = "admin.affairs.model"
    _description = 'Admin affairs model'

    _columns = { 
        'name': fields.char('Name', size=64, required=True, select=True,),
        'model' : fields.char('Model', size=64, required=True, ),
               }
        
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be unique !'),
            ] 
    
admin_affairs_model()

#----------------------------------------
# Class admin_affairs account
#----------------------------------------
class admin_affairs_account(osv.osv):
    """
    To manage admin affaire accounts """
    
    def create(self, cr, user, vals, context=None):
        """
        Create new entry sequence for every new admin affairs account record.

        @param vals: record to be created
        @return: return a result that create a new record in the database
        """
        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  'admin_affairs.account'
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name) 
        return super(admin_affairs_account, self).create(cr, user, vals, context) 
    
    _name = "admin_affairs.account"
    _description = 'Admin affairs account'

    _columns = { 
        'name': fields.char('Reference', size=64, required=True, select=True, readonly=True, help="unique number of the record"),
        'date' : fields.date('Date',required=True, readonly=True,),
        'model_id': fields.many2one('admin.affairs.model','Model',required=True),
        'templet_id': fields.many2one('account.account.template','Account Templet'),
        'code': fields.related('templet_id','code',type='char',relation='account.account.template',string='Code', store=True, readonly=True),
        'name_type': fields.many2one('account.account.type','Account_type'),
        #'company_id': fields.many2one('res.company','Company'),
        'journal_id': fields.property('account.journal', required=True,type='many2one', relation='account.journal',string='Journal', method=True, view_load=True),                        
        'account_id': fields.property('account.account',type='many2one', relation='account.account', string='Account', method=True, view_load=True),
        
       # 'pro_journal_id': fields.property('account.journal', 
        #    type='many2one', 
         #   relation='account.journal',
          #  string='Project Journal', 
           # method=True, 
           # view_load=True), 
                       
        #'pro_account_id': fields.property('account.account',
            #type='many2one', 
            #relation='account.account',
            #string='Project Account', 
           # method=True, 
           # view_load=True),           
       'analytic_id': fields.property('account.analytic.account',
            type='many2one', 
            relation='account.analytic.account',
            string='Analytic account', 
            method=True, 
            view_load=True),
           
        'notes': fields.text('Notes', size=256 ), 
               }
        
    _sql_constraints = [
        ('model_uniq', 'unique(model_id)', 'Model must be unique!'),
        ('name_uniq', 'unique(name)', 'Reference must be unique !'),
            ] 
    
    _defaults = {
                'date': time.strftime('%Y-%m-%d'),
                'name':'/'
                }


class manufacturing_year(osv.osv):
    """
    To manage manufactur year """

    _name = 'manufacturing.year'
    _columns = {
        'name': fields.char('Year', size=64, required=True),
		}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
