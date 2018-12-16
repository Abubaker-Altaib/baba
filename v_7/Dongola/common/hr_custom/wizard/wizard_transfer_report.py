from osv import fields, osv


class wizard_transfer(osv.osv_memory):
   _name = "wizard.transfer"        


   _columns = {
        'from':fields.date('From', size=8, required=True),
        'to':fields.date('To', size=8, required=True),
   
            }



   def print_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids', []),
             'model': 'hr.process.archive',
             'form': data
                }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'transfer.report',
            'datas': datas,
            }
wizard_transfer()

