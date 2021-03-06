# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _

class account_tax(osv.Model):
    """ Inherit model to override name_get method """
    _inherit = "account.tax"
    
    def name_get(self, cr, uid, ids, context=None):
        """
        override method to makeing Tax name appeare like "code name"
        @return: dictionary,name of all tax 
        """
        cr.execute('select count(id) from res_company')
        if cr.fetchone()[0] < 2:
            return super(account_tax, self).name_get(cr, uid, ids, context)
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads=[]
        for i in ids:
            r = {}
            r = self.read(cr, uid, i, ['name'], context, load='_classic_write')
            cr.execute('SELECT c.code FROM account_tax p left join res_company  c on (p.company_id = c.id) ' \
                        'WHERE p.id = %s  ', (i,))
            r['code'] =  cr.fetchone()[0]
            reads.append(r)
        return [(x['id'], (x['code'] and (x['code'] + ' - ') or '') + x['name']) \
                for x in reads]
account_tax()


class account_period(osv.Model):

    """ Inherit model to override name_get method """
    
    _inherit = "account.period"

    def find(self, cr, uid, dt=None, context=None):
        if context is None:
            context = {}
        result=super(account_period, self).find(cr, uid, dt=dt, context=context)
        if not context.get('closed',False):
            result = self.search(cr, uid, [('id', 'in', result),('state', '=', 'draft')], context=context)
        if not result:
            raise osv.except_osv(_('Error!'), _('There is no period defined for this date: %s.\nPlease create one.')%dt)
        return result

    def name_get(self, cr, uid, ids, context=None):
        """
        override method to makeing account period name appeare like "code name"
        @return: dictionary,name of all account periods 
        """
        cr.execute('select count(id) from res_company')
        if cr.fetchone()[0] < 2:
            return super(account_period, self).name_get(cr, uid, ids, context)
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads=[]
        for i in ids:
            r = {}
            r = self.read(cr, uid, i, ['name'], context, load='_classic_write')
            cr.execute('SELECT c.code FROM account_period p left join res_company  c on (p.company_id = c.id) ' \
                        'WHERE p.id = %s  ', (i,))
            r['code'] =  cr.fetchone()[0]
            reads.append(r)
        return [(x['id'], (x['code'] and (x['code'] + ' - ') or '') + x['name']) \
                for x in reads]
account_period()


class account_fiscalyear(osv.Model):
    
    """ Inherit model to override name_get method """

    _inherit = "account.fiscalyear"

    def name_get(self, cr, uid, ids, context=None):
        """
        override method to makeing  fiscal year name appeare like "code name"
        @return: dictionary,name of all account fiscal years 
        """
        cr.execute('select count(id) from res_company')
        if cr.fetchone()[0] < 2:
            return super(account_fiscalyear, self).name_get(cr, uid, ids, context)
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads=[]
        for i in ids:
            r = {}
            r = self.read(cr, uid, i, ['name'], context, load='_classic_write')
            cr.execute('SELECT c.code FROM account_fiscalyear p left join res_company  c on (p.company_id = c.id) ' \
                        'WHERE p.id = %s  ', (i,))
            r['code'] =  cr.fetchone()[0]
            reads.append(r)
        return [(x['id'], (x['code'] and (x['code'] + ' - ') or '') + x['name']) \
                for x in reads]


            
account_fiscalyear()


class account_journal(osv.Model):

    """ Inherit model to override name_get method """

    _inherit = "account.journal"
    
    def name_get(self, cr, uid, ids, context=None):
        """
        override method to makeing  account journal name appeare like "code name"
        @return: dictionary,name of all account journals 
        """
        cr.execute('select count(id) from res_company')
        if cr.fetchone()[0] < 2:
            return super(account_journal, self).name_get(cr, uid, ids, context)
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads=[]
        for i in ids:
            r = {}
            r = self.read(cr, uid, i, ['name'], context, load='_classic_write')
            cr.execute('SELECT c.code FROM account_journal p left join res_company  c on (p.company_id = c.id) ' \
                        'WHERE p.id = %s  ', (i,))
            r['code'] =  cr.fetchone()[0]
            reads.append(r)
        return [(x['id'], (x['code'] and (x['code'] + ' - ') or '') + x['name']) \
                for x in reads]
account_journal()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
