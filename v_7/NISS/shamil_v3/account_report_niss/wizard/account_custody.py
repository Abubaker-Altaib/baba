# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import time
from openerp.osv import osv, fields

class custody_report_line(osv.osv_memory):
    _name = "custody.report.line"

    _columns = {
        'date': fields.date('Date'),
        'move_id': fields.many2one('account.move', 'Move'),
        'voucher_line_id': fields.many2one('account.voucher.line', 'Voucher Line'),
        'partner_code': fields.char('Partner Code',size =64),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'account_analytic_id': fields.many2one('account.analytic.account', 'Analytic Account'),
        'dest_approve': fields.many2one('account.analytic.account', 'Dest Approve'),
        'second_partner_id': fields.many2one('res.partner', 'Second Partner'),
        'chk_seq': fields.char('Check',size =64),
        'name': fields.char('Name', size =256),
        'amount': fields.float('Balance'),
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'report_id': fields.many2one('account.custody.report', 'Report'),
    }

class account_custody_report(osv.osv_memory):

    _name = "account.custody.report"
    _description = 'Account Custody'

    _columns = {
        'name': fields.char('Name', size =256),
        'chk_seq': fields.char('Check',size =64),
        'ready_print': fields.boolean('Ready for print',),
        'permission': fields.char('Permission',size =64),
        'custody_state': fields.selection([('all','All'),('removed','Removed'),('not removed','Not Removed'), ],'Custody State'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'dest_approve': fields.many2one('account.analytic.account', 'Dest Approve'),
        'account_analytic_id': fields.many2one('account.analytic.account', 'Analytic Account'),
        'second_partner_id': fields.many2one('res.partner', 'Second Partner'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'second_partner_id': fields.many2one('res.partner', 'Second Partner'),
        'date_from':fields.date('Date From'),
        'date_to':fields.date('Date To'),
        'amount_from': fields.float('Amount From'),
        'amount_to': fields.float('Amount To'),
        'target_move':fields.selection([('all','All'),('posted','posted'), ],'Target Move'),
        'report_line_ids': fields.one2many('custody.report.line', 'report_id', 'Lines'),
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'group_report': fields.boolean('Group the report',),
        'remove_date_from':fields.date('Remove Date From'),
        'remove_date_to':fields.date('Remove Date To'),
        'end_date_from':fields.date('End Date From'),
        'end_date_to':fields.date('End Date To'),
        'report_type': fields.selection([('detail','Detail'),('grouped','Grouped'),('name_only','Name Only'), ],'Report Type'),
    }

    _defaults = {
        'ready_print': False,
        'custody_state':'all',
        'target_move':'all',
        'date_from':time.strftime('%Y-01-01'),
        'date_to': time.strftime('%Y-%m-%d'),
        'remove_date_from':time.strftime('%Y-01-01'),
        'remove_date_to': time.strftime('%Y-%m-%d'),
        'report_type':'detail',
    }
    
    def onchange_custody_state(cr, uid, ids, context, custody_state):
        """ If Custody state field is Null then change report_type field value to detail"""
        res = {}
        if not custody_state:
            res.update({'value': {'report_type':'detail'} })
        return res  

    def get_report(self, cr, uid, ids, context=None):
        report_line_obj = self.pool.get('custody.report.line')
        voucher_line_obj = self.pool.get('account.voucher.line')
        voucher_obj = self.pool.get('account.voucher')
        department_obj = self.pool.get('hr.department')
        partner_obj = self.pool.get('res.partner')
        form = self.browse(cr, uid, ids[0])
        voucher_posted_ids  = voucher_obj.search(cr, uid , [('state','=','posted')])
        domain = [('voucher_id','in', voucher_posted_ids), ('date','>=',form['date_from']),('date','<=',form['date_to'])]
        if form.custody_state == 'removed':
            domain.append(('date','>=',form['remove_date_from']))
            domain.append(('date','<=',form['remove_date_to']))
        if form.custody_state == 'not removed' and form.end_date_from:
            domain.append(('custody_end_date','>=',form['end_date_from']))
        if form.custody_state == 'not removed' and form.end_date_to:
            domain.append(('custody_end_date','<=',form['end_date_to']))
        if form.custody_state:
            domain.append(('custody','=',True))
        if form.partner_id:
            domain.append(('res_partner_id','=',form.partner_id.id))
        if form.dest_approve:
            domain.append(('dest_approve','=',form.dest_approve.id))
        if form.account_analytic_id:
            domain.append(('account_analytic_id','=',form.account_analytic_id.id))
        if form.second_partner_id:
            domain.append(('second_partner_id','=',form.second_partner_id.id))
        if form.custody_state == 'removed':
            domain.append(('custody_state','=','removed'))
        if form.custody_state == 'not removed':
            domain.append(('custody_state','=','not removed'))
        if form.amount_from:
            domain.append(('amount','>=',form.amount_from))
        if form.amount_to:
            domain.append(('amount','<=',form.amount_to))
        if form.name:
            domain.append(('name','ilike',form.name))
        if form.chk_seq:
            voucher_ids  = voucher_obj.search(cr, uid , [('chk_seq','ilike',form.chk_seq)])
            domain.append(('voucher_id','in', voucher_ids))
        if form.currency_id:
            voucher_ids  = voucher_obj.search(cr, uid , [('currency_id','=',form.currency_id.id)])
            domain.append(('voucher_id','in', voucher_ids))
        if form.permission:
            domain.append(('permission','ilike',form.permission))
        if form.department_id:
            department_ids = department_obj.search(cr, uid, [('parent_id','child_of',form.department_id.id)], context=context)
            partner_ids = partner_obj.search(cr, uid, [('department_id','in',department_ids)], context=context)
            domain.append(('res_partner_id','in', partner_ids))

        voucher_line_ids = voucher_line_obj.search(cr, uid, domain)

        voucher_lines = voucher_line_obj.browse(cr, uid, voucher_line_ids)
        report_line_obj.unlink(cr,uid,[line.id for line in self.browse(cr, uid, ids[0]).report_line_ids])
        for line in voucher_lines:
            report_line_obj.create(cr, uid, {
                                            'date': line.date,
                                            'move_id': line.voucher_id.move_id.id,
                                            'voucher_line_id': line.id,
                                            'partner_code': line.res_partner_id and line.res_partner_id.code,
                                            'partner_id': line.res_partner_id and line.res_partner_id.id,
                                            'second_partner_id': line.second_partner_id and line.second_partner_id.id,
                                            'chk_seq': line.voucher_id.chk_seq or line.permission,
                                            'name': line.name,
                                            'amount': line.amount,
                                            'account_analytic_id': line.account_analytic_id.id,
                                            'currency_id': line.voucher_id.currency_id.id,
                                            'report_id': ids[0],
                                            })
        self.write(cr, uid, ids[0], {'ready_print' : True})
    def print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, ids[0], {'ready_print' : False})
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['custody_state','target_move', 'date_from', 'date_to', 'end_date_from', 'end_date_to', 'partner_id','dest_approve','account_analytic_id','report_line_ids', 'currency_id','group_report','remove_date_from', 'remove_date_to','department_id','report_type' ],)[0]
        return {'type': 'ir.actions.report.xml', 'report_name': 'employee.custody', 'datas': data}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
