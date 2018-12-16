# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2011-2012 NCTR (<http://www.nctr.sd>).
#
##############################################################################
import web
from web.controllers import main
def rights_validate(self, req, model, method):
        try:
            search_ids = req.session.model('model_control.line').search([('model','=',model),('is_active','=',True),(method,'=',True)])
            if search_ids:
                return False
        except:
            pass
        
        # print "....................model",model
        # print "....................method",method

        return True 
        

        
class DataSet_custom(main.DataSet):

    
            
            
#---------------------------------------
                   
            
    def _call_kw(self, req, model, method, args, kwargs):
        #rights_validate(self, req, model, method)
        if method in ['read', 'write', 'create', 'unlink']:
            if not rights_validate(self, req, model, method):
                raise ValueError(("هذه العملية موقوفه مؤقتا") )


        # Temporary implements future display_name special field for model#read()
        if method == 'read' and kwargs.get('context', {}).get('future_display_name'):
            if 'display_name' in args[1]:
                names = dict(req.session.model(model).name_get(args[0], **kwargs))
                args[1].remove('display_name')
                records = req.session.model(model).read(*args, **kwargs)
                for record in records:
                    record['display_name'] = \
                        names.get(record['id']) or "%s#%d" % (model, (record['id']))
                return records

        return getattr(req.session.model(model), method)(*args, **kwargs)

    main.DataSet._call_kw = _call_kw
