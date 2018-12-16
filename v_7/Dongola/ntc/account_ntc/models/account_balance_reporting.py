# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
############################################################################
from openerp.osv import fields, osv, orm
from tools.translate import _
import re

class account_balance_reporting(osv.osv):

    _inherit = "account.balance.reporting.line"

    _columns = {
        ######### fields for change in owner equity use##########
        # Concept value 
        'value1': fields.float('Value 1', digits=(16,2)),
        'value1_prev': fields.float('Value 1 previous', digits=(16,2)),
        # Concept value 
        'value2':fields.float('Value 2', digits=(16,2)),
        'value2_prev': fields.float('Value 2 previous', digits=(16,2)),
        # Concept value 
        'value3': fields.float('Value 3', digits=(16,2)),
        'value3_prev': fields.float('Value 3 previous', digits=(16,2)),
        # Concept value 
        'value4': fields.float('Value 4', digits=(16,2)),
        'value4_prev': fields.float('Value 4 previous', digits=(16,2)),
        #########################################################
        }
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
        for line in self.browse(cr, uid, ids):
            current_value = 0.0
            previous_value = 0.0

            value1 = 0.0 ##
            value1_prev = 0.0
            value2 = 0.0 ##
            value2_prev = 0.0
            value3 = 0.0 ##
            value3_prev = 0.0
            value4 = 0.0 ##
            value4_prev = 0.0
            

            #
            # We use the same code to calculate both fiscal year values,
            # just iterating over them.
            #
            for fyear in ('current', 'previous', 'value1', 'value1_prev',  'value2', 'value2_prev', 'value3', 'value3_prev', 'value4', 'value4_prev'):
                value = 0
                if fyear == 'current':
                    template_value = line.template_line_id.current_value

                elif fyear == 'previous':

                    template_value = line.template_line_id.previous_value


#####   
                elif fyear == 'value1':                        
                    template_value = line.template_line_id.value1
                elif fyear == 'value1_prev':                        
                    template_value = line.template_line_id.value1_prev


                elif fyear == 'value2':                        
                    template_value = line.template_line_id.value2
                elif fyear == 'value2_prev':                        
                    template_value = line.template_line_id.value2_prev


                elif fyear == 'value3':                        
                    template_value = line.template_line_id.value3
                elif fyear == 'value3_prev':                        
                    template_value = line.template_line_id.value3_prev


                elif fyear == 'value4':                        
                    template_value = line.template_line_id.value4
                elif fyear == 'value4_prev':                        
                    template_value = line.template_line_id.value4_prev                


#####
              # Remove characters after a ";" (we use ; for comments)
                if template_value and len(template_value):
                    template_value = template_value.split(';')[0]

                if (fyear == 'current' and not line.report_id.current_fiscalyear_id) \
                        or (fyear == 'previous' and not line.report_id.previous_fiscalyear_id):
                    value = 0
                else:
                    #
                    # Calculate the value
                    #
                    if not template_value or not len(template_value):
                        #
                        # Empy template value => sum of the children, of this concept, values.
                        #
                        for child in line.child_ids:
                            # Tell the child to refresh its values
                            child.refresh_values()
                            # Reload the child data
                            child = self.browse(cr, uid, [child.id])[0]
                            if fyear == 'current':
                                value += float(child.current_value)

                            elif fyear == 'previous':
                                value += float(child.previous_value)


                            elif fyear == 'value1':
                                value += float(child.value1)

                            elif fyear == 'value2':
                                value += float(child.value2)

                            elif fyear == 'value3':
                                value += float(child.value3)

                            elif fyear == 'value4':
                                value += float(child.value4)


                            elif fyear == 'value1_prev':
                                value += float(child.value1_prev)

                            elif fyear == 'value2_prev':
                                value += float(child.value2_prev)

                            elif fyear == 'value3_prev':
                                value += float(child.value3_prev)

                            elif fyear == 'value4_prev':
                                value += float(child.value4_prev)
                            



                            
                    elif re.match(r'^\-?[0-9]*\.[0-9]*$', template_value):
                        #
                        # Number with decimal points => that number value (constant).
                        #
                        value = float(template_value)


                    elif re.match(r'^[0-9a-zA-Z,\(\)\*_]*$', template_value):
                        #
                        # Account numbers separated by commas => sum of the account balances.
                        #
                        # We will use the context to filter the accounts by fiscalyear
                        # and periods.
                        #
                        if fyear == 'current':
                            ctx = {
                                'fiscalyear': line.report_id.current_fiscalyear_id.id,
                                'periods': [p.id for p in line.report_id.current_period_ids],
                            }

                        elif fyear == 'previous':
                            ctx = {
                                #'fiscalyear': line.report_id.previous_fiscalyear_id.id,
                                'periods': [p.id for p in line.report_id.previous_period_ids],
                            }

