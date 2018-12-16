# -*- coding: utf-8 -*-
import getpdfjs
import getpdfworker
import web.http as openerpweb
import urllib
import simplejson
import time
import base64
from openerp.tools import config, ustr
import urllib2
#from openerp.http import request

#from .. import http
class myController(openerpweb.Controller):
    _cp_path = 'report_no_download/ff'

    @openerpweb.httprequest
    def index(self, **kw):
        return "<h1>alfadil</>"

def content_disposition(filename, req):
    filename = ustr(filename)
    escaped = urllib2.quote(filename.encode('utf8'))
    browser = req.httprequest.user_agent.browser
    version = int((req.httprequest.user_agent.version or '0').split('.')[0])
    if browser == 'msie' and version < 9:
        return "attachment; filename=%s" % escaped
    elif browser == 'safari':
        return u"attachment; filename=%s" % filename
    else:
        return "attachment; filename*=UTF-8''%s" % escaped

class cont(openerpweb.Controller):
    _cp_path = '/report_no_download/export'
    
    

    @openerpweb.httprequest
    def index(self,req,name="",token=""):
        name = name.encode('utf-8')
        action = name[name.find('action'):].replace('action=', '')
        name = name+"&session_id="+req.session_id.encode('utf-8')+"&token="+token.encode('utf-8')
        #name = "http://localhost:8069/web/report?action=%7B%22groups_id%22%3A%5B%5D%2C%22help%22%3Afalse%2C%22report_rml_content%22%3A%229.43+Kb%22%2C%22header%22%3Atrue%2C%22report_type%22%3A%22pdf%22%2C%22id%22%3A1391%2C%22webkit_header%22%3A%5B1%2C%22Base+Sample%22%5D%2C%22report_sxw_content%22%3Afalse%2C%22report_webkit_data%22%3Afalse%2C%22attachment%22%3Afalse%2C%22usage%22%3Afalse%2C%22report_sxw_content_data%22%3Afalse%2C%22type%22%3A%22ir.actions.report.xml%22%2C%22report_xml%22%3Afalse%2C%22model_id%22%3A137%2C%22report_rml_content_data%22%3Afalse%2C%22auto%22%3Afalse%2C%22report_sxw%22%3A%22hr_ntc_custom%2Freport%2Femp_training_list_report.sxw%22%2C%22report_file%22%3A%22hr_ntc_custom%2Freport%2Femp_training_list_report.rml%22%2C%22multi%22%3Afalse%2C%22report_xsl%22%3Afalse%2C%22name%22%3A%22%D8%A7%D9%84%D8%A8%D8%B7%D8%A7%D9%82%D8%A9+%D8%A7%D9%84%D8%AA%D8%AF%D8%B1%D9%8A%D8%A8%D9%8A%D8%A9%22%2C%22report_rml%22%3A%22hr_ntc_custom%2Freport%2Femp_training_list_report.rml%22%2C%22report_name%22%3A%22emp_training_list_report.report%22%2C%22flags%22%3A%7B%22new_window%22%3Atrue%2C%22views_switcher%22%3Atrue%2C%22search_view%22%3Atrue%2C%22action_buttons%22%3Atrue%2C%22sidebar%22%3Atrue%2C%22pager%22%3Atrue%2C%22display_title%22%3Atrue%2C%22search_disable_custom_filters%22%3Atrue%7D%2C%22attachment_use%22%3Afalse%2C%22webkit_debug%22%3Afalse%2C%22model%22%3A%22hr.employee%22%2C%22precise_mode%22%3Afalse%2C%22context%22%3A%7B%22lang%22%3A%22ar_SY%22%2C%22tz%22%3A%22Africa%2FKhartoum%22%2C%22uid%22%3A1%2C%22department_id%22%3Afalse%2C%22active_id%22%3A13%2C%22active_ids%22%3A%5B13%5D%2C%22active_model%22%3A%22hr.employee%22%2C%22search_disable_custom_filters%22%3Atrue%7D%2C%22menu_id%22%3Anull%7D&token=1515651495767&session_id=5e2636e913f342a2a5d0e5d1bf1a37d0"
        
        #import urllib2
        #response = urllib2.urlopen(name) 
        #pdf = response.read()

        #import requests
        #r = requests.post(name, json={"session_id": req.session_id})

        POLLING_DELAY = 0.25
        TYPES_MAPPING = {
            'doc': 'application/vnd.ms-word',
            'html': 'text/html',
            'odt': 'application/vnd.oasis.opendocument.text',
            'pdf': 'application/pdf',
            'sxw': 'application/vnd.sun.xml.writer',
            'xls': 'application/vnd.ms-excel',
        }


        action = simplejson.loads(action)

        report_srv = req.session.proxy("report")
        context = dict(req.context)
        context.update(action["context"])
        report_data = {}
        report_ids = context["active_ids"]
        if 'report_type' in action:
            report_data['report_type'] = action['report_type']
        if 'datas' in action:
            if 'ids' in action['datas']:
                report_ids = action['datas'].pop('ids')
            report_data.update(action['datas'])

        report_id = report_srv.report(
            req.session._db, req.session._uid, req.session._password,
            action["report_name"], report_ids,
            report_data, context)
        

        report_struct = None
        while True:
            report_struct = report_srv.report_get(
                req.session._db, req.session._uid, req.session._password, report_id)
            if report_struct["state"]:
                break

            time.sleep(POLLING_DELAY)
        report = base64.b64decode(report_struct['result'])

        

        
        if report_struct.get('code') == 'zlib':
            report = zlib.decompress(report)
        report_mimetype = TYPES_MAPPING.get(
            report_struct['format'], 'octet-stream')
        file_name = action.get('name', 'report')
        if 'name' not in action:
            reports = req.session.model('ir.actions.report.xml')
            res_id = reports.search([('report_name', '=', action['report_name']),],
                                    0, False, False, context)
            if len(res_id) > 0:
                file_name = reports.read(res_id[0], ['name'], context)['name']
            else:
                file_name = action['report_name']
        file_name = '%s.%s' % (file_name, report_struct['format'])
        

        return req.make_response(report,
             headers=[('Content-Type', report_mimetype),])
        
class pdf_js(openerpweb.Controller):
    _cp_path = '/report_no_download/pdf.js'

    @openerpweb.httprequest
    def index(self,req,_):
        return req.make_response(getpdfjs.pdfjs,
             headers=[('Content-Type', 'script')])

class pdf_worker_js(openerpweb.Controller):
    _cp_path = '/report_no_download/pdf.worker.js'

    @openerpweb.httprequest
    def index(self,req,_):
        return req.make_response(getpdfworker.pdfworker,
             headers=[('Content-Type', 'script')])
