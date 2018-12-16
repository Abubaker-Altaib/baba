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

class strategic_objective_project(osv.Model):
    _name = 'strategic.plan.goal'
    _description = 'Strategic objective project'
    _columns = {
        'goal_id': fields.many2one('strategic.goal', 'Goal', required=True),
        'weight': fields.float('Weight'),
        'expected': fields.related('goal_id', 'expected', type='float', relation='strategic.goal', 
                                     string='Expected', readonly=True),
        'actual': fields.related('goal_id', 'actual', type='float', relation='strategic.goal', 
                                     string='Actual', readonly=True),
        'plan_id': fields.many2one('strategic.plan', 'dsfds Pla   n'),
		
    }	
class strategic_plan(osv.Model):
    _name = 'strategic.plan'
    _description = 'Strategic Plan'
    _order = 'sequence'

    def _progress(self, cr, uid, ids, field_name, arg, context=None):
	res = {}
	for obj in self.browse(cr, uid, ids, context=context):
	    actual = 0.0	
            expected = 0.0
	    for l in obj.goal_line_ids:
	       actual += l.weight    * l.actual / 100
	       expected += l.weight  * l.expected / 100
	    res[obj.id] = {'actual':actual , 'expected':expected}
	return res
        '''case_default': fields.boolean('Default for New Goals',
                        help="If you check this field, this plan will be proposed by default on each new project. It will not assign this stage to existing projects."),
        fold': fields.boolean('Folded in Kanban View',
                               help='This plan is folded in the kanban view when'
                               'there are no goals in that plan to display.'),
		'''
    _columns = {
        'name': fields.char('Plan Name', required=True,  translate=True),
        'description': fields.text('Description'),
        'sequence': fields.integer('Sequence'),
	'date_start': fields.date('Start Date', select=True, copy=False),
        'date_end': fields.date('End Date', select=True, copy=False),	
        'goal_line_ids': fields.one2many('strategic.plan.goal', 'plan_id', 'plan'),

        'expected':fields.function(_progress, method=True , string='Current Expected Progress', type='float', multi='sums'), 
        'actual':fields.function(_progress, method=True , string='Current Actual Progress', type='float', multi='sums'),  
    }
	
	# TODO: Why not using a SQL contraints ?
    def _check_dates(self, cr, uid, ids, context=None):
        for leave in self.read(cr, uid, ids, ['date_start', 'date_end'], context=context):
            if leave['date_start'] and leave['date_end']:
                if leave['date_start'] > leave['date_end']:
                    return False
        return True

    _constraints = [
        (_check_dates, 'Error! project start-date must be lower then project end-date.', ['date_start', 'date_end'],)
    ]
	
class strategic_goal_objective(osv.Model):
    _name = 'strategic.goal.objective'
    _description = 'Strategic goal objective'
    _columns = {
        'objective_id': fields.many2one('strategic.objective', 'Objective', required=True),
        'weight': fields.float('Weight'),
        'expected': fields.related('objective_id', 'expected', type='float', relation='strategic.objective', 
                                     string='Expected', readonly=True),
        'actual': fields.related('objective_id', 'actual', type='float', relation='strategic.objective', 
                                     string='Actual', readonly=True),
        'goal_id': fields.many2one('strategic.goal', 'Objective'),
		
    }		
class strategic_goal(osv.Model):
    _name = 'strategic.goal'
    _description = 'Strategic Goal'
    _order = 'sequence'
    def _progress(self, cr, uid, ids, field_name, arg, context=None):
	res = {}
	for obj in self.browse(cr, uid, ids, context=context):
	    actual = 0.0	
            expected = 0.0
	    for l in obj.objective_line_ids:
	       actual += l.weight    * l.actual / 100
	       expected += l.weight  * l.expected / 100
	    res[obj.id] = {'actual':actual , 'expected':expected}
	return res
    _columns = {
        'name': fields.char('Goal', required=True, translate=True),
        'responsible': fields.char('Responsible'),
        'description': fields.text('Description'),
        'sequence': fields.integer('Sequence'),
	'date_start': fields.date('Start Date', select=True, copy=False),
        'date_end': fields.date('End Date', select=True, copy=False),
	'plan_id': fields.many2one('strategic.plan', 'Plan', ondelete='set null',select=True,),
        'expected':fields.function(_progress, method=True , string='Current Expected Progress', type='float', multi='sums'), 
        'actual':fields.function(_progress, method=True , string='Current Actual Progress', type='float', multi='sums'),  
        'objective_line_ids': fields.one2many('strategic.goal.objective', 'goal_id', 'objective'),
		
    }
	
