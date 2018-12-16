# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2018 NCTR (<http://www.nctr.sd>).
#
##############################################################################
from odoo import api , fields, models,_
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import *
from datetime import date, datetime, timedelta



class budget_comparsion_wizard(models.TransientModel):
    _name = "budget.comparsion.wizard"

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', required=True)
    start_date = fields.Date('Date From')
    end_date = fields.Date('Date To')




    def print_budget_comparsion_report(self):
        """
        Print Budget Comparsion REport to compare current budget againts previous budget
        :return:
        """

        if self.start_date > self.end_date:
            raise ValidationError(_("""You Must Set 'Date From' less Than 'Date To'."""))


        date_start = datetime.strptime(self.start_date, '%Y-%m-%d')
        date_end = datetime.strptime(self.end_date, '%Y-%m-%d')
        new_date_start = date_start - relativedelta(years=1)

        budget = self.env['crossovered.budget'].search([
            ('analytic_account_id','=',self.analytic_account_id.id),
            ('date_from','>=',new_date_start),('date_to','<=',self.end_date)
        ],order="date_from")

        first_budget = [] #to store prev budget
        second_budget = [] # to store current budget
        damage_budget = [] #to store diff's
        count = 0
        if len(budget) == 2:
            for bud in budget:
                count += 1
                for line in bud.crossovered_budget_line:
                    if count==1:
                        first_budget.append([line.general_budget_id.id,line.general_budget_id.name ,line.planned_amount,line.practical_amount,bud.date_from])
                    else:
                        second_budget.append([line.general_budget_id.id,line.general_budget_id.name ,line.planned_amount,line.practical_amount,bud.date_from])


            for budget1 in first_budget:
                is_equal = True
                for budget2 in second_budget:

                    if budget1[0] == budget2[0]:
                        is_equal=False
                        damage_budget.append([budget1[1],
                                              budget1[2],
                                              budget1[3],
                                              budget2[2],
                                              (float(budget2[2])-float(budget1[2])),
                                              round((((float( budget2[2])-float(budget1[2]))/float( budget1[2]))*100),2)])
                if is_equal:
                    damage_budget.append([budget1[1], budget1[2],budget1[3],'-','-','-'])

            for budget2 in second_budget:
                is_equal = True
                for budget1 in first_budget:

                    if budget2[0] == budget1[0]:
                        is_equal=False

                if is_equal:
                    damage_budget.append([budget2[1],'-','-',budget2[2],'-','-'])

        else:
            raise ValidationError(_("""Must Excatly Be Two Budget to compare, More than Two budget or No Budget At all !!'."""))



        data = {}
        data.update({'report_data':damage_budget})

        data.update({'time_now': fields.datetime.now()})
        data.update({'date_from': new_date_start})
        data.update({'date_to': self.end_date})

        return self.env.ref('account_budget_custom.action_budget_comparsion').with_context(landscape=True).report_action(
            self, data=data)





class budgetComparsion(models.AbstractModel):
    _name = 'report.account_budget_ebs.budget_comparsion'



    @api.model
    def get_report_values(self, docids, data=None):
        print("ABSTRACT ", data)
        if len(data.get('report_data')) == 0 :
            raise UserError(_("No Data , this report cannot be printed."))

        return {
            'doc_ids': 1,
            'data': data,
            'docs': self.env['account.account'].search([('id', 'in',(1,2) )]),#data['ids']

        }

