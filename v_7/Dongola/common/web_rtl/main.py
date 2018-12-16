# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################

import openerp
import web
from web.controllers import main
from web import http
openerpweb = http
#----------------------------------------------------------
# OpenERP Web RTl
#----------------------------------------------------------
def get_direction(req):
    """
    @return: char logged in user language's direction
    """
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

rtl_module_installed =main.module_installed
rtl_module_boot=main.module_boot
def rtl_module_installed(req):
    """
    Method that return all installed modules without web_rtl module when current language's direction
    
    @return: list of char
    """
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

def rtl_module_boot(req, db=None):
    """
    Method that return all installed modules without web_rtl module when current language's direction
    
    @return: list of char
    """
    server_wide_modules = openerp.conf.server_wide_modules or ['web']
    serverside = []
    dbside = []
    for i in server_wide_modules:
        if i in openerpweb.addons_manifest:
            serverside.append(i)
    monodb = db or main.db_monodb(req)
    if monodb:
        dbside = main.module_installed_bypass_session(monodb)
        dbside = [i for i in dbside if i not in serverside]
    addons = serverside + dbside
    if 'web_rtl' in addons and get_direction(req)=='ltr':
        addons.remove('web_rtl')
    return addons

main.module_installed = rtl_module_installed
main.module_boot = rtl_module_boot

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: 943
