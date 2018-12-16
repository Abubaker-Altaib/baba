# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import base64
import datetime
from lxml import etree
import os
from time import strftime

from openerp import addons, netsvc, tools
from openerp.osv import fields, osv
from openerp.tools import to_xml
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval

class survey_question_wiz(osv.osv_memory):
    _inherit = 'survey.question.wiz'
    
    def create(self, cr, uid, vals, context=None):
        result = []
        result = super(survey_question_wiz,self).create(cr, uid,vals, context=context)
        resp_line = self.pool.get('survey.response.line')
        res_ans_obj = self.pool.get('survey.response.answer')
        surv_name_wiz = self.pool.get('survey.name.wiz')   
        colum_head = self.pool.get('survey.question.column.heading')     
        sur_resp = self.pool.get('survey.response').browse(cr, uid, context.get('survey_id') , context=context)
        sur_name_read = surv_name_wiz.read(cr, uid, context.get('sur_name_id',False), [])
        if not sur_name_read['response']:
            response_id = resp.create(cr, uid, {'response_type':'link', 'user_id':uid, 'date_create':datetime.datetime.now(), 'survey_id' : context['survey_id']})
            surv_name_wiz.write(cr, uid, [context.get('sur_name_id', False)], {'response' : tools.ustr(response_id)})
        else:    
            response_id = int(sur_name_read['response'])
            
        answer = res_ans_obj.browse(cr, uid, response_id, context=context)
        dic = sur_name_read['store_ans']
        dic_val= int(sur_name_read['store_ans'][1])
        answer_col = res_ans_obj.search(cr, uid, [('answer_id', '=', sur_name_read['store_ans'][1])], context=context)
        sur_resp = res_ans_obj.browse(cr, uid, response_id , context=context)
            
        rating_ls = []
        ans_ids = []
        col_ids = []
        col_weight = []
        res_line_id = resp_line.search(cr, uid, [('response_id','=', response_id)], context=context)
        res_ans_id = res_ans_obj.search(cr, uid, [('response_id','=', res_line_id)], context=context)
        res_ans_brw = res_ans_obj.browse(cr, uid, res_ans_id, context=context)
        if res_ans_brw :
            brw = res_ans_brw[0]
            survey_id = sur_name_read['survey_id'][0]
            page =  self.pool.get('survey.page').search(cr, uid,  [('survey_id','=', survey_id)], context=context)
            page_que = self.pool.get('survey.question').search(cr, uid,  [('page_id','in', page)], context=context)
            col_head = colum_head.search(cr, uid,  [('question_id','in', page_que)], context=context)
            col_ans  = colum_head.browse(cr, uid, col_head, context=context)
            #for que ,ans in map(None,col_ans,res_ans_brw) :
            for que in col_ans:
                col_ids += [que.id]
                rating_ls += [que.rating_weight]
            for ans in res_ans_brw:
                ans_ids += [ans.column_id.rating_weight]
                col_weight +=  [ans.column_id.rating_weight]
           # for col in col_weight:   
            for i,j in map(None,res_ans_id,col_weight):                      
                res_ans_obj.write(cr, uid, i , {'value_choice':j,'answer':max(rating_ls)}, context=context) 
                
        return result
    
survey_question_wiz()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
