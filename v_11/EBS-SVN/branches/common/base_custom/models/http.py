# -*- coding: utf-8 -*-
# ----------------------------------------------------------
# OpenERP HTTP layer
# ----------------------------------------------------------
import odoo 
from odoo import http
import werkzeug.contrib.sessions
import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers
import werkzeug.wsgi
from werkzeug import urls
from werkzeug.wsgi import wrap_file
from odoo import api , fields,exceptions, tools, models,_

class JsonRequestCustom(http.JsonRequest):

    def _handle_exception(self, exception):
        try:
            return super(http.JsonRequest, self)._handle_exception(exception)
        except Exception:
            if not isinstance(exception, (odoo.exceptions.Warning, http.SessionExpiredException,
                                          odoo.exceptions.except_orm, werkzeug.exceptions.NotFound)):
                http._logger.exception("Exception during JSON request handling.")
            error = {
                'code': 200,
                'message': _("Odoo Server Error"),
                'data': http.serialize_exception(exception)
            }
            if isinstance(exception, werkzeug.exceptions.NotFound):
                error['http_status'] = 404
                error['code'] = 404
                error['message'] = "404: Not Found"
            if isinstance(exception, http.AuthenticationError):
                error['code'] = 100
                error['message'] = "Odoo Session Invalid"
            if isinstance(exception, http.SessionExpiredException):
                error['code'] = 100
                error['message'] = "Odoo Session Expired"
            return self._json_response(error=error)
    http.JsonRequest._handle_exception = _handle_exception
