import time
from report import report_sxw

class fuel_move(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(fuel_move, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'line1':self._getShop1,
            'line':self._getShop,
            'line2':self._getShop2,
            'line3':self._getShop3,
        })
   
    def _getShop(self,data,num):
          
           date= data['form']['Date_from']
           date1= data['form']['Date_to']
           location_id= data['form']['location_id']


           self.cr.execute("""SELECT 

                                     sum(s.product_qty) AS product_qty_out


                              From fuel_picking f LEFT JOIN stock_move s ON (f.id = s.fuel_picking_id)

                                     LEFT JOIN product_product p ON (s.product_id=p.id)
                              Where
                                     s.product_id=%s and to_char(f.date,'YYYY-mm-dd')>=%s and to_char(f.date,'YYYY-mm-dd')<=%s and f.state = 'done' and p.fuel_ok ='True' and s.location_id=%s """,(num,date,date1,location_id[0])) 
           res = self.cr.dictfetchall()
           return res



    def _getShop2(self,data,num):
          
           date= data['form']['Date_from']
           date1= data['form']['Date_to']
           location_id= data['form']['location_id']
           self.cr.execute("""SELECT 
                                     
                                     sum(s.product_qty) AS product_qty_in

                              From fuel_picking f LEFT JOIN stock_move s ON (f.id = s.fuel_picking_id)

                                     LEFT JOIN product_product p ON (s.product_id=p.id)
                              Where
                                     s.product_id=%s and to_char(f.date,'YYYY-mm-dd')>=%s and to_char(f.date,'YYYY-mm-dd')<=%s and f.state = 'done' and p.fuel_ok ='True' and s.location_dest_id=%s""",(num,date,date1,location_id[0])) 
           res = self.cr.dictfetchall()
           return res



    def _getShop3(self,data):
          
           date= data['form']['Date_from']
           date1= data['form']['Date_to']
           location_id= data['form']['location_id']
           self.cr.execute("""SELECT 
                                     
                                     distinct s.product_id as id ,
                                     p.name_template AS product_name,
                                     p.default_code AS default_code,
                                     u.name AS uom_id

                              From fuel_picking f LEFT JOIN stock_move s ON (f.id = s.fuel_picking_id)

                                     LEFT JOIN product_uom u ON (s.product_uom=u.id)
                                     LEFT JOIN product_product p ON (s.product_id=p.id)
                              Where
                                    to_char(f.date,'YYYY-mm-dd')>=%s and to_char(f.date,'YYYY-mm-dd')<=%s and f.state = 'done' and p.fuel_ok ='True' and ( s.location_id=%s or s.location_dest_id=%s) ORDER BY p.default_code """,(date,date1,location_id[0],location_id[0])) 
           res = self.cr.dictfetchall()
           return res



    def _getShop1(self,data):
           location_id= data['form']['location_id']
           self.cr.execute('SELECT  name From stock_location where id=%s'%(location_id[0])) 
           res = self.cr.dictfetchall()
           return res
        
report_sxw.report_sxw('report.fuel_move.report', 'stock.move', 'addons/fuel_management/report/fuel_move.rml' ,parser=fuel_move ,header='False')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

