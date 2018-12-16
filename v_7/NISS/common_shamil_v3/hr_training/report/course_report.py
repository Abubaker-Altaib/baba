import time
import pooler
import copy
from report import report_sxw
import pdb
import re


class course_training(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
		super(course_training, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
                        #'info':self. _get_emp,
                        #'course':self._get_course,
               })


    
   
#####################################################################################################

      



report_sxw.report_sxw('report.course.training', 'hr.employee',
	'addons/hr_training/report/course_report.rml', parser=course_training, header=True)
