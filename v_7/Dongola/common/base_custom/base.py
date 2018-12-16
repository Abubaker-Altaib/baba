# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from openerp import tools
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class res_currency(osv.Model):
    """
    To manage currency sambols and modify operations
    """
    _inherit = "res.currency"

    _columns = {
        'symbol': fields.char('Symbol', size=5, help="Currency sign, to be used when printing amounts"),
        'units_name': fields.char('Currency Symbol', size=5, help="To be use when printing units  amount",required=True),
        'cents_name': fields.char('Cents Symbol', size=5, help="To be use when printing Cents  amount",required=True),
    }

    def compute(self, cr, uid, from_currency_id, to_currency_id, from_amount, round=True, currency_rate_type_from=False, currency_rate_type_to=False, context=None):
        """
        Method that transfer amount from one currency to the other.
        
        @param from_currency_id: the amount currency id 
        @param to_currency_id: new currency id
        @param from_amount: amount to change currency
        @param round: Boolean to round the amount
        @param currency_rate_type_from: Boolean of currency rate type
        @param currency_rate_type_to: Boolean of currency rate type
        @return: super compute() method
        """
        return super(res_currency,self).compute(cr, uid, to_currency_id, from_currency_id, from_amount,
                round=round, currency_rate_type_from=currency_rate_type_from, currency_rate_type_to=currency_rate_type_to, context=context)

class res_company(osv.Model):
    """
    To add currency format 
    """
    _inherit = "res.company"

    _columns = {
        
        'currency_format': fields.selection([ ('euro','Europian Format'), ('ar','Arabic Format')], 'Check Printing Format'),
    }

    _defaults = {
        'currency_format':'ar',
    }

class update_records(osv.osv_memory):
    """
    Model that recalculate functional fields thats already stored for the selected model 
    """
    _name = "update.records"
    
    _description = 'Updating Records Values'

    _columns = {
        'obj': fields.many2one('ir.model', 'Model Name', required=True),
        'val': fields.char('Values'),
        'domain': fields.char('Domain'),
    }
    _defaults = {
        'val':'{}',
        'domain':'[]',
    }
    
    def compute(self, cr, uid, ids, context={}):
        """
        To update object lines.

        @return: Action 
        """
        wiz = self.browse(cr, uid, ids, context=context)[0]
        obj = self.pool.get(wiz.obj.model)
        try:
            vals = eval(wiz.val)
        except:
            raise orm.except_orm(_('Parsing Error !'), _('Values field must be dictionary')) 
        try:
            domain = eval(wiz.domain)
        except:
            raise orm.except_orm(_('Parsing Error !'), _('Domain field must be list of tuple')) 
        rec_ids = obj.search(cr, uid,domain, context=context)
        obj.write(cr,uid,rec_ids,vals,context=context)
        return {'type': 'ir.actions.act_window_close'}

class ir_translation(osv.osv):
    """
    Inherit ir.translation to resolve workflow functions issue which doesn't send context 
    which means no lang send to translate terms
    """
    _inherit = "ir.translation"

    @tools.ormcache(skiparg=3)
    def _get_source(self, cr, uid, name, types, lang, source=None):
        """
        When there is no language sent, set the current logged in user language
        
        @return: super _get_source
        """
        if not lang:
            cr.execute("""SELECT lang
                          FROM res_users INNER JOIN res_partner ON
                          res_partner.id = res_users.partner_id
                          WHERE res_users.id=%s""", (uid,))
            lang = cr.fetchone()[0] or False
        return super(ir_translation, self)._get_source(cr, uid, name, types, lang, source)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
