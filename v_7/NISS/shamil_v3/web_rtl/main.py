# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import os
import simplejson
import urllib
import glob
import werkzeug.wrappers
import re
import openerp
import web
from web.controllers import main
from web import http
openerpweb = http
#----------------------------------------------------------
# OpenERP Web RTl
#----------------------------------------------------------
def get_direction(req):
 
    
    direction='ltr'
    if not req.session or not req.session._uid:
        return direction
    current_lang = req.session._uid and req.session.get_context().get('lang', 'en_US') or 'en_US'
    context = req.session.get_context() 
    Model = req.session.model
    langobj = Model('res.lang').search([('code', '=', current_lang),], 0, False, False, context)
    lang = Model('res.lang').read(langobj[0], ['code', 'direction'], context) if langobj else None
    if not lang:
        return direction
    return lang.get('direction', 'ltr') 

def module_installed(req):
    # Candidates module the current heuristic is the /static dir
    loadable = openerpweb.addons_manifest.keys()
    modules = {}
    # Retrieve database installed modules
    # TODO The following code should move to ir.module.module.list_installed_modules()
    Modules = req.session.model('ir.module.module')
    domain = [('state','=','installed'), ('name','in', loadable)]
    for module in Modules.search_read(domain, ['name', 'dependencies_id']):
        modules[module['name']] = []
        deps = module.get('dependencies_id')
        if deps:
            deps_read = req.session.model('ir.module.module.dependency').read(deps, ['name'])
            dependencies = [i['name'] for i in deps_read]
            modules[module['name']] = dependencies
    
    sorted_modules = main.module_topological_sort(modules)
    if  'web_rtl' in sorted_modules and get_direction(req)=='ltr':
        sorted_modules.remove('web_rtl')
    return sorted_modules

def module_boot(req, db=None):
    server_wide_modules = openerp.conf.server_wide_modules or ['web']
    serverside = []
    dbside = []
    for i in server_wide_modules:
        if i in openerpweb.addons_manifest:
            serverside.append(i)
    monodb = db or db_monodb(req)
    if monodb:
        dbside = main.module_installed_bypass_session(monodb)
        dbside = [i for i in dbside if i not in serverside]
    addons = serverside + dbside
    if 'web_rtl' in addons and get_direction(req)=='ltr':
        addons.remove('web_rtl')
    return addons

def manifest_glob(req, extension, addons=None, db=None):
    if addons is None:
        addons = module_boot(req, db=db)
    else:
        addons = addons.split(',')
    r = []
    for addon in addons:
        manifest = openerpweb.addons_manifest.get(addon, None)
        if not manifest:
            continue
        # ensure does not ends with /
        addons_path = os.path.join(manifest['addons_path'], '')[:-1]
        globlist = manifest.get(extension, [])
        for pattern in globlist:
            for path in glob.glob(os.path.normpath(os.path.join(addons_path, addon, pattern))):
                r.append((path, main.fs2web(path[len(addons_path):])))
    return r

def manifest_list(req, extension, mods=None, db=None):
    """ list ressources to load specifying either:
    mods: a comma separated string listing modules
    db: a database name (return all installed modules in that database)
    """
    mods_list = []
    if not req.debug:
        path = '/web/webclient/' + extension
        if mods is not None:
            path += '?' + urllib.urlencode({'mods': mods})
        elif db:
            path += '?' + urllib.urlencode({'db': db})
        return [path]
    files = manifest_glob(req, extension, addons=mods, db=db)
    return [wp for _fp, wp in files]

class Home(main.Home):
    _cp_path = '/'

    @openerpweb.httprequest
    def index(self, req, s_action=None, db=None, **kw):
       
        db, redir = main.db_monodb_redirect(req)
        if redir:
            return main.redirect_with_hash(req, redir)
        for k, v in dict(req.httprequest.cookies).iteritems():
            if '|session_id' in k:
                # strip %22 from begining and end
                req.session_id = v[3:-3]
                if req.session_id:
                    req.session = req.httpsession.get(req.session_id)
       
        js = "\n        ".join('<script type="text/javascript" src="%s"></script>' % i for i in  manifest_list(req, 'js', db=db))
        css = "\n        ".join('<link rel="stylesheet" href="%s">' % i for i in  manifest_list(req, 'css', db=db))
        r = main.html_template % {
            'js': js,
            'css': css,
            'modules': simplejson.dumps(module_boot(req, db=db)),
            'init': 'var wc = new s.web.WebClient();wc.appendTo($(document.body));'
        }
        return r

    @openerpweb.httprequest
    def login(self, req, db, login, key):
        return main.login_and_redirect(req, db, login, key)

class Session(main.Session):
    _cp_path = "/web/session"

    @openerpweb.jsonrequest
    def modules(self, req):
        # return all installed modules. Web client is smart enough to not load a module twice
        return module_installed(req)

class WebClient(main.WebClient):
    _cp_path = "/web/webclient"

    @openerpweb.jsonrequest
    def csslist(self, req, mods=None):
        return manifest_list(req, 'css', mods=mods)

    @openerpweb.httprequest
    def css(self, req, mods=None, db=None):
        for k, v in dict(req.httprequest.cookies).iteritems():
            if '|session_id' in k:
                # strip %22 from begining and end
                req.session_id = v[3:-3]
                if req.session_id:
                    req.session = req.httpsession.get(req.session_id)
        files = list(manifest_glob(req, 'css', addons=mods, db=db))
        last_modified = main.get_last_modified(f[0] for f in files)
        if req.httprequest.if_modified_since and req.httprequest.if_modified_since >= last_modified:
            return werkzeug.wrappers.Response(status=304)

        file_map = dict(files)

        rx_import = re.compile(r"""@import\s+('|")(?!'|"|/|https?://)""", re.U)
        rx_url = re.compile(r"""url\s*\(\s*('|"|)(?!'|"|/|https?://|data:)""", re.U)

        def reader(f):
            """read the a css file and absolutify all relative uris"""
            with open(f, 'rb') as fp:
                data = fp.read().decode('utf-8')

            path = file_map[f]
            web_dir = os.path.dirname(path)

            data = re.sub(
                rx_import,
                r"""@import \1%s/""" % (web_dir,),
                data,
            )

            data = re.sub(
                rx_url,
                r"""url(\1%s/""" % (web_dir,),
                data,
            )
            return data.encode('utf-8')

        content, checksum = main.concat_files((f[0] for f in files), reader)

        # move up all @import and @charset rules to the top
        matches = []
        def push(matchobj):
            matches.append(matchobj.group(0))
            return ''

        content = re.sub(re.compile("(@charset.+;$)", re.M), push, content)
        content = re.sub(re.compile("(@import.+;$)", re.M), push, content)

        matches.append(content)
        content = '\n'.join(matches)

        return main.make_conditional(
            req, req.make_response(content, [('Content-Type', 'text/css')]),
            last_modified, checksum)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: 943
