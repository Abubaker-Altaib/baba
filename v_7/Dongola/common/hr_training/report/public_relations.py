import time
import pooler
import copy
from report import report_sxw
import pdb
import re
from osv import orm
from tools.translate import _


class public_relations(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
		super(public_relations, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
                      
               })
		self.context = context
      def set_context(self, objects, data, ids, report_type=None):
        for obj in objects:
            if obj.state == ('draft'):
                raise orm.except_orm(_('Warning!'), _("You cannot print report , this course not approved yet"))
            if obj.state == 'rejected':
                raise orm.except_orm(_('Warning!'), _("You cannot print report , this course is rejected"))
            if obj.state == 'done':
                raise orm.except_orm(_('Warning!'), _("You cannot print report , this course already done"))
        return super(public_relations, self).set_context(objects, data, ids, report_type=report_type)


    
   
#####################################################################################################

		
      
report_sxw.report_sxw('report.public.relations', 'hr.employee.training.approved',
	'addons/hr_training/report/public_relations.rml', parser=public_relations, header=True)
