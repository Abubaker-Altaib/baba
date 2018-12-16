# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

"""
Account balance report templates

Generic account balance report template that will be used to define
accounting concepts with formulas to calculate its values/balance.
Designed following the needs of the Spanish/Spain localization.
"""

from openerp.osv import fields, osv
import re
import time
from openerp.tools.translate import _

_BALANCE_MODE_HELP = """Formula calculation mode: Depending on it, the balance is calculated as follows:
  Mode 0: debit-credit (default);
  Mode 1: debit-credit, credit-debit for accounts in brackets;
  Mode 2: credit-debit;
  Mode 3: credit-debit, debit-credit for accounts in brackets."""

_VALUE_FORMULA_HELP = """Value calculation formula: Depending on this formula the final value is calculated as follows:
  Empy template value: sum of (this concept) children values.
  Number with decimal point ("10.2"): that value (constant).
  Account numbers separated by commas ("430,431,(437)"): Sum of the account balances
    (the sign of the balance depends on the balance mode).
  Concept codes separated by "+" ("11000+12000"): Sum of those concepts values.
"""

#---------------------------------------------------
# CSS classes for the account lines
#---------------------------------------------------
CSS_CLASSES = [('default','Default'),('l1', 'Level 1'), ('l2', 'Level 2'),
                ('l3', 'Level 3'), ('l4', 'Level 4'), ('l5', 'Level 5')]


#---------------------------------------------------
# Account balance report template (document/header)
#---------------------------------------------------
class account_balance_reporting_template(osv.Model):
    """
    Account balance report template.
    It stores the header fields of an account balance report template,
    and the linked lines of detail with the formulas to calculate
    the accounting concepts of the report.
    """
    
    _name = "account.balance.reporting.template"

    _columns = {
        'name': fields.char('Name', size=64, required=True, select=True),

        'type': fields.selection([('system','System'),('user','User')], 'Type'),

        'report_xml_id': fields.many2one('ir.actions.report.xml', 'Report design', ondelete='set null'),

        'description': fields.text('Description'),

        'balance_mode': fields.selection([('0','Debit-Credit'),('1','Debit-Credit, reversed with brakets'),('2','Credit-Debit'),
                                          ('3','Credit-Debit, reversed with brakets')], 'Balance mode', help=_BALANCE_MODE_HELP),
        #3: debit/credit, 5: amount - debit/credit, 4: move without details, 1: move with details, 2: year compare
        'rml': fields.selection([('1','Debit/Credit'),('2','Amount - Debit/Credit'),('3','Move Without Details'),('4','Move With Details'),('5','Tow Years Comparison'),('h4','4 Horizantal'),('h5','4 Horizantal')], 'RML', required=True),
        #'rml': fields.selection([('3','Trial Balance'),('5','Addtions'),('4','Changes in Equity'),('1','Profit & Loss/Balance Sheet'),('2','Cash Flow')], 'RML', required=True),
        'cash_report': fields.boolean('Cash'),
    }

    _defaults = {
        'type': 'user',
        'balance_mode': '0',
	    'rml': '4',
    }

    def copy(self, cr, uid, id, default=None, context=None):
        """
        Redefine the copy method to perform it correctly as the line
        structure is a graph.
        """
        line_facade = self.pool.get('account.balance.reporting.template.line')
        # Read the current item data:
        template = self.browse(cr, uid, id, context=context)
        # Create the template
        new_id = self.create(cr, uid, {
                    'name': '%s*' % template.name, # We change the name to identify the copy
                    'type': 'user', # Copies are always user templates
                    'report_xml_id': template.report_xml_id.id,
                    'description': template.description,
                    'balance_mode': template.balance_mode,
                    'line_ids': None,
                }, context=context)
        # Now create the lines (without parents)
        for line in template.line_ids:
            line_facade.create(cr, uid, {
                    'report_id': new_id,
                    'sequence': line.sequence,
                    'css_class': line.css_class,
                    'code': line.code,
                    'name': line.name,
                    'current_value': line.current_value,
                    'previous_value': line.previous_value,
                    'negate': line.negate,
                    'parent_id': None,
                    'child_ids': None,
                    'detail_account_ids':[(6, 0, [x.id for x in line.detail_account_ids])],
                }, context=context)
        # Now set the (lines) parents
        for line in template.line_ids:
            if line.parent_id:
                # Search for the copied line
                new_line_id = line_facade.search(cr, uid, [('report_id', '=', new_id), ('code', '=', line.code)], context=context)[0]
                # Search for the copied parent line
                new_parent_id = line_facade.search(cr, uid, [('report_id', '=', new_id), ('code', '=', line.parent_id.code)], context=context)[0]
                # Set the parent
                line_facade.write(cr, uid, new_line_id, {'parent_id': new_parent_id}, context=context)
        return new_id



