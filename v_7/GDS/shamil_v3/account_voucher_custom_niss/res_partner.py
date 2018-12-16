# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
#############################################################################
#############################################################################

from osv import osv, fields
from openerp.tools.translate import _

class res_partner(osv.Model):

    _inherit = 'res.partner'

    _columns = {
            'code':fields.char('Code', size=64 ),
	    'department_id':fields.many2one('hr.department','Department'),
            #'degree_id':fields.many2one('hr.salary.degree','Degree'),
	 }

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'The partner code must be unique!'),
    ]

    def create(self, cr, user, vals, context=None):
        """
        Override to add constrain in name
        @param vals: Dictionary of values
        @return: super of res_partner
        """
        name = vals.get('name',False)
        if name and any(i.isdigit() for i in name):
            print">>>>>>>>>>>>>iam here"
            #seq = self.pool.get('ir.sequence').get(cr, user, 'exchange.order')
            #vals['name'] = seq and seq or '/'
            #if not seq:
            raise  osv.except_osv(_('Warning'), _('You cannot add number in the partner name, please use the field Code') )

        new_id = super(res_partner, self).create(cr, user, vals, context)
        return new_id

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []
        result = []
        for partner in self.browse(cr, user, ids, context=context):
            name = partner.name
            code = partner.code
            if code:
                name = '[%s] %s' % (code,name)
            result.append((partner.id, name))
        return result

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            ids = self.search(cr, user, [('code','=',name)]+ args, limit=limit, context=context)
           
            if not ids:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                ids = set()
                ids.update(self.search(cr, user, args + [('code',operator,name)], limit=limit, context=context))
                if not limit or len(ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    #ids.update(self.search(cr, user, args + [('name',operator,name)], limit=(limit and (limit-len(ids)) or False) , context=context))   
                    limit=(limit and (limit-len(ids)) or 8)
                    WHERE = " and name ilike '" + name + "%' limit " + str(limit)
                    cr.execute("SELECT id from res_partner where active=True "+ WHERE  )
                    res = cr.dictfetchall()
                    ids.update([l['id'] for l in res])

                ids = list(ids)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result

class res_users(osv.Model):

    _inherit = 'res.users'

    def create(self, cr, uid, vals, context=None):
        user_id = super(res_users, self).create(cr, uid, vals, context=context)
        user = self.browse(cr, uid, user_id, context=context)
        if user.login: 
            user.partner_id.write({'code': user.login})
        return user_id

    def write(self, cr, uid, ids, values, context=None):
        if not isinstance(ids,list):
            ids = [ids]
        res = super(res_users, self).write(cr, uid, ids, values, context)
        if values.get('login'):
            for user in self.browse(cr, uid, ids, context=context):
                user.partner_id.write({'code': user.login})
        return res
    
