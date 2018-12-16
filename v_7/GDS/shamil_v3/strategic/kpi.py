# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import datetime, date
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _

class kpi(osv.Model):
    _name = 'kpi'
    _description = 'KPI'
    _order = 'sequence'
    _columns = {
        'name': fields.char('KPI', required=True, translate=True),
        'description': fields.text('Description'),
        'sequence': fields.integer('Sequence'),
        'expected': fields.float('Current Expected Progress'),
        'actual': fields.float('Current Actual Progress'),
        'periodic' : fields.selection([('monthly','Mponthly'),('quartly','quartly'),
                                   ('yearly','yearly')], 'Type'),
        'kpi_line_ids': fields.one2many('kpi.lines', 'kpi_id', 'KPIs'),
		
    }	
class strategic_objective_kpi(osv.Model):
    _name = 'strategic.strategic.kpi'
    _description = 'Strategic objective KPI'
    _columns = {
        'name': fields.char('KPI', required=True, translate=True),
        'weight': fields.float('Weight'),
        'expected': fields.float('Current Expected Progress'),
        'actual': fields.float('Current Actual Progress'),
        'objective_id': fields.many2one('strategic.strategic', 'Objective'),
		
    }	
class kpi_lines(osv.Model):
    _name = 'kpi.lines'
    _description = 'KPI lines'
    _columns = {
	'date_start': fields.date('Start Date', select=True, copy=False),
        'date_end': fields.date('End Date', select=True, copy=False),
        'expected': fields.float('Current Expected Progress'),
        'actual': fields.float('Current Actual Progress'),
        'kpi_id': fields.many2one('kpi', 'KPI'),
		
    }	

