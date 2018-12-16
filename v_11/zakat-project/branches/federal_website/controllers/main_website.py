from datetime import datetime
from odoo import http, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.http import request
from odoo import fields, models, api, exceptions, _
from odoo.exceptions import ValidationError, AccessError


class MyController(http.Controller):

  @http.route(['/federal_request'], auth="public", website=True)
  def federal_form(self , **kw):

    return request.render("federal_website.federal_request" , {'national_n':  kw.get('national_number') ,  'req_type': kw.get('req_type') , 'nationality': kw.get('nationality') , 'passport':kw.get('passport'),'session_start':kw.get('session_start')})

 
  @http.route(['/thank_you'], auth="public", website=True)
  def federal_thanks(self, **kw):
    return request.render("federal_website.federal_thanks")

  @http.route(['/federal_following'], csrf=False, auth="public", website=True)
  def federal_following(self, **kw):
    try:
      if kw.get('natio_validate') == 'False':
        pass

      else:
        has_request = []
        result = []
        print("********",kw.get('n_nat') )
        if kw.get('n_nat') == 'natio':
          print("|||||||||||", kw.get('national_folow') )
          result = request.env['res.partner'].sudo().search([('national_number' ,'=' , kw.get('national_folow') )])
          has_request = request.env['zakat.federaltreatment.request'].sudo().search([('partner_id' ,'=' , result.id)])
          if has_request:
            return request.render("federal_website.federal_following",{'fol_req':has_request , 'partner_info': result})
          else:
            print("|))))")
            raise exceptions.UserError(_('Sorry! You must Enter at least Onr Adminstrative Unit'))
            print("$$$$$$",er)
            return request.render("federal_website.federal_request" , {'wrong_req': 'natio_wrong' , 'natio_n': kw.get('national_folow')})

        if kw.get('n_nat') == 'passp':
          print("|||||||||||", kw.get('pass_fol') )
          result = request.env['res.partner'].sudo().search([('passport' ,'=' , kw.get('pass_fol') )])
          has_request = request.env['zakat.federaltreatment.request'].sudo().search([('partner_id' ,'=' , result.id)])
          if has_request:
            return request.render("federal_website.federal_following",{'fol_req':has_request , 'partner_info': result})
          else:
            return request.render("federal_website.federal_request" , {'wrong_req': 'passp_wrong' , 'pass_n': kw.get('pass_fol')})

        else:
          has_request = request.env['zakat.federaltreatment.request'].sudo().search([('code' ,'=' , kw.get('follow_num') )])          
          result = request.env['res.partner'].sudo().search([('id' ,'=' , has_request[-1].partner_id.id )])
          if has_request:
            return request.render("federal_website.federal_following",{'fol_req':has_request , 'partner_info': result})
          else:
            return request.render("federal_website.federal_request" , {'wrong_req': 'ref_wrong' , 'foll_n': kw.get('follow_num')})

    except:
      pass
    

  @http.route(['/federal_request_submit'], auth="public",csrf=True, website=True)
  def federal_submit(self, **kw ):
    try:
      print("_____________")

      # if kw.get('session_start') != 'True':
      #   return request.render("federal_website.federal_request" , {'session_start': 'False'})
    
      if kw.get('national_validate') == 'False' or kw.get('passport_validate') == 'False':
        pass
      else:
        print("^^^^^^^^^^^")
        result = request.env['res.partner'].sudo().search([('national_number' ,'=' , kw.get('national_number') )])
        states = request.env['zakat.state'].sudo().search([])

        if result:
          print("$$$$$$$$$$$$$$$")
          # created_date = datetime.strptime(, '%Y-%m-%d')
          has_request = request.env['zakat.federaltreatment.request'].sudo().search([('partner_id' ,'=' , result.id)])
          c_date = has_request[-1].create_date
          # print("++++++++",c_date)

          # b = datetime.now()
          # created_date = str(b - c_date)

          # print("@@@@@@@@@",b.day  )
          # print("00000",created_date.day)
          # date_format = "%Y-%m-%d %h:%m:%s"
          # a = datetime.strptime(str(c_date), date_format)
          # print("AAAAAAAA",a)
          # delta = b - a
          # print("ppppppp",delta)
          # print("]]]]]]]]]",delta.total_seconds() // 60)
          return request.render("federal_website.registered_data" , {'result':result , 'req_type': kw.get('req_type') ,'session_start':kw.get('session_start')})
       
        else:
          return request.render("federal_website.new_registration" , {'national_n':  kw.get('national_number') , 'req_type': kw.get('req_type') , 'nationality': kw.get('nationality'),'passport':kw.get('passport') , 'states':states, 'session_start':kw.get('session_start') })
    
    except:
      pass
    

  @http.route(['/federal_get'], auth="public", website=True)
  def federal_get(self, **kw):
    return request.render("federal_website.federal_get")


  @http.route(['/request_submit'], auth="public", website=True)
  def federal_thanks(self, **kw):
    req_id = []
    if kw.get('amount_v') == 'False' :
        pass
    else:
      try:
        re = request.env['res.partner'].sudo().search([('national_number' ,'=' , kw.get('national_number') )])
        req = request.env['zakat.federaltreatment.request'].sudo().create({
          'first_name':  kw.get('first_name'),
          'second_name': kw.get('second_name') ,
          'third_name':  kw.get('third_name'),
          'forth_name': kw.get('forth_name'),
          'partner_id' :re.id,
          'type': kw.get('req_type') ,
          'birth_date':  kw.get('birth_date'),
          'gender': kw.get('gender'),
          'phone': kw.get('phone'),
          'zakat_state': kw.get('state_id'),
          'national_number': kw.get('national_number'),
          'treatment_amount': kw.get('treatment_amount'),
          'note': kw.get('note'),
          # 'bill': kw.get('bill'),
          # 'medical': kw.get('medical'),
          # 'review': kw.get('review'),
          # 'check': kw.get('check'),
          # 'commission': kw.get('commission'),
          # 'abroad_cost': kw.get('abroad_cost'),
          # 'passport_co': kw.get('passport_co'),
          # 'tickets': kw.get('tickets'),
          # 'visa': kw.get('visa'),
          # 'conversion_replacement': kw.get('conversion_replacement'),
          'website_request_validate':True,

          })
        req_id = request.env['zakat.federaltreatment.request'].sudo().search([('id','=',req.id)])
      except:
        pass 
      return request.render("federal_website.federal_thanks",{'req_ref':req_id.code , 'connection_reset':kw.get('connection_reset')})


  @http.route(['/registration'], auth="public", website=True)
  def federal_register(self, **kw):
    req_id = []
    at = []
    attach = []
    # if kw.get('connection_reset') != 'False':
    #   return request.render("federal_website.federal_request" , {'session_start': 'False'})

    if kw.get('session_start') != 'True':
      return request.render("federal_website.federal_request" , {'session_start': 'False'})

    if kw.get('name_v') == 'False' or kw.get('phone_v') == 'False' :
      pass

    else:
      if kw.get('nationality') == 'sd':
        partner = request.env['res.partner'].sudo().create({
        'first_name':  kw.get('first_name'),
        'second_name': kw.get('second_name') ,
        'third_name':  kw.get('third_name'),
        'forth_name': kw.get('forth_name'),
        'national_number': kw.get('national_number'),
        'zakat_state': kw.get('state_id'),
        'phone': kw.get('phone'),
        # 'passport': '',
        'birth_date': kw.get('birth_date'),
        'city': kw.get('city'),
        'nationality': kw.get('nationality'),
        # 'local_state_id': kw.get('local_state'),
        # 'admin_unit': kw.get('administrative_unit'),
        'job': kw.get('job'),
        'house_no': kw.get('house_no'),
        'Village': kw.get('village'),
        'zakat_partner':'TRUE',
        })


      if kw.get('nationality') == 'other':
        partner = request.env['res.partner'].sudo().create({
        'first_name':  kw.get('first_name'),
        'second_name': kw.get('second_name') ,
        'third_name':  kw.get('third_name'),
        'forth_name': kw.get('forth_name'),
        # 'national_number': '',
        'zakat_state': kw.get('state_id'),
        'phone': kw.get('phone'),
        'passport': kw.get('passport'),
        'birth_date': kw.get('birth_date'),
        'city': kw.get('city'),
        'nationality': kw.get('nationality'),
        # 'local_state_id': kw.get('local_state'),
        # 'admin_unit': kw.get('administrative_unit'),
        'job': kw.get('job'),
        'house_no': kw.get('house_no'),
        'Village': kw.get('village'),
        'zakat_partner':'TRUE',
        })

      req = request.env['zakat.federaltreatment.request'].sudo().create({
        'first_name':  kw.get('first_name'),
        'second_name': kw.get('second_name') ,
        'third_name':  kw.get('third_name'),
        'forth_name': kw.get('forth_name'),
        'partner_id' :partner.id,
        'type': kw.get('req_type') ,
        'birth_date':  kw.get('birth_date'),
        'gender': kw.get('gender'),
        'phone': kw.get('phone'),

        'zakat_state': kw.get('state_id'),
        # 'national_number': kw.get('national_number'),
        'treatment_amount': kw.get('treatment_amount'),
        'note': kw.get('note'),

        'bill': kw.get('bill'),
        # 'medical': kw.get('medical'),
        # 'review': kw.get('review'),
        # 'check': kw.get('check'),
        # 'commission': kw.get('commission'),
        # 'abroad_cost': kw.get('abroad_cost'),
        # 'passport_co': kw.get('passport_co'),
        # 'tickets': kw.get('tickets'),
        # 'visa': kw.get('visa'),
        # 'conversion_replacement': kw.get('conversion_replacement'),
        'website_request_validate':True,
        
        })

      at.append(kw.get('fileInput1'))
      at.append(kw.get('fileInput2'))
      at.append(kw.get('fileInput3'))
      at.append(kw.get('fileInput4'))

      print("+++++++++++++",at)
      for i in range(0,3):
        print("|||||||||||||",at[i])
        attach += request.env['ir.attachment'].sudo().create({
          'res_model':'zakat.federaltreatment.request',
          'name': at[i],
          'res_id': req.id ,
          })

      req_id = request.env['zakat.federaltreatment.request'].sudo().search([('id','=',req.id)])
     
      if partner:
        return request.render("federal_website.federal_thanks",{'req_ref':req_id.code , 'connection_reset':kw.get('connection_reset')})
      
      else:
        return request.render("federal_website.federal_request")

 
  # @http.route('/website/reset_templates', type='http', auth='user', methods=['POST'], website=True)
  #   def reset_template(self, templates, redirect='/'):
  #       templates = request.httprequest.form.getlist('templates')
  #       modules_to_update = []
  #       for temp_id in templates:
  #           view = request.env['ir.ui.view'].browse(int(temp_id))
  #           if view.page:
  #               continue
  #           view.model_data_id.write({
  #               'noupdate': False
  #           })
  #           if view.model_data_id.module not in modules_to_update:
  #               modules_to_update.append(view.model_data_id.module)

  #       if modules_to_update:
  #           modules = request.env['ir.module.module'].sudo().search([('name', 'in', modules_to_update)])
  #           if modules:
  #               modules.button_immediate_upgrade()
  #       return request.redirect(redirect)
