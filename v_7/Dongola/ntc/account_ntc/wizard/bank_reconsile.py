# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################


from openerp.osv import osv, fields
from openerp.tools.translate import _
import xml.etree.ElementTree as ET
import base64


class checks_wizard(osv.osv_memory):
    _name = "bank.reconsile.wizard"

    _description = "bank reconsile wizard"

    _columns =  {
        'file': fields.binary('attachments', "File", required=True),
        'journal_id':fields.many2one('account.journal', "Bank", required=True),
        'date':fields.date('date', required=True),
    }

    def bank_reconsile(self, cr, uid, ids, context=None):
        if not ids:
            return False
        record = self.browse(cr, uid, ids, context=context)
        
        journal_id = record[0].journal_id
        account_id = journal_id.default_debit_account_id.id
        date = record[0].date
        tree = record[0].file
        
        tree = base64.decodestring(tree)
        all_lines = {}
        id = amount = 0
        try:
            #get data lines from the xml file
            file = xlrd.open_workbook(file_contents=tree)
            for sh in file.sheet_names():
                cr_sh = file.sheet_by_name(sh)
                for rownum in range(cr_sh.nrows):
                    if rownum == 0:continue
                    cr_row = cr_sh.row_values(rownum)
                    id = cr_row[0]
                    if type(id) is float:
                        id = int(id)
                        
                    
                    if type(id) is str:
                        if id.isdigit():
                            id = int(id)

                    id = str(id)


                    amount = cr_row[1]
                    amount = float(cr_row[1])
                    
                    
                    
                    all_lines[id]=amount
        except:
            raise osv.except_osv(_('Warning'), _('worng data in id : '+str(id) +' and amount : '+str(amount)))
        if not all_lines:
            raise osv.except_osv(_('Warning'), _('no lines found in the file'))
        
        #search for move lines with entered references 
        move_line_obj = self.pool.get('account.move.line')
        search_ids = move_line_obj.search(cr, uid, [
            ('ref', 'in', all_lines.keys()),
            ('account_id', '=', account_id),
            ('statement_id', '=', False),
            ('move_id.state', 'in', ['posted', 'reversed']),
            ('date','<=', date),
            ], context=context)
        
        reconsiled_ids = []
        for line in move_line_obj.browse(cr, uid, search_ids, context=context):
            #check entered amount with line amount
            if all_lines[line.ref] == line.debit+line.credit:
                reconsiled_ids.append(line.id)
        
        if not reconsiled_ids:
            raise osv.except_osv(_('Warning'), _('no move lines found to transfer'))
        data = {
            'journal_id':journal_id.id,
            'date':date,
            'move_line_ids':[[6, False, reconsiled_ids]],
            'note': False,
            'line_ids': [],
        }

        return self.pool.get('account.bank.statement').create(cr, uid, data, context=context)
            

