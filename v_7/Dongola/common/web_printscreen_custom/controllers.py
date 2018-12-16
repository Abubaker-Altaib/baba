# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2013 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    contact@zbeanztech.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

try:
    import json
except ImportError:
    import simplejson as json

import web.http as openerpweb
from web.controllers.main import ExcelExport
from web.controllers.main import Export

import time, os
from lxml  import etree
from web_printscreen import trml2pdf
from web_printscreen.controllers import ExportPdf,PdfExportView
import locale
import openerp.tools as tools
import operator
import simplejson
import urllib2
from openerp.report import render, report_sxw
import openerp.pooler as pooler

def content_disposition(filename, req):
    filename = filename.encode('utf8')
    escaped = urllib2.quote(filename)
    browser = req.httprequest.user_agent.browser
    version = int((req.httprequest.user_agent.version or '0').split('.')[0])
    if browser == 'msie' and version < 9:
        return "attachment; filename=%s" % escaped
    elif browser == 'safari':
        return "attachment; filename=%s" % filename
    else:
        return "attachment; filename*=UTF-8''%s" % escaped

class ExportPdfCustom(ExportPdf):
    def __init__(self, name=''):
        ExportPdf.__init__(self, name)
        self.dir = 'ltr'

    _cp_path = '/web/export/pdf'
    @openerpweb.httprequest
    def index(self, req, data, token):
        model, fields, ids, domain, import_compat, list_name = \
            operator.itemgetter('model', 'fields', 'ids', 'domain',
                                'import_compat' ,'list_name')(
                simplejson.loads(data))
        #Remove External ID:
        fields.pop(0)
        #title
        if list_name:
           title = list_name
        else:
		    model_id = req.session.model('ir.model').search([('model','=',model)])
		    if model_id:
		        title = req.session.model('ir.model').read(model_id[0], ["name"])["name"]
        #direction
        res_lang = req.session.model('res.lang')
        langs = res_lang.search([("code", "=", req.lang)])
        if langs:
            self.dir = res_lang.read(langs[0], ["direction"])["direction"]
        if self.dir == 'rtl':
            fields.reverse()
        Model = req.session.model(model)
        ids = ids or Model.search(domain, 0, False, False, req.context)
        context = dict(req.context)
        field_names = map(operator.itemgetter('name'), fields)
        import_data = Model.export_data(ids, field_names, req.context).get('datas',[])
        if import_compat:
            #columns_headers = field_names
            #export fields label
            columns_headers = map(operator.itemgetter('label'), fields)
        else:
            columns_headers = [val['label'].strip() for val in fields]
        
        return req.make_response(self.from_data(req.session._uid,columns_headers, import_data, Model,title),
            headers=[('Content-Disposition',
                            content_disposition(self.filename(model), req)),
                     ('Content-Type', self.content_type)],
            cookies={'fileToken': token})
    fmt = {
        'tag': 'pdf',
        'label': 'PDF',
        'error': None
    }
    
    def content_type(self):
        return 'application/pdf'
    
    def filename(self, base):
        return base + '.pdf'
    
    def from_data(self, uid, fields, rows, model,title=''):
        pageSize=[210.0,297.0]
        new_doc = etree.Element("report")
        config = etree.SubElement(new_doc, 'config')
        def _append_node(name, text):
            n = etree.SubElement(config, name)
            n.text = text
        _append_node('date', time.strftime(str(locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y'))))
        _append_node('PageSize', '%.2fmm,%.2fmm' % tuple(pageSize))
        _append_node('PageWidth', '%.2f' % (pageSize[0] * 2.8346,))
        _append_node('PageHeight', '%.2f' %(pageSize[1] * 2.8346,))
        _append_node('PageFormat', 'a4')
        _append_node('header-date', time.strftime(str(locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y'))))
        _append_node('lang', self.dir)
        _append_node('report-header', title)
        l = []
        t = 0
        temp = []
        tsum = []
        header = etree.SubElement(new_doc, 'header')
        for f in fields:
            field = etree.SubElement(header, 'field')
            field.text = tools.ustr(f)
        lines = etree.SubElement(new_doc, 'lines')
        for row_lines in rows:
            node_line = etree.SubElement(lines, 'row')
            for row in row_lines:
                col = etree.SubElement(node_line, 'col', para='yes', tree='no')
                col.text = tools.ustr(row)

        transform = etree.XSLT(etree.parse(tools.file_open('web_printscreen_custom/report/custom_new.xsl'))) 
        
        rml = etree.tostring(transform(new_doc))
        self.obj = trml2pdf.parseNode(rml, title=title)
        return self.obj

class PdfExportViewCustom(PdfExportView,ExportPdfCustom):
    _cp_path = '/web/export/pdf_view'
    
    @openerpweb.httprequest
    def index(self, req, data, token):
        data = json.loads(data)
        model = data.get('model',[])
        columns_headers = data.get('headers',[])
        rows = data.get('rows',[])
        model_id = req.session.model('ir.model').search([('model','=',model)])
        if model_id:
            title = req.session.model('ir.model').read(model_id[0], ["name"])["name"]
        #direction
        res_lang = req.session.model('res.lang')
        langs = res_lang.search([("code", "=", req.lang)])
        if langs:
            self.dir = res_lang.read(langs[0], ["direction"])["direction"]
        if self.dir == 'rtl':
            columns_headers .reverse()
            for row in rows:
            	row.reverse()
        uid = data.get('uid', False)
        return req.make_response(self.from_data(uid, columns_headers, rows, model),
            headers=[('Content-Disposition', 'attachment; filename="%s"' % self.filename(model)),
                     ('Content-Type', self.content_type)],
            cookies={'fileToken': int(token)})

