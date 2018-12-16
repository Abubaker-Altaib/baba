# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from osv import osv, fields
from openerp.tools.translate import _
from urlparse import urljoin
from urllib import urlencode
import openerp.addons.web.http as http



def send_mail(self, cr, uid, id, group_name, mail_title, mail_body, user=False, department=False, context=None):
    action = context and context.get('action',0) or 0
    if action:
        module_name, menu_xml_id = action.split('.')

        dummy, menu_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, module_name, menu_xml_id)

        ir_ui_menu = self.pool.get('ir.ui.menu').browse(cr, uid, menu_id, context=None)

        action = ir_ui_menu.action.id

    user_obj = self.pool.get('res.users')
    base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')

    base_url = base_url.split(':')[0]+ ':' +base_url.split(':')[1]
    #base_url = 'erp.ntc.gov.sd'
    query = {'db': cr.dbname}
    mail_to = []
    if user:
        user = user_obj.read(cr, uid, user, ['email','login'], context=context)

        mail_to = [ {'mail':x['email'], 'user_id':x['id'], 'login':x['login']} for x in user]

    elif group_name:
        group_name = group_name.split(',')
        
        # groups ids
        g_ids = groups_ids(cr, group_name)

        mail_to = get_users(cr, g_ids, department)


    mail_obj = self.pool.get('email.service')
    for mail in mail_to:
        fragment = {
            'login': mail['login'],
            'model': self._name,
            'id': id,
            'action':action,
            'view_type':'form'
        }
        self.check_access_rule(cr, mail['user_id'], [id], 'read', context=context)
        url = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
        mail_id = mail_obj.create(cr,uid,{'mail_title':mail_title, 'mail_body':mail_body, 'mail':mail['mail'],'url':url},context=context)

        mail_obj.send_mail(cr, uid, mail_id, context=context)
        mail_obj.unlink(cr, uid, mail_id, context=context)

    # if user_obj.has_group(cr, uid, group_name)


def groups_ids(cr, group_ext_ids):
    ids = []
    for group_ext_id in group_ext_ids:
        assert group_ext_id and '.' in group_ext_id, "External ID must be fully qualified"
        module, ext_id = group_ext_id.split('.')
        cr.execute("""SELECT res_id FROM ir_model_data WHERE module=%s AND name=%s""",
                   (module, ext_id))
        fetch = [x[0] for x in cr.fetchall()]
        ids += fetch
    return ids


def get_users(cr, groups_ids, department):
    if groups_ids:
        if not department:
            cr.execute("""SELECT distinct p.email as email,uid as user_id , login FROM res_groups_users_rel rel 
                        left join res_users u on(rel.uid = u.id)
                        left join res_partner p on(u.partner_id = p.id)
                        WHERE u.active = True and gid in %s """,
                    (tuple(groups_ids), ))
        else:
            cr.execute("""SELECT distinct p.email as email,uid as user_id , login FROM res_groups_users_rel rel 
                        left join res_users u on(rel.uid = u.id)
                        left join res_partner p on(u.partner_id = p.id)
                        WHERE u.active = True and gid in %s
                        and u.context_department_id = %s""",
                    (tuple(groups_ids), department))
        return [{'mail':str(x[0]), 'user_id':x[1], 'login':str(x[2])} for x in cr.fetchall()]
    return []


class email_service(osv.Model):
    """To manage e-mail service """
    _name = "email.service"

    _description = 'e-mail service'

    _columns = {
        'mail': fields.char('mail'),
        'mail_body': fields.text('Mail Body'),
        'mail_title': fields.text('Mail Title'),
        'url':fields.char('Url'),
    }

    _defaults = {
        'mail': 'erptest1@itisalat.ntc.org.sd'
    }

    def send_mail(self, cr, uid, id, context=None):
        template_obj = self.pool.get('email.template')
        data_obj = self.pool.get('ir.model.data')
        mail_template_id = data_obj.get_object_reference(
            cr, uid, 'admin_affairs', 'email_generic_form')
        template_obj.send_mail(cr, uid, mail_template_id[
                               1], id, True, context=context)
