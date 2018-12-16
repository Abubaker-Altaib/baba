# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import fields,osv
import netsvc
import time
from tools.translate import _
import decimal_precision as dp


class monitoring_press(osv.osv):
    """
    To manage monitoring press and it's operations"""

    def create(self, cr, user, vals, context=None):
        """
        Create new entry sequence for every new Monitoring Press Record.
        @param vals: record to be created
        @return: super create() method 
      	"""
        if ('name' not in vals) or (vals.get('name')=='/'):  
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'monitoring.press')
        return super(monitoring_press, self).create(cr, user, vals, context)
    
    STATE_SELECTION = [
    ('draft', 'Draft'),
	('confirmed', 'Waiting for Media Section Manager To process'),
	('gm', 'Waiting for GM To comment'),
	('done', 'done'),
        ('cancel', 'Cancel'), ]


    _name = "monitoring.press"
    _columns = {
    'name': fields.char('Reference', size=64, required=True, select=True, readonly=True  , help="unique number of the monitoring press,computed automatically when the monitoring press is created"),
    'date' : fields.date('Date',readonly=True),
    'user_id':  fields.many2one('res.users', 'Responsible', readonly=True , ),
    'press_lines':fields.one2many('monitoring.press.lines', 'press_id' , 'Newspapers' , states={'confirmed':[('readonly',True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'state': fields.selection(STATE_SELECTION,'State', readonly=True, select=True),
    'notes': fields.text('Notes', size=256 ,states={'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'description': fields.char('Description',size=256 ,states={'confirmed':[('readonly',True)],'gm':[('readonly',True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
    'press_name': fields.related('press_lines','p_name', type='char', relation='monitoring.press.lines',string='News Paper'),
    'company_id': fields.many2one('res.company','Company',required=True,readonly=True),

    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Monitoring Press Reference must be unique !'),
		]
    _defaults = {
                'name': lambda self, cr, uid, context: '/',
                'state': 'draft',
        	'user_id': lambda self, cr, uid, context: uid,
                'date': lambda *a: time.strftime('%Y-%m-%d'),
  		'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'monitoring.press', context=c),
                }
    

    def confirmed(self, cr, uid, ids, context=None):
        """
        Workflow method to Change state of Monitoring Press to confirmed.
 
        @param context: context arguments, like lang, time zone
        @return: Boolean True       
        """
        for press in self.browse(cr, uid, ids):
                if not press.press_lines:
                    raise osv.except_osv(_('No News Paper  !'), _('Please fill the NewsPaper list first ..'))                
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True

    def gm(self,cr,uid,ids,context=None):
        """ 
        Workflow function changes order state to gm.
        
        @return: Boolean True 
        """
        self.write(cr, uid, ids, {'state':'gm'},context=context)
        return True


    def done(self,cr,uid,ids,context=None):
        """ 
        Workflow function changes order state to done.
        
        @return: Boolean True 
        """
        self.write(cr, uid, ids, {'state':'done'},context=context)
        return True

    
    def cancel(self, cr, uid, ids, notes='', context=None):
        """ 
        Workflow function changes order state to cancel and writes note.

	    @param notes: contains information of cancel.
        @return: Boolean True
        """
        notes = ""
        u = self.pool.get('res.users').browse(cr, uid,uid).name
        notes = notes +'\n'+'Monitoring Press at : '+time.strftime('%Y-%m-%d') + ' by '+ u
        self.write(cr, uid, ids, {'state':'cancel','notes':notes})
        return True

    def ir_action_cancel_draft(self, cr, uid, ids, context=None):
        """ 
        Changes state to Draft and reset the workflow.

        @return: True 
        """
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for s_id in ids:
		    self.write(cr, uid, s_id, {'state':'draft'})
		    wf_service.trg_delete(uid, 'monitoring.press', s_id, cr)            
		    wf_service.trg_create(uid, 'monitoring.press', s_id, cr)
        return True

    def unlink(self, cr, uid, ids, context=None):
        """
        Delete the Monitoring Press record if record in draft or cancel state,
        and create log message to the deleted record.

        @return: super unlink() method
        """
        press_request = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in press_request:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('Sorry in order to delete a Moitoring press record(s), it must be cancelled first!'))
        wf_service = netsvc.LocalService("workflow")
        for id in unlink_ids:
            wf_service.trg_validate(uid, 'monitoring.press', id, 'request_cancel', cr)
            record_name = self.browse(cr, uid, id, context=context).name
            message = _("Monitoring Press '%s' has been deleted.") % record_name
            self.log(cr, uid, id, message)
        return super(monitoring_press, self).unlink(cr, uid, unlink_ids, context=context)
   

class monitoring_press_lines(osv.osv):
    """
    To manage NewsPapers of Press"""

    _name = "monitoring.press.lines"
    _description = 'NewsPapers of Press'

    TYPE_SELECTION = [
        ('positive', 'Positive'),
	('negative', 'Negative'),
	('info', 'Information'),
	 ]

    
    _columns = {
                'p_name': fields.many2one('news.papers','News Paper Name', size=64 ,required=True),
		'writer': fields.char('Writer' , size=64 ),  
                'paper_number': fields.char('Page Number',size=256), 
                'no_page': fields.char('No of pages',size=10,required=True),
    		'release_date' : fields.date('Release Date',required=True),
                'press_id': fields.many2one('monitoring.press', 'Monitoring Press', ondelete='cascade'),
                'subject': fields.char('subject',required=True,size=256),
                'template_press': fields.char('Template press',size=256),
                'gm_comment': fields.char('GM Comment',size=256),
                'evaluation': fields.selection(TYPE_SELECTION,'Evaluation', select=True),


               }
    _defaults = {
                'release_date': lambda *a: time.strftime('%Y-%m-%d'),
                 }  
       

class news_papers(osv.osv):
    """
    To manage papers """

    _name = "news.papers"
    _description = 'NewsPapers of Press'
    
    _columns = {
                'name': fields.char('Newspaper Name', size=64 ,required=True),
                'code': fields.integer('Newspaper Code',size=5), 
               }
       

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
