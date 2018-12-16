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
from datetime import datetime

class strategic_objective_project(osv.Model):
    _name = 'strategic.strategic.line'
    _description = 'Strategic line'
    _columns = {
        'strategic_id': fields.many2one('strategic.strategic', 'Strategic Plan', required=True),


        'weight': fields.float('Weight'),
        'expected': fields.related('goal_objective_id', 'expected', type='float', relation='strategic.strategic', 
                                     string='Expected', readonly=True),
        'actual': fields.related('goal_objective_id', 'actual', type='float', relation='strategic.strategic', 
                                     string='Actual', readonly=True),
        'type': fields.related('strategic_id', 'type', type='char', relation='strategic.strategic', 
                                     string='Type', readonly=True),
        'goal_objective_id': fields.many2one('strategic.strategic', 'Objective/Goal'),
		
    }	

class strategic_objective_project(osv.Model):
    _name = 'strategic.project.line'
    _description = 'Strategic objective project'
    _columns = {
        'project_id': fields.many2one('project', 'project', required=True),
        'weight': fields.float('Weight'),
        'expected': fields.related('project_id', 'expected', type='float', relation='project', 
                                     string='Expected', readonly=True),
        'actual': fields.related('project_id', 'actual', type='float', relation='project', 
                                     string='Actual', readonly=True),
        'strategic_id': fields.many2one('strategic.strategic', 'strategic'),
		
    }
