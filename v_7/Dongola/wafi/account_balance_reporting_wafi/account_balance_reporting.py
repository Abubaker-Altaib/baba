# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from openerp.osv import osv
import re


#---------------------------------------------------
# Account balance report line of detail (accounting concept)
#---------------------------------------------------
class account_balance_reporting_line(osv.Model):

    _inherit = "account.balance.reporting.line"

    def refresh_values(self, cr, uid, ids, context=None):
        """
        Recalculates the values of this report line using the
        linked line template values formulas:

        Depending on this formula the final value is calculated as follows:
        - Empy template value: sum of (this concept) children values.
        - Number with decimal point ("10.2"): that value (constant).
        - Account numbers separated by commas ("430,431,(437)"): Sum of the account balances.
            (The sign of the balance depends on the balance mode)
        - Concept codes separated by "+" ("11000+12000"): Sum of those concepts values.
        """
        for line in self.browse(cr, uid, ids, context=context):
            current_value = 0.0
            previous_value = 0.0
            debit_value = 0.0
            credit_value = 0.0
            openning_balance=0.0
            # We use the same code to calculate both fiscal year values,
            # just iterating over them.
            for fyear in ('current', 'previous'):
                value = 0
                op_balance = 0
                template_value = (fyear == 'current' and line.template_line_id.current_value) or \
                                 (fyear == 'previous' and line.template_line_id.previous_value) or 0
                # Remove characters after a ";" (we use ; for comments)
                template_value = template_value and len(template_value) and template_value.split(';')[0] or template_value
                if (fyear == 'current' and not line.report_id.current_fiscalyear_id) or \
                       (fyear == 'previous' and not line.report_id.previous_fiscalyear_id): 
                    value = 0
                else:
                    # Calculate the value
                    if not template_value or not len(template_value):
                        # Empy template value => sum of the children, of this concept, values.
                        for child in line.child_ids:
                            # Tell the child to refresh its values
                            child.refresh_values()
                            # Reload the child data
                            child = self.browse(cr, uid, [child.id], context=context)[0]
                            value += (fyear == 'current' and float(child.current_value)) or \
                                     (fyear == 'previous' and float(child.previous_value)) or 0
                    elif re.match(r'^\-?[0-9]*\.[0-9]*$', template_value):
                        # Number with decimal points => that number value (constant).
                        value = float(template_value)
                    elif re.match(r'^[0-9a-zA-Z,\(\)\*_]*$', template_value):
                        # Account numbers separated by commas => sum of the account balances.
                        # We will use the context to filter the accounts by fiscalyear
                        # and periods.
                        ctx = {'selected_journals':True,
                               'fiscalyear': fyear == 'current' and line.report_id.current_fiscalyear_id.id or \
                                            fyear == 'previous' and line.report_id.previous_fiscalyear_id.id,
                               'periods': fyear == 'current' and [p.id for p in line.report_id.current_period_ids] or \
                                        fyear == 'previous' and [p.id for p in line.report_id.previous_period_ids] or []}
                        # Get the mode of balance calculation from the template
                        ccc = ctx.copy()
                        balance_mode = line.template_line_id.report_id.balance_mode
                        value = line._get_account_balance(template_value, balance_mode, context=ccc)
                        #value2 = line._get_account_balance(template_value, balance_mode, context=ccc)
                        # Get the balance
                       # if ctx.get('periods'):
                            #Mudathir
                            #cc = ctx.copy()
                            #op_balance = line._get_account_balance(template_value, balance_mode, context=ctx)

                            #openning_balance = op_balance - value
                        cc = ctx.copy()
                        openning_balance =  line._get_account_balance_custom2(template_value, balance_mode, context=cc)
                        value=value+openning_balance

                    elif re.match(r'^[\+\-0-9a-zA-Z_\*]*$', template_value):
                        # Account concept codes separated by "+" => sum of the concept (report lines) values.
                        for line_code in re.findall(r'(-?\(?[0-9a-zA-Z_]*\)?)', template_value):
                            # Check the sign of the code (substraction)
                            if line_code.startswith('-') or line_code.startswith('('):
                                sign = -1.0
                            else:
                                sign = 1.0
                            line_code = line_code.strip('-()*')
                            # Check if the code is valid (findall might return empty strings)
                            if len(line_code) > 0:
                                # Search for the line (perfect match)
                                line_ids = self.search(cr, uid, [('report_id', '=', line.report_id.id), 
                                                                 ('code', '=', line_code)], context=context)
                                for child in self.browse(cr, uid, line_ids, context=context):
                                    # Tell the child to refresh its values
                                    child.refresh_values()
                                    # Reload the child data
                                    child = self.browse(cr, uid, [child.id], context=context)[0]
                                    if fyear == 'current':
                                        value += float(child.current_value) * sign
                                    elif fyear == 'previous':
                                        value +=    float(child.previous_value) * sign
                # Negate the value if needed
                value = line.template_line_id.negate and -value or value

                if fyear == 'current':                   
                    current_value =  value
                elif fyear == 'previous':
                    previous_value = value
            openning_balance = line.template_line_id.negate and -openning_balance or openning_balance
            if template_value:
                debit='debit'+'('+template_value+')'
                credit='credit'+'('+template_value+')'
                ctx2 = {'selected_journals':True,
                               'fiscalyear':  line.report_id.current_fiscalyear_id.id,
                               'periods':  [p.id for p in line.report_id.current_period_ids] 
                                     }

                debit_value= line._get_account_balance(debit, balance_mode, context=ctx2)
                ctx3 = {'selected_journals':True,
                               'fiscalyear':  line.report_id.current_fiscalyear_id.id,
                               'periods':  [p.id for p in line.report_id.current_period_ids] 
                                     }
                credit_value= line._get_account_balance(credit, balance_mode, context=ctx3)
                #if openning_balance>=0 and credit!=0:
                #credit_value=credit_value+openning_balance
                #if openning_balance<=0 and debit!=0:
                 #   debit_value=debit_value-openning_balance
            # Write the values
            self.write(cr, uid, [line.id], {
                    'current_value': current_value, 
                    'debit': debit_value, 
                    'credit': credit_value, 
                    'previous_value': previous_value,
                    'openning_balance': openning_balance ,
            }, context=context)
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
