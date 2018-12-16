import time
from openerp.report import report_sxw
from openerp.osv import osv
import pooler

class programming_contracts(report_sxw.rml_parse):
      def __init__(self, cr, uid, name, context):
          super(programming_contracts, self).__init__(cr, uid, name, context=context)
          self.localcontext.update({
            'time': time,
            'line' : self._getdata,
            'line2' :self.get_total,
            'line3' : self.get_euro_total,
            'currency': self.get_rate,
        })
      # the main data of the report
      def _getdata(self,data) :
          res=[]
          result=[]
          res1=[]
          res2=[]
          from_date = data['form']['from_date']
          to_date = data['form']['to_date']
          purpose = data['form']['purpose']
          voucher_obj = self.pool.get('account.voucher')
          voucher_line_obj = self.pool.get('account.voucher.line')
          contract_obj = self.pool.get('purchase.contract')
          self.cr.execute( """ select 
                                   min(pc.id) as contract_id,
				   min(pc.name) as contract_number ,
                                   min(pc.contract_title) as name,
                                   min(part.name) as partner, 
                                   min(cur.name) as currency ,
                                   min(cur.id) as cur_id,
                                   min(cur.units_name) as cur_name,
                                   min(pc.contract_amount) as amount
                                   from purchase_contract as pc 
                                        left join res_currency cur on (cur.id = pc.currency_id)
                                        left join res_partner part on (part.id = pc.partner_id)
                                        left join contract_fees fc on (fc.contract_id = pc.id and fc.state <> 'draft') 
                                   where pc.contract_purpose = %s and (to_char(fc.fees_date,'YYYY-mm-dd')>=%s and to_char(fc.fees_date,'YYYY-mm-dd')<=%s) group by contract_id order by contract_number""" ,(purpose,from_date,to_date))
          result = self.cr.dictfetchall()
          dic={} 
          if result:
             # to count the not done yet fees
	     for r in result:
	         self.cr.execute(""" select count(fees_amount) as counter from contract_fees where state not in ('done','cancel','draft') and contract_id=%s and (to_char(fees_date,'YYYY-mm-dd')>=%s and to_char(fees_date,'YYYY-mm-dd')<=%s)""",(r['contract_id'],from_date,to_date))  
	         m = self.cr.dictfetchall()
	         dic={
				      'contract_number':r['contract_number'],
				      'counter' : m[0]['counter'],
				      'name' : r['name'] ,
				      'partner' : r['partner'] ,
				      'currency' : r['currency'] ,
                                      'cur_name' : r['cur_name'],
                                      'cur_id' : r['cur_id'],
				      'contract_id' : r['contract_id'],
		                      'amount' : r['amount'],
				         }
	         res.append(dic) 

             dic={}
             for re in res:
                self.cr.execute( """ 
select 
        c.name,
        c.id,
        NULLIF(sum(f.fees_amount), 0.0) as total_fees
	from contract_fees f
	left join purchase_contract c on (c.id = contract_id)                                       
        where (f.state not in ('cancel','draft')) and  
        f.contract_id=%s and (to_char(fees_date,'YYYY-mm-dd')>=%s 
        and to_char(fees_date,'YYYY-mm-dd')<=%s)
        group by c.id ,c.name """,(re['contract_id'],from_date,to_date))
                m = self.cr.dictfetchall()
	        if m[0]['total_fees']<= 0:
	            m[0]['total_fees'] = 0
	        dic = {
				 'total_fees': m[0]['total_fees'], 
		                 'counter' : re['counter'],      
				 'name' : re['name'] ,
				 'partner' : re['partner'] ,
				 'contract_number':re['contract_number'],
				 'currency' : re['currency'] ,
                                 'cur_name' : re['cur_name'],
                                 'cur_id' : re['cur_id'],                                
		                 'amount' : re['amount'],
		                 'contract_id' : re['contract_id'], 
				      } 
		res1.append(dic)
	     dic2 = {}
             for re2 in res1 :
                letter = '%'
		self.cr.execute("""select distinct %s,
       (select sum(inv.residual) from account_invoice inv 
      left outer join account_move am on (inv.move_id = am.id)
      left join contract_fees cf on (inv.reference like %s||cf.name||%s and inv.contract_id = cf.contract_id and cf.state <> 'draft')
           where am.state <> 'reversed' and  inv.contract_id = %s and (to_char(cf.fees_date,'YYYY-mm-dd')>=%s and to_char(cf.fees_date,'YYYY-mm-dd')<=%s)) as residual,
       (select sum(fees_amount) from contract_fees where state in ('confirm') and contract_id = %s and (to_char(fees_date,'YYYY-mm-dd')>=%s and to_char(fees_date,'YYYY-mm-dd')<=%s)) as not_done
       from purchase_contract as c""",(re2['contract_id'],letter,letter,re2['contract_id'],from_date,to_date,re2['contract_id'],from_date,to_date))                  
		result = self.cr.dictfetchall()
                for mm in result:
                    residual = mm['residual'] or 0.0
                    if mm['residual'] == None: 
                        mm['residual'] = 0
                    if mm['not_done'] == None:
                        mm['not_done'] = 0
                    if purpose == 'project':
                        sum_all = 0.0
                        contract = contract_obj.browse(self.cr,self.uid,re2['contract_id'])
                        vouchers = contract.voucher_ids 
                        for voucher in vouchers :
                            sum_all += voucher.read(['residual'])[0]['residual']
                        residual = sum_all  
		    dic2 = {   
		                 'payable' :re2['total_fees'] - (residual + mm['not_done']),
		                 'remain' : residual + mm['not_done'],
		                 'total_fees': re2['total_fees'], 
		                 'counter' : re2['counter'],      
				 'name' : re2['name'] ,
				 'partner' : re2['partner'] ,
				 'contract_number':re2['contract_number'],
				 'currency' : re2['currency'] , 
                                 'cur_name' :re2['cur_name'],
                                 'cur_id' : re2['cur_id'],
		                 'contract_id' : re2['contract_id'],
		                     } 
		    res2.append(dic2)
          return res2
 
      def get_total(self,data):
          result = self._getdata(data)
          all_currecncy = [0]
          dic={}   
          all_result = []
          for record in result:
              if record['currency'] in all_currecncy :
                  continue
              amount_currency = record['currency']
              all_currecncy.append(amount_currency)
              total = 0.0
              remain = 0.0
              payable = 0.0
              for test in result:
                 if test['currency'] == amount_currency:
                     total+=test['total_fees']
                     remain+=test['remain']
                     payable+=test['payable'] 
            
              dic = {
                      'cur_name': record['cur_name'],
                      'currency': amount_currency,
                      'payable' : payable,
		      'remain' : remain,
		      'total_fees': total,
                      'cur_id': record['cur_id'],
                      'name':record['currency'],
                      }
              all_result.append(dic)
          return all_result

      def get_euro_total(self,data):
          to_date = data['form']['to_date']
          currency_obj = self.pool.get('res.currency')
          euro_id = currency_obj.search(self.cr, self.uid, [('name','=','EUR')],limit=1)[0]
          result = self.get_total(data)
          total_amount = 0.0
          remain_amount = 0.0
          payed_amount = 0.0
          amounts = {}
          for record in result:
              if record['currency']=='EUR' :
                  total_amount += record['total_fees']
                  remain_amount += record['remain']
                  payed_amount += record['payable']
              elif record['currency']=='SDG':
                  total_amount += currency_obj.compute(self.cr, self.uid, euro_id,record['cur_id'], record['total_fees'], to_date)
                  remain_amount += currency_obj.compute(self.cr, self.uid, euro_id,record['cur_id'], record['remain'], to_date)
                  payed_amount += currency_obj.compute(self.cr, self.uid, euro_id,record['cur_id'], record['payable'], to_date)
              else:
                  total_amount += currency_obj.compute(self.cr, self.uid, record['cur_id'],euro_id, record['total_fees'], to_date)
                  remain_amount += currency_obj.compute(self.cr, self.uid, record['cur_id'],euro_id, record['remain'], to_date)
                  payed_amount += currency_obj.compute(self.cr, self.uid, record['cur_id'], euro_id, record['payable'], to_date) 
          amounts = {
                  'total_amount':total_amount,
                  'remain_amount':remain_amount,
                  'payed_amount': payed_amount,
                    }
          return amounts

      def get_rate(self,data,curency):
           to_date = data['form']['to_date']
           currency_obj = self.pool.get('res.currency')
           currency_id = currency_obj.search(self.cr, self.uid, [('name','=',curency)],limit=1)[0]
           self.cr.execute("SELECT rate FROM res_currency_rate WHERE currency_id = %s AND name <= %s ORDER BY name desc LIMIT 1" ,(currency_id, to_date))
           res = self.cr.dictfetchall()
           return res[0]['rate'] 

report_sxw.report_sxw('report.programming_contracts','purchase.contract','purchase_contracts/report/programming_contracts.rml',parser=programming_contracts,header=False)