#---------------------------------------------------
# Account balance report template line of detail (accounting concept template)
#---------------------------------------------------
class account_balance_reporting_template_line(osv.Model):
    """
    Account balance report template line / Accounting concept template
    One line of detail of the balance report representing an accounting
    concept with the formulas to calculate its values.
    The accounting concepts follow a parent-children hierarchy.
    """
    
    _name = "account.balance.reporting.template.line"

    _columns = {
        'report_id': fields.many2one('account.balance.reporting.template', 'Template', ondelete='cascade'),

        'sequence': fields.char('Sequence', size=32, required=False, help="Lines will be sorted/grouped by this field"),

        'css_class': fields.selection(CSS_CLASSES, 'CSS Class', required=False, help="Style-sheet class"),

        'code': fields.char('Code', size=64, required=True, select=True, help="Concept code, may be used on formulas to reference this line"),

        'name': fields.char('Name', size=256, required=True, select=True, help="Concept name/description"),

        'current_value': fields.text('Fiscal year 1 formula', help=_VALUE_FORMULA_HELP),

        'previous_value': fields.text('Fiscal year 2 formula', help=_VALUE_FORMULA_HELP),

        'negate': fields.boolean('Negate', help="Negate the value (change the sign of the balance)"),

        'parent_id': fields.many2one('account.balance.reporting.template.line', 'Parent', ondelete='cascade'),

        'child_ids': fields.one2many('account.balance.reporting.template.line', 'parent_id', 'Children'),

        'detail': fields.boolean('Has Disclosure', help="Is this Line has Disclosure"),

        'detail_account_ids': fields.many2many('account.account', 'account_detail_temp_rel', 'temp_line_id', 'account_id', 'Disclosure Accounts'), 

        'disclosure_number': fields.integer('Disclosure Number'), 
        'currency_id': fields.many2one('res.currency', 'Currency'),

    }

    _defaults = {
        'report_id': lambda self, cr, uid, context: context.get('report_id', None),
        'negate': False,
        'css_class': 'default',
    }

    _order = "sequence, code"
    
    _sql_constraints = [('report_code_uniq', 'unique (report_id,code)', _("The code must be unique for this report!"))]

    def name_get(self, cr, uid, ids, context=None):
        """ Line name show as "[code] name" """
        return ids and [(item.id, "[%s] %s" % (item.code, item.name)) for item in self.browse(cr, uid, ids, context=context)] or []

    def name_search(self, cr, uid, name, args=[], operator='ilike', context={}, limit=80):
        """ Allow searching by line name or code """        
        ids = name and self.search(cr, uid, [('code','ilike',name)]+ args,  context=context, limit=limit) or []
        if not ids:
            ids = self.search(cr, uid, [('name',operator,name)]+ args,  context=context, limit=limit)
        return self.name_get(cr, uid, ids, context=context)



class account_account(osv.Model):

    _inherit = "account.account"

    _columns = {

        'templete_line_id': fields.many2one('account.balance.reporting.template.line', 'Template Line'),
    }



class account_balance_reporting_template_withlines(osv.Model):
    """
    Extend the 'account balance report template' to add a link to its
    lines of detail.
    """

    _inherit = "account.balance.reporting.template"

    _columns = {
        'line_ids': fields.one2many('account.balance.reporting.template.line', 'report_id', 'Lines'),
        'column_ids': fields.one2many('account.balance.reporting.template.sequence', 'report_id', 'Columns'),
    }



class account_balance_reporting_template_sequence(osv.Model):

    _name = "account.balance.reporting.template.sequence"
    _description = "Header columns for the template"

    def _check_sequence(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.sequence > 8 or obj.sequence < 1 or len(self.search(cr, uid, [('id','!=',obj.id),('sequence','=',obj.sequence)]))>0 :
                    return False
        return True

    _columns = {
        'report_id': fields.many2one('account.balance.reporting.template', 'Template', ondelete='cascade'), 
        'name': fields.char('Name', size=256, required=True, select=True, help="Concept name/description"),
        'sequence': fields.integer('Sequence', required=True, help="Lines will be sorted/grouped by this field"),

               }
    _constraints = [
        (_check_sequence, 'The sequence of columns must be between one and eight and must be unique.', ['sequence']),
                     ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
