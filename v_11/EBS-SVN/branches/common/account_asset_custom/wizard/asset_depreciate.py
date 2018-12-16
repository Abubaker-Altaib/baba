# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from odoo import api, fields, models, _
from datetime import datetime, timedelta



class asset_depreciate(models.TransientModel):
    """
    Closes Account Fiscalyear and Generate Closing entries for the selected Fiscalyear Profit & loss accounts
    """
    _name = "asset.depreciate"

    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    dept_id = fields.Many2many('hr.department','dept_asset_rel','dept_id','asset_id','Departments')
    category_id = fields.Many2many('account.asset.category','asset_categ_rel','asset_id','categ_id','Asset Category')

    note = fields.Text("Notes")



    def depre(self):
        domain = [('state','=','draft')]

        if self.from_date :
            domain.append(('depreciation_date','>=',self.from_date))
        
        if self.to_date :	
            domain.append(('depreciation_date','<=',self.to_date))
        
        if self.dept_id:
            domain.append(('asset_id.department_id.id','in',self.dept_id.ids))

        if self.category_id:
            domain.append(('asset_id.category_id.id','in',self.category_id.ids))


        assets =self.env['account.asset.depreciation.line'].search(domain)
        
        for line in assets :
            line.create_move()
            line.move_id.state = 'posted'

