import time
from report import report_sxw
from osv import osv
import pooler

class contracts_purchase_order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(contracts_purchase_order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'line' : self._getdata,
	    'line2' : self._getcurrency,
	    'line3':self._gettotal
           
        })
    def _getdata(self,data) :
        return_res=[]
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']
	data_type = data['form']['type']
        where_condition = ""
        where_condition += data_type and (data_type == 'contract' and " and po.contract_id is not null  " or " and po.contract_id is null ") or ""
        self.cr.execute( """ select po.name as name,
       				pc.name as contract_number ,
       				ir.name as request_name , 
       				co.name company,
       				cat.name category,
       				part.name partner,
       				cur.name as currency,
       				ai.id as bill_id ,
       				ai.amount_total as bill_amount ,
       				ai.residual as residual ,
       				po.amount_total as total 
       from purchase_order as po  
	   			left join purchase_contract pc on (pc.id = po.contract_id)
	   			left join ireq_m ir on (ir.id = po.ir_id)
	   			left join purchase_invoice_rel pi on (pi.purchase_id = po.id)
	   			left join account_invoice ai on (pi.invoice_id = ai.id)
           			left join res_company co on (co.id = po.company_id)
           			left join product_category cat on (cat.id = po.cat_id)
           			left join res_currency cur  on (cur.id = po.currency_id)               
           			left join res_partner part on (part.id = po.partner_id)
       where po.purchase_type = 'foreign' and 
       (to_char(po.date_order,'YYYY-mm-dd')>=%s and to_char(po.date_order,'YYYY-mm-dd')<=%s)  """ + where_condition +"order by pc.name",(from_date,to_date))
        res = self.cr.dictfetchall()
        if res: 
           dic={}
           where_condition = ""
           for re in res :
               if re['bill_id']!=None:
               		self.cr.execute( """  select ai.state as state from account_invoice ai where ai.id=%s"""%re['bill_id'])
               		payment = self.cr.dictfetchall()
               		if payment[0]['state']!= 'done':
                 
               				dic={
                 			'name':re['name'],
                 			'contract_number': re['contract_number'],
                 			'request_name': re['request_name'],    
                 			'company': re['company'],
                 			'category' : re['category'] ,
                 			'partner' : re['partner'] ,
                 			'currency' : re['currency'] , 
                 			'total' : re['total'],
                 			'bill_amount' : 0.0 ,
                 			'residual' : re['total'] ,}
              		else:                
               				dic={
                 			'name': re['name'],
                 			'contract_number': re['contract_number'],
                 			'request_name': re['request_name'],      
                 			'company': re['company'],
                 			'category' : re['category'] ,
                 			'partner' : re['partner'] ,
                 			'currency' : re['currency'] , 
                 			'total' : re['total'],
                 			'bill_amount' : re['total'] ,
                 			'residual' : 0.0,}
               else:
               				dic={
                 			'name': re['name'],
                 			'contract_number': re['contract_number'],
                 			'request_name': re['request_name'],      
                 			'company': re['company'],
                 			'category' : re['category'] ,
                 			'partner' : re['partner'] ,
                 			'currency' : re['currency'] , 
                 			'total' : re['total'],
                 			'bill_amount' : 0.0 ,
                 			'residual' :re['total'],}
               return_res.append(dic)
        return return_res

    def _getcurrency(self,data,currency) :
        return_res=[]
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']
	data_type = data['form']['type']
        where_condition = ""
        where_condition += data_type and (data_type == 'contract' and " and po.contract_id is not null  " or " and po.contract_id is null ") or ""
        self.cr.execute( """ select
       				ai.id as bill_id ,
       				po.amount_total as total 
       from purchase_order as po  
	   			left join purchase_contract pc on (pc.id = po.contract_id)
	   			left join purchase_invoice_rel pi on (pi.purchase_id = po.id)
	   			left join account_invoice ai on (pi.invoice_id = ai.id)
           			left join res_currency cur  on (cur.id = po.currency_id)               
       where po.purchase_type = 'foreign' and cur.name = %s and 
       (to_char(po.date_order,'YYYY-mm-dd')>=%s and to_char(po.date_order,'YYYY-mm-dd')<=%s)  """ + where_condition ,(currency,from_date,to_date))
        res = self.cr.dictfetchall()
        if res:
	   dic = {} 
	   amount = 0.0
	   amount_paid = 0.0
	   remaining = 0.0
           where_condition = ""
           for re in res :
               if re['bill_id']!=None:
               		self.cr.execute( """  select ai.state as state from account_invoice ai where ai.id=%s"""%re['bill_id'])
               		payment = self.cr.dictfetchall()
               		if payment[0]['state']!= 'done':
	   				amount += re['total']
	   				amount_paid  = 0.0
	   				remaining += re['total']

              		else:
	   				amount += re['total']
	   				amount_paid  = re['total']
					remaining = 0.0 
	       else :
	   				amount += re['total']
	   				amount_paid  = 0.0
					remaining += re['total'] 
	   dic={
                 			'amount' : amount,
                 			'amount_paid' : amount_paid,
                 			'remaining' :remaining,}
           return_res.append(dic)
        return return_res

    def _gettotal(self,data) :
        currency_obj = self.pool.get('res.currency')
        euro_id = currency_obj.search(self.cr, self.uid, [('name','=','EUR')],limit=1)
        curren = currency_obj.browse(self.cr, self.uid, euro_id)
        return_res=[]
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']
	data_type = data['form']['type']
        where_condition = ""
        where_condition +=  data_type and (data_type == 'contract' and " and po.contract_id is not null  " or " and po.contract_id is null ") or ""
        self.cr.execute("""  select
       				ai.id as bill_id ,
				cur.name as currency ,
				cur.id as currency_id ,
       				po.amount_total as total 
       from purchase_order as po  
	   			left join purchase_contract pc on (pc.id = po.contract_id)
	   			left join purchase_invoice_rel pi on (pi.purchase_id = po.id)
	   			left join account_invoice ai on (pi.invoice_id = ai.id)
           			left join res_currency cur  on (cur.id = po.currency_id)               
       where po.purchase_type = 'foreign' and  
       (to_char(po.date_order,'YYYY-mm-dd')>=%s and to_char(po.date_order,'YYYY-mm-dd')<=%s)"""   + where_condition ,(from_date,to_date))
        res = self.cr.dictfetchall()
        if res:
	   dic = {} 
	   amount = 0.0
	   amount_paid = 0.0
	   remaining = 0.0
           where_condition = ""
           for re in res :
               if re['bill_id']!=None:
               		self.cr.execute( """  select ai.state as state from account_invoice ai where ai.id=%s"""%re['bill_id'])
               		payment = self.cr.dictfetchall()
               		if payment[0]['state']!= 'done':
				if re['currency']=='EUR':
	   				amount += re['total']
	   				amount_paid  = 0.0
	   				remaining += re['total']
				elif re['currency']=='SDG':
	   				amount += currency_obj.compute(self.cr, self.uid, curren[0].id,re['currency_id'], re['total'], to_date)
	   				amount_paid  = 0.0
	   				remaining += currency_obj.compute(self.cr, self.uid, curren[0].id,re['currency_id'], re['total'], to_date)
				else :
	   				amount += currency_obj.compute(self.cr, self.uid,re['currency_id'],curren[0].id, re['total'], to_date)
	   				amount_paid  = 0.0
	   				remaining += currency_obj.compute(self.cr, self.uid, re['currency_id'],curren[0].id, re['total'], to_date)
              		else:
				if re['currency']=='EUR':
	   				amount += re['total']
	   				amount_paid += re['total']
					remaining = 0.0
				elif re['currency']=='SDG':
	   				amount += currency_obj.compute(self.cr, self.uid, curren[0].id,re['currency_id'], re['total'], to_date)
	   				amount_paid += currency_obj.compute(self.cr, self.uid, curren[0].id,re['currency_id'], re['total'], to_date)
	   				remaining =0.0
				else :
	   				amount += currency_obj.compute(self.cr, self.uid, re['currency_id'] ,curren[0].id, re['total'], to_date)
	   				amount_paid += currency_obj.compute(self.cr, self.uid, re['currency_id'] ,curren[0].id, re['total'], to_date)
	   				remaining = 0.0 
 
	       else :
				if re['currency']=='EUR':
	   				amount += re['total']
	   				amount_paid  = 0.0
					remaining += re['total']
				elif re['currency']=='SDG':
	   				amount += currency_obj.compute(self.cr, self.uid, curren[0].id,re['currency_id'], re['total'], to_date)
	   				amount_paid  = 0.0
	   				remaining += currency_obj.compute(self.cr, self.uid, curren[0].id,re['currency_id'], re['total'], to_date)
				else :

	   				amount += currency_obj.compute(self.cr, self.uid, re['currency_id'] ,curren[0].id, re['total'], to_date)
	   				amount_paid = 0.0 
	   				remaining += currency_obj.compute(self.cr, self.uid, re['currency_id'] ,curren[0].id, re['total'], to_date)

	   dic={
                 			'amount' : amount,
                 			'amount_paid' : amount_paid,
                 			'remaining' :remaining,}
           return_res.append(dic)
        return return_res
report_sxw.report_sxw('report.contracts_purchase_order.report','purchase.contract','purchase_contracts/report/contracts_purchase_order.rml',parser=contracts_purchase_order,header=False)