class strategic_plan(osv.Model):
    _name = 'strategic.strategic'
    _description = 'Strategic Plan'
    _order = 'sequence'
    
    def _get_dic(self, cr, uid, obj, res = {}, lst=False, context={}):
        actual = 0.0	
        expected = 0.0
        lines = context.get('type',False)=='objective' and obj.project_line_ids \
		or obj.strategic_line_ids
	div = obj.type=='plan' and len(lines) or 100
	for l in lines:
	    if context.get('type',False)=='objective' and l.project_id.is_operation:continue
            weight = obj.type=='plan' and 1 or l.weight
	    if lst and res.get(lst.goal_objective_id.id,False):
		act = res[lst.goal_objective_id.id]['actual']
		exp = res[lst.goal_objective_id.id]['expected']
	    elif context.get('project_id',False) and l.project_id.id in context['project_id']:
		act = context['project_id'][l.project_id.id]['actual']
		exp = context['project_id'][l.project_id.id]['expected']		
	    else:
		act = l.actual
		exp = l.expected
            actual += weight * act / div
            expected += weight * exp / div
	res[obj.id] = {'actual':actual , 'expected':expected}
	ides = self.pool.get('strategic.strategic.line').search(cr, uid, [('goal_objective_id','=',obj.id)])
        for lst in self.pool.get('strategic.strategic.line').browse(cr, uid, ides, context=context):
	    res = dict(res.items() + self._get_dic(cr, uid, lst.strategic_id, res, lst).items() ) 
        return res

    def _progress(self, cr, uid, ids, field_name, arg, context=None):
	res = {}
	for obj in self.browse(cr, uid, ids, context=context):
	    res = dict(res.items() + self._get_dic(cr, uid, obj, context=context).items() ) 
	return res


    def _get_c(self, cr, uid, obj, res = [], context={}):
	res = [r.goal_objective_id for r in obj.strategic_line_ids]
	#res += [r.strategic_id for r in obj.strategic_line_ids]
	for l in obj.strategic_line_ids:
	    res = res + self._get_c(cr, uid, l.goal_objective_id, res)
        return res

    def _get_child(self, cr, uid, ids, field_name, arg, context=None):
	result = {}
        line_obj= self.pool.get('strategic.strategic.line')
	for obj in self.browse(cr, uid, ids, context=context):
            res = [obj]
	    res = res + self._get_c(cr, uid, obj , context=context)
            line_ids= line_obj.search(cr,uid,[('goal_objective_id','=',obj.id)], context=context)
            strategic_ids = [l.strategic_id.id for l in line_obj.browse(cr, uid,line_ids, context)]
            lines=self.browse(cr, uid,strategic_ids, context=context)
            res+=lines
            if obj.type == 'objective':
               line_ids= line_obj.search(cr,uid,[('goal_objective_id','in',strategic_ids)], context=context)
               lines=self.browse(cr, uid,[l.strategic_id.id for l in line_obj.browse(cr, uid,line_ids, context)], context=context)
               res+=lines
            plans = []
	    goals = []
	    objectives = []
            projects = []
	    result[obj.id] = {'goal_line':[],'objective_line':[],'plan_line':[],'project_line':[]}
            print "pres....... " , res
	    for r in res:
		if r.type=='objective':
		   objectives.append(r.id)
                   projects+= [p.project_id.id for p in r.project_line_ids if p.project_id.id not in projects] 
                   print "projects....... " , projects
		elif r.type=='goal':
		   goals.append(r.id)
                elif r.type=='plan':
		   plans.append(r.id)
	    result[obj.id] = {'goal_line':goals,'objective_line':objectives,'plan_line':plans,'project_line':projects}
	return result

    _columns = {
        'name': fields.char('Name', required=True,  translate=True),
        'image': fields.binary("Image",
            help="This field holds the image used as avatar for this contact, limited to 1024x1024px"),
        'description': fields.text('Description'),
        'responsible': fields.many2one('hr.department', 'Department'),
        'sequence': fields.integer('Sequence'),
	'date_start': fields.date('Start Date', select=True, copy=False),
        'date_end': fields.date('End Date', select=True, copy=False),	
        'strategic_line_ids': fields.one2many('strategic.strategic.line', 'strategic_id', 'plan'),
        'project_line_ids': fields.one2many('strategic.project.line', 'strategic_id', '--'),

	'actual':fields.function(_progress, method=True , string='Current Actual Progress', type='float', 
                        store={
                            'strategic.strategic': (lambda self, cr, uid, ids, c={}: ids, ['strategic_line_ids','project_line_ids'], 10),
                        }, multi='sums'),   
        'expected':fields.function(_progress, method=True , string='Current Expected Progress', type='float', 
                        store={
                            'strategic.strategic': (lambda self, cr, uid, ids, c={}: ids, ['strategic_line_ids','project_line_ids'], 10),
                        }, multi='sums'),
        'type' : fields.selection([('plan','plan'),('goal','goal'),
                                   ('objective','objective')], 'Type'),
	'plan_line':fields.function(_get_child, string='Current Actual Progress', relation='strategic.strategic', type='one2many', multi="all"),   
	'goal_line':fields.function(_get_child, string='Current Actual Progress', relation='strategic.strategic', type='one2many', multi="all"),   
	'objective_line':fields.function(_get_child, string='Current Actual Progress', relation='strategic.strategic', type='one2many', multi="all"),   
	'project_line':fields.function(_get_child, string='Current projects', relation='project', type='one2many', multi="all"),   
        'color': fields.integer('Color Index'),
    }


    def _get_type(self, cr, uid,context=None):
        """Determine the Strategy's type"""
        type = 'plan'
        if context:
            if context.has_key('type'): type = context['type']
        return type

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
	
    _defaults = {
        'type': _get_type
    }


    def get_action(self, cr, uid, ids, context={}):
	print 'ACTiiiiiiiiiiiiiion', context
	obj =  self.browse(cr, uid, ids[0], context)
        line_obj= self.pool.get('strategic.strategic.line')
        if context['button'] == 'plan':
           lines = obj.plan_line
        if context['button'] == 'objective':
	   lines = obj.objective_line
        if context['button'] == 'goal':
	   lines = obj.goal_line
        return {
                'domain': "[('id','in',%s),('type','=','%s')]" % ([r.id for r in lines],context['button']),
                'name': ' ',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'strategic.strategic',
                'type': 'ir.actions.act_window'
        }

    def get_project(self, cr, uid, ids, context={}):
	res = []
	for record in self.browse(cr, uid, ids, context):
           res = [p.id for p in record.project_line]	
        return {
                'domain': "[('id','in',%s)]" % res,
                'name': ' ',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'project',
                'type': 'ir.actions.act_window'
        }

