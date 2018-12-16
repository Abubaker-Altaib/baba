# -*- coding: utf-8 -*-
##############################################################################
#
#    NCTR, Nile Center for Technology Research
#    Copyright (C) 2016-2017 NCTR (<http://www.nctr.sd>).
#
##############################################################################

from report import report_sxw
import re

class Stack:
     def __init__(self):
         self.items = []

     def isEmpty(self):
         return self.items == []

     def push(self, item):
         self.items.append(item)

     def pop(self):
         return self.items.pop()

     def peek(self):
         return self.items[len(self.items)-1]

     def size(self):
         return len(self.items)
class owner_equity_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        self.context = context
        super(owner_equity_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'lines':self.lines,
        })
    
    def account_balance(self, account_code):
        acc_facade = self.pool.get('account.account')
        acc_move = self.pool.get('account.move')
        acc_move_line = self.pool.get('account.move.line')
        acc_journal = self.pool.get('account.journal')
        mode = 'balance'
        if re.match(r'^debit\(.*\)$', str(account_code)):
            # Use debit instead of balance
            mode = 'debit'
            account_code = account_code[6:-1] # Strip debit()
        elif re.match(r'^credit\(.*\)$', str(account_code)):
            # Use credit instead of balance
            mode = 'credit'
            account_code = account_code[7:-1] # Strip credit()
        elif re.match("^\-?\d+?\.\d+$",str( account_code) ):
            #for float numbers
            return float(account_code)
        ctx = {'periods':self.period_ids}
        if self.opening_journal:
            account_ids = acc_facade.search(self.cr, self.uid, [('code', '=', account_code)], context=ctx)
            if not account_ids:
                # We didn't find the account, search for a subaccount ending with '0'
                account_ids = acc_facade.search(self.cr, self.uid, [('code', '=like', '%s%%0' % account_code)], context=ctx)


            journal_id = acc_journal.search(self.cr, self.uid, [('code','=',self.opening_journal)], context=ctx)
            move_id = acc_move.search(self.cr, self.uid, [('state','=','posted'),('journal_id','in',journal_id),('period_id','in',self.period_ids)], context=ctx)
            move_line_ids = acc_move_line.search(self.cr, self.uid, [('move_id','in',move_id),('account_id','in',account_ids)])
            if move_line_ids:
                move_line = acc_move_line.browse(self.cr, self.uid, move_line_ids, context = ctx)[0]
                res = move_line.credit
                if res == 0:
                    res = move_line.debit
                return res
            if not move_line_ids:
                raise ValueError('Error')

        # Search for the account (perfect match)
        account_ids = acc_facade.search(self.cr, self.uid, [('code', '=', account_code)], context=ctx)
        if not account_ids:
            # We didn't find the account, search for a subaccount ending with '0'
            account_ids = acc_facade.search(self.cr, self.uid, [('code', '=like', '%s%%0' % account_code)], context=ctx)
        if len(account_ids) > 0:
            
            res = acc_facade.read(self.cr, self.uid, account_ids, [mode], context=ctx)[0][mode]
            return res
    
    def check_list(self,temp):

        i = 0
        while i < len(temp):
            if temp[i] == '':
                return False
            cr = ''
            if temp[i].startswith('-') or temp[i].startswith('+') or temp[i].startswith('/') or temp[i].startswith('*'):
                if len(temp[i]) > 1:
                    return False
            
            if temp[i].startswith('(') or temp[i].startswith(')'):
                if len(temp[i]) > 1:
                    return False
            
        
            else:
                cr = temp[i]
                if len(cr) > 1 and (cr.endswith(')') or cr.endswith('(')):
                    if not(temp[i].isdigit() or re.match(r'^debit\(.*\)$', temp[i]) or re.match(r'^credit\(.*\)$', temp[i]) ):
                        return False
            i+=1
        return True

    def str_to_list(self,string):
        string = string.replace(' ','')
        temp = re.findall('(\/?\*?\+?\-?\w*\(?[0.0-9.9]*\)?)', string)
        new_list = self.list2list(temp)
        while not self.check_list(new_list):
            new_list = self.list2list(new_list)
        return new_list

    def list2list(self,temp):
        new_list = []
        i = 0
        
        while i < len(temp):
            if temp[i] == '':
                i+=1
                continue
            cr = ''

            if temp[i].isdigit() or re.match(r'^debit\(.*\)$', temp[i]) or re.match(r'^credit\(.*\)$', temp[i]):
                cr += temp[i]
                i+=1
                
                new_list.append(cr)
                continue

            if temp[i].startswith('-') or temp[i].startswith('+') or temp[i].startswith('/') or temp[i].startswith('*'):
                new_list.append(temp[i][0])

                if len(temp[i]) > 1:
                    temp[i] = temp[i][1:]
                    continue

                i+=1
                
                continue
            
            if temp[i].startswith('(') or temp[i].startswith(')'):
                new_list.append(temp[i][0])

                if len(temp[i]) > 1:
                    temp[i] = temp[i][1:]
                    continue

                i+=1
                continue
                
            
            
            else:
                cr = temp[i]
                if len(cr) > 1 and (cr.endswith(')') or cr.endswith('(')):
                    new_list.append(cr[:len(cr)-1])
                    cr = cr[len(cr)-1:len(cr)]
                i+=1
                
                new_list.append(cr)
                continue
        return new_list

    def postfixEval(self, postfixExpr):
        operandStack = Stack()
        tokenList = postfixExpr.split()

        for token in tokenList:
            if token.isdigit() or re.match(r'^debit\(.*\)$', token) or re.match(r'^credit\(.*\)$', token) or re.match("^\d+?\.\d+?$", token):
                if len(tokenList) == 1:
                    token = self.account_balance(token)
                operandStack.push(token)
            else:
                if not operandStack.isEmpty():
                    operand2 = operandStack.pop()
                    if not operandStack.isEmpty():
                        operand1 = operandStack.pop()
                        result = self.doMath(token,operand1,operand2)
                        operandStack.push(result)
        if not operandStack.isEmpty():
            return operandStack.pop()
        return 0

    def doMath(self, op, op1, op2):
        op1 = self.account_balance(op1)
        op2 = self.account_balance(op2)
        if op == "*":
            return op1 * op2
        elif op == "/":
            return op1 / op2
        elif op == "+":
            return op1 + op2
        else:
            return op1 - op2
    

    def infixToPostfix(self, infixexpr):
        prec = {}
        prec["*"] = 3
        prec["/"] = 3
        prec["+"] = 2
        prec["-"] = 2
        prec["("] = 1
        opStack = Stack()
        postfixList = []
        tokenList = self.str_to_list(infixexpr)

        for token in tokenList:
            if token.isdigit() or re.match(r'^debit\(.*\)$', token) or re.match(r'^credit\(.*\)$', token) or re.match("^\d+?\.\d+?$", token):
                postfixList.append(token)
            elif token == '(':
                opStack.push(token)
            elif token == ')':
                topToken = opStack.pop()
                while topToken != '(':
                    postfixList.append(topToken)
                    topToken = opStack.pop()
            else:
                while (not opStack.isEmpty()) and \
                (prec[opStack.peek()] >= prec[token]):
                    postfixList.append(opStack.pop())
                opStack.push(token)

        while not opStack.isEmpty():
            postfixList.append(opStack.pop())
        return " ".join(postfixList)
    
    def process_value(self, value):
        Postfix = self.infixToPostfix(str(value))
        eval = self.postfixEval(Postfix)
        return eval
    
    def lines(self,data):
        lines = []
        year0 = data['form']['year0']
        year = data['form']['year']
        line_ids = data['form']['line_ids']
        lines_obj = self.pool.get("owner.equity.line")
        
        self.period_ids= self.pool.get('account.period').search(self.cr, self.uid, [('fiscalyear_id', '=', year[0])], 
                                                                                       order='date_start', context=self.context)
        if year0:
            self.period_ids= self.pool.get('account.period').search(self.cr, self.uid, [('fiscalyear_id', '=', year0[0])], 
                                                                                       order='date_start', context=self.context)
        
        sum = {'name':'المجموع', 'value1':0.0, 'value2':0.0, 'value3':0.0, 'value4':0.0}
        for line in lines_obj.browse(self.cr, self.uid, line_ids, context=self.context):
            self.opening_journal = False
            if line.opening:
                self.opening_journal = str(line.opening_journal)
            
            cr_line = {'name':line.name}
            cr_line['value1'] = line.value1 and self.process_value(line.value1) or 0
            cr_line['value2'] = line.value2 and self.process_value(line.value2) or 0
            cr_line['value3'] = line.value3 and self.process_value(line.value3) or 0
            cr_line['value4'] = line.value4 and self.process_value(line.value4) or 0
            sum['value1'] += cr_line['value1']
            sum['value2'] += cr_line['value2']
            sum['value3'] += cr_line['value3']
            sum['value4'] += cr_line['value4']
            lines.append(cr_line)
        lines.append(sum)

        if year0 and year:
            self.period_ids= self.pool.get('account.period').search(self.cr, self.uid, [('fiscalyear_id', '=', year[0])], 
                                                                                       order='date_start', context=self.context)
            sum = {'name':'المجموع', 'value1':0.0, 'value2':0.0, 'value3':0.0, 'value4':0.0}
            for line in lines_obj.browse(self.cr, self.uid, line_ids, context=self.context):
                self.opening_journal = False
                if line.opening:
                    self.opening_journal = line.opening_journal
                cr_line = {'name':line.name}
                cr_line['value1'] = line.value1 and self.process_value(line.value1) or 0
                cr_line['value2'] = line.value2 and self.process_value(line.value2) or 0
                cr_line['value3'] = line.value3 and self.process_value(line.value3) or 0
                cr_line['value4'] = line.value4 and self.process_value(line.value4) or 0
                sum['value1'] += cr_line['value1']
                sum['value2'] += cr_line['value2']
                sum['value3'] += cr_line['value3']
                sum['value4'] += cr_line['value4']
                lines.append(cr_line)
            lines.append(sum)
        return lines


report_sxw.report_sxw('report.owner_equity.report', 'owner.equity', 'addons/account_ntc/report/owner_equity.rml' ,parser=owner_equity_report,header=False )