class strategic_objective(osv.Model):
    _name = 'strategic.objective'
    _description = 'Strategic objective'
    _order = 'sequence'

    def _progress(self, cr, uid, ids, field_name, arg, context=None):
	res = {}
	for obj in self.browse(cr, uid, ids, context=context):
	    actual = 0.0	
            expected = 0.0
	    for l in obj.project_line_ids:
	       actual += l.weight    * l.actual / 100
	       expected += l.weight  * l.expected / 100
	    res[obj.id] = {'actual':actual , 'expected':expected}
	return res

    _columns = {
        'name': fields.char('Objective', required=True, translate=True),
        'responsible': fields.char('Responsible'),
        'description': fields.text('Description'),
        'sequence': fields.integer('Sequence'),
	'date_start': fields.date('Start Date', select=True, copy=False),
        'date_end': fields.date('End Date', select=True, copy=False),
	'goal_id': fields.many2one('strategic.goal', 'Goal', ondelete='set null',select=True,),
        'kpi_line_ids': fields.one2many('strategic.objective.kpi', 'objective_id', 'KPIs'),
        'project_line_ids': fields.one2many('strategic.objective.project', 'objective_id', '--'),
        'objective_id': fields.many2one('strategic.goal', 'goal'),
        'actual':fields.function(_progress, method=True , string='Current Actual Progress', type='float', multi='sums'),   
        'expected':fields.function(_progress, method=True , string='Current Expected Progress', type='float', multi='sums'), 		
    }	

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
    _name = 'strategic.objective.kpi'
    _description = 'Strategic objective KPI'
    _columns = {
        'name': fields.char('KPI', required=True, translate=True),
        'weight': fields.float('Weight'),
        'expected': fields.float('Current Expected Progress'),
        'actual': fields.float('Current Actual Progress'),
        'objective_id': fields.many2one('strategic.objective', 'Objective'),
		
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

class project(osv.Model):
    _name = 'project'
    _description = 'Project'
    _order = 'sequence'

    def _progress(self, cr, uid, ids, field_name, arg, context=None):
	res = {}
	for project in self.browse(cr, uid, ids, context=context):
	    actual = 0.0	
            expected = 0.0
	    for l in project.project_line_ids:
	       actual += l.weight * l.actual / 100
	       if time.strftime('%Y-%m-%d') < l.date_end: continue
	       expected += l.weight  
	    res[project.id] = {'actual':actual , 'expected':expected}
	return res
    _columns = {
        'name': fields.char('project', required=True, translate=True),
        'responsible': fields.char('Responsible'),
        'description': fields.text('Description'),
        'sequence': fields.integer('Sequence'),
        'expected':fields.function(_progress, method=True , string='Current Expected Progress', type='float', multi='sums'), 
        'actual':fields.function(_progress, method=True , string='Current Actual Progress', type='float', multi='sums'),   

        'periodic' : fields.selection([('monthly','Mponthly'),('quartly','quartly'),
                                   ('yearly','yearly')], 'Type'),
        'project_line_ids': fields.one2many('project.lines', 'project_id', 'projects'),
		
    }	
class strategic_objective_project(osv.Model):
    _name = 'strategic.objective.project'
    _description = 'Strategic objective project'
    _columns = {
        'project_id': fields.many2one('project', 'project', required=True),
        'weight': fields.float('Weight'),
        'expected': fields.related('project_id', 'expected', type='float', relation='project', 
                                     string='Expected', readonly=True),
        'actual': fields.related('project_id', 'actual', type='float', relation='project', 
                                     string='Actual', readonly=True),
        'objective_id': fields.many2one('strategic.objective', 'Objective'),
		
    }	
class project_lines(osv.Model):
    _name = 'project.lines'
    _description = 'project lines'
    _order = 'date_end'
    _columns = {
        'name': fields.char('Task', required=True),	
	'weight': fields.float('Weight'),
        'date_start': fields.date('Start Date', select=True, copy=False),
        'date_end': fields.date('End Date', select=True, copy=False),
        'actual': fields.float('Current Actual Progress'),
        'project_id': fields.many2one('project', 'project'),
		
    }	


''' 'actual':fields.function(_progress, method=True , string='Current Actual Progress', type='float', 
                        store={
                            'strategic.objective': (lambda self, cr, uid, ids, c={}: ids, ['project_line_ids'], 10),
                        }, multi='sums'),   
        'expected':fields.function(_progress, method=True , string='Current Expected Progress', type='float', 
                        store={
                            'strategic.objective': (lambda self, cr, uid, ids, c={}: ids, ['project_line_ids'], 10),
                        }, multi='sums'), 	

'''