class project(osv.Model):
    _name = 'project'
    _description = 'Project'
    _order = 'sequence'

    def _progress(self, cr, uid, ids, field_name, arg, context=None):
	res = {}
	ctx = context.copy()
	project_progress_obj = self.pool.get('strategic.project.progress')
	for line in self.browse(cr, uid, ids, context=context):
            progress_id = project_progress_obj.search(cr, uid, \
			[('project_id','=',line.id)], order="date desc", limit=1, context=context)
	    if progress_id:
	        p_obj = project_progress_obj.browse(cr, uid, progress_id[0], context)	
	    actual = progress_id and p_obj.progress or 0
	    expected = 0
	    if line.date_end and line.date_start:
		date = line.date and line.date or time.strftime('%Y-%m-%d')
	        dys = datetime.strptime(line.date_end, "%Y-%m-%d")- datetime.strptime(line.date_start, "%Y-%m-%d")
	        current_dys = datetime.strptime(date, "%Y-%m-%d")- datetime.strptime(line.date_start, "%Y-%m-%d")
	        expected = float(current_dys.days)/float(dys.days)*100
	    res[line.id] = {'actual':actual, 'expected':expected}
	    ctx.update({'project_id': {line.id:res[line.id] }})
	ctx.update({'type':'objective'})
	ides = self.pool.get('strategic.project.line').search(cr, uid, [('project_id','in',ids)])
	strategic_ids =  self.pool.get('strategic.project.line').read(cr, uid, ides, ['strategic_id'])
        asas =[r['strategic_id'][0] for r in strategic_ids ] 
	self.pool.get('strategic.strategic').write(cr, uid, asas,{'project_line_ids':[] }, ctx)
	return res

    def write_scheduler(self, cr, uid, ids=None, use_new_cursor=False, context={}):
        """Scheduler to check the status of car periodically 
        @return True
        """
	ids = self.search(cr, uid, [], context)
        self.write(cr, uid, ids ,{'date':time.strftime('%Y-%m-%d')})
        return True

    _columns = {
        'name': fields.char('project', required=True, translate=True),
        'responsible': fields.many2one('hr.department', 'Responsible'),
        'description': fields.text('Description'),
        'sequence': fields.integer('Sequence'),
        'employee_id' : fields.many2one('hr.employee',"PM"),
        'expected':fields.function(_progress, method=True, string='Current Expected Progress', type='float', store=True, multi='sums'), 
        'actual':fields.function(_progress, method=True, string='Current Actual Progress', type='float', store=True, multi='sums'),   

        'periodic' : fields.selection([('monthly','Mponthly'),('quartly','quartly'),
                                   ('yearly','yearly')], 'Type'),
        'is_operation' : fields.boolean('Is Operation?'),
        'project_progress_ids': fields.one2many('strategic.project.progress', 'project_id', 'projects'),
        'project_line_ids': fields.one2many('project.lines', 'project_id', 'projects'),
        'date_start':fields.date('Start Date'),   		
        'date_end':fields.date('End Date'),   		
        'date':fields.date('Date'),   		
    }	
    _defaults = {
        'is_operation': False,
        'date': lambda *a: time.strftime('%Y-%m-%d'),
    }


class project_lines(osv.Model):
    _name = 'project.lines'
    _description = 'project lines'
    _order = 'date_end'

    def _progress(self, cr, uid, ids, field_name, arg, context=None):
	res = {}
	project_progress_obj = self.pool.get('strategic.project.progress')
	for line in self.browse(cr, uid, ids, context=context):
            progress_id = project_progress_obj.search(cr, uid, \
			[], order="date desc", limit=1, context=context)
	    if progress_id:
	        p_obj = project_progress_obj.browse(cr, uid, progress_id[0], context)	
	    res[line.id] = progress_id and p_obj.progress or 0
	return res


    _columns = {
        'name': fields.char('Phase', required=True),	
	'weight': fields.float('Weight'),
        'date_start': fields.date('Start Date', select=True, copy=False),
        'date_end': fields.date('End Date', select=True, copy=False),
        'project_id': fields.many2one('project', 'project'),
        #'project_progress_ids': fields.one2many('strategic.project.progress', 'phase_id', 'projects'),
	
        'actual':fields.function(_progress, method=True , string='Current Progress', type='float'),   	
    }	


class strategic_project_progress(osv.Model):
    _name = 'strategic.project.progress'
    _description = 'Project Progress'

    _columns = {
        'project_id': fields.many2one('project', 'project'),
        'responsible': fields.related('project_id', 'responsible', type='many2one', relation='project', 
                                     string='Department', store=True, readonly=True),

        'date': fields.date('Date', required=True),
        'progress': fields.float('Progress'),


    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
	}
    '''_sql_constraints = [
        ('phase_date_uniq', 'unique(phase_id, date)', 'You enter two progress for the same phase and date!'),
    ]'''