#######
                        elif fyear == 'value1':
                            ctx = {
                                #'fiscalyear': line.report_id.current_fiscalyear_id.id,
                                'periods': [p.id for p in line.report_id.current_period_ids],
                            }  
                        elif fyear == 'value1_prev':
                            ctx = {
                                #'fiscalyear': line.report_id.current_fiscalyear_id.id,
                                'periods': [p.id for p in line.report_id.previous_period_ids],
                            }          
                        elif fyear == 'value2':
                            ctx = {
                                'fiscalyear': line.report_id.current_fiscalyear_id.id,
                                'periods': [p.id for p in line.report_id.current_period_ids],
                            } 
                        elif fyear == 'value2_prev':
                            ctx = {
                                #'fiscalyear': line.report_id.current_fiscalyear_id.id,
                                'periods': [p.id for p in line.report_id.previous_period_ids],
                            }                    
                        elif fyear == 'value3':
                            ctx = {
                                #'fiscalyear': line.report_id.current_fiscalyear_id.id,
                                'periods': [p.id for p in line.report_id.current_period_ids],
                            } 
                        elif fyear == 'value3_prev':
                            ctx = {
                                #'fiscalyear': line.report_id.current_fiscalyear_id.id,
                                'periods': [p.id for p in line.report_id.previous_period_ids],
                            }                    
                        elif fyear == 'value4':
                            ctx = {
                                #'fiscalyear': line.report_id.current_fiscalyear_id.id,
                                'periods': [p.id for p in line.report_id.current_period_ids],
                            }
                        elif fyear == 'value4_prev':
                            ctx = {
                                #'fiscalyear': line.report_id.current_fiscalyear_id.id,
                                'periods': [p.id for p in line.report_id.previous_period_ids],
                            }                
######                           
                        

                        # Get the mode of balance calculation from the template
                        balance_mode = line.template_line_id.report_id.balance_mode

                        # Get the balance
                        value = line._get_account_balance(template_value, balance_mode, ctx)

                    elif re.match(r'^[\+\-0-9a-zA-Z_\*]*$', template_value):
                        #
                        # Account concept codes separated by "+" => sum of the concept (report lines) values.
                        #
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
                                line_ids = self.search(cr, uid, [
                                        ('report_id','=', line.report_id.id),
                                        ('code', '=', line_code),
                                    ])
                                for child in self.browse(cr, uid, line_ids):
                                    # Tell the child to refresh its values
                                    child.refresh_values()
                                    # Reload the child data
                                    child = self.browse(cr, uid, [child.id])[0]
                                    if fyear == 'current':
                                        value += float(child.current_value) * sign


                                    elif fyear == 'previous':
                                        value += float(child.previous_value) * sign

                                    elif fyear == 'value1':
                                        value += float(child.value1) * sign
                                    elif fyear == 'value2':
                                        value += float(child.value2) * sign

                                    elif fyear == 'value3':
                                        value += float(child.value3) * sign

                                    elif fyear == 'value4':
                                        value += float(child.value4) * sign

                                    elif fyear == 'value1_prev':
                                        value += float(child.value1_prev) * sign

                                    elif fyear == 'value2_prev':
                                        value += float(child.value2_prev) * sign

                                    elif fyear == 'value3_prev':
                                        value += float(child.value3_prev) * sign

                                    elif fyear == 'value4_prev':
                                        value += float(child.value4_prev) * sign



#'current', 'previous', 'value1', 'value1_prev',  'value2', 'value2_prev', 'value3', 'value3_prev', 'value4', 'value4_prev'


                #
                # Negate the value if needed
                #
                if line.template_line_id.negate:
                    value = -value

                if fyear == 'current':
                    current_value = value
                elif fyear == 'previous':
                    previous_value = value
####
                elif fyear == 'value1':
                    value1 = value
                elif fyear == 'value1_prev':
                    value1_prev = value
                elif fyear == 'value2':
                    value2 = value
                elif fyear == 'value2_prev':
                    value2_prev = value
                elif fyear == 'value3':
                    value3 = value
                elif fyear == 'value3_prev':
                    value3_prev = value
                elif fyear == 'value4':
                    value4 = value
                elif fyear == 'value4_prev':
                    value4_prev = value
####
            # Write the values

            self.write(cr, uid, [line.id], {
                    'current_value': current_value,
                    'previous_value': previous_value,
                    'value1': value1,
                    'value1_prev': value1_prev,
                    'value2': value2,
                    'value2_prev': value2_prev,
                    'value3': value3,
                    'value3_prev': value3_prev,
                    'value4': value4,
                    'value4_prev': value4_prev,
                })
        return True

class account_balance_reporting_template_line(osv.osv):
    """
    Account balance report template line / Accounting concept template
    One line of detail of the balance report representing an accounting
    concept with the formulas to calculate its values.
    The accounting concepts follow a parent-children hierarchy.
    """

    _inherit = "account.balance.reporting.template.line"

    _columns = {
        ######### fields for change in owner equity use##########
        # Concept value 
        'value1': fields.text('Value 1'),
        'value1_prev': fields.text('Value 1 previous'),
        # Concept value 
        'value2':fields.text('Value 2'),
        'value2_prev': fields.text('Value 2 previous'),
        # Concept value 
        'value3': fields.text('Value 3'),
        'value3_prev': fields.text('Value 3 previous'),
        # Concept value 
        'value4': fields.text('Value 4'),
        'value4_prev': fields.text('Value 4 previous'),
        #########################################################
        }
