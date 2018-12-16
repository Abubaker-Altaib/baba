# Translation of Odoo Server.
# This file contains the translation of the following modules:
#	* account_custom
#	* account
#	* payment
#
msgid ""
msgstr ""
"Project-Id-Version: Odoo Server 11.0\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2018-04-29 19:02+0000\n"
"PO-Revision-Date: 2018-04-29 19:02+0000\n"
"Last-Translator: <>\n"
"Language-Team: \n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: \n"
"Plural-Forms: \n"

#. module: account_custom
#: model:ir.model.fields,field_description:account_custom.field_account_journal_financial_era
msgid "Financial era"
msgstr "عهدة مالية"

#. module: account_custom
#: model:ir.model.fields,field_description:account_custom.field_account_account_analytic
msgid "Analytic"
msgstr "مرتبط بمركز تكلفة"

#. module: account_custom
#: model:ir.model.fields,field_description:account_custom.field_account_account_analytic_account_ids
msgid "Analytic Account"
msgstr "مراكز التكلفة"

#. module: account_custom
#: sql_constraint:account.tax:0
msgid "The code must be unique per company !"
msgstr "الكود يجب أن يكون متفرداً!"

#. module: account_custom
#: model:ir.ui.view,arch_db:account_custom.account_journal_form_inherit
msgid "Name"
msgstr "الإسم"

#. module: account_custom
#: model:ir.ui.view,arch_db:account_custom.account_journal_form_inherit
msgid "Code - Name"
msgstr "الرمز - الإسم"

#. module: account
#: model:ir.model.fields,field_description:account.field_account_account_deprecated
msgid "Deprecated"
msgstr "قفل الحساب"

#. module: account
#: selection:account.payment,state:0
#: model:ir.model.fields,field_description:account.field_account_invoice_sent
#: model:ir.ui.view,arch_db:account.view_account_payment_search
msgid "Sent"
msgstr "تم الارسال"

#. module: account
#: model:ir.model.fields,field_description:account.field_account_tax_amount
#: model:ir.model.fields,field_description:account.field_account_tax_template_amount
msgid "Amount"
msgstr "مبلغ/نسبة"

#. module: account
#: model:ir.model.fields,field_description:account.field_account_tax_amount_type
#: model:ir.model.fields,field_description:account.field_account_tax_template_amount_type
msgid "Tax Computation"
msgstr "طريقة الحساب"

#. module: account_custom
#: model:ir.model.fields,field_description:account_custom.field_account_payment_payment_transfer_date
msgid "Payment Transfer Date"
msgstr "تاريخ الإستلام"

#. module: account
#: model:ir.model.fields,field_description:account.field_account_abstract_payment_payment_method_id
#: model:ir.model.fields,field_description:account.field_account_payment_payment_method_id
#: model:ir.model.fields,field_description:account.field_account_register_payments_payment_method_id
msgid "Payment Method Type"
msgstr "طريقة الدفع"

#. module: account_custom
#: model:ir.ui.view,arch_db:account_custom.view_account_payment_form
msgid "Confirm"
msgstr "تأكيد"

#. module: account_custom
#: model:ir.ui.view,arch_db:account_custom.view_account_payment_form
msgid "Send"
msgstr "إرسال"

#. module: payment
#: model:account.payment.method,name:payment.account_payment_method_electronic_in
msgid "Electronic"
msgstr "إلكتروني"

#. module: account_custom
#: model:ir.model.fields,field_description:account_custom.field_account_analytic_account_cost_type
msgid "Cost Type"
msgstr "نوع التكلفة"

#. module: account_custom
#: selection:account.analytic.account,cost_type:0
msgid "Restricted"
msgstr "مقيد"


#. module: account_custom
#: code:addons/account_custom/models/account_custom.py:169
#, python-format
msgid "Draft Payment"
msgstr "دفعيه مبدئيه"

#. module: account_custom
#: selection:account.analytic.account,cost_type:0
msgid "Awqaf"
msgstr "أوقاف"

#. module: account_custom
#: selection:account.analytic.account,cost_type:0
msgid "Unrestricted"
msgstr "غير مقيد"

#. module: account_custom
#: code:addons/account_custom/models/account_custom.py:77
#, python-format
msgid "You cannot edit name or code of account that have journal entries."
msgstr "لا يمكن تعديل كود أو إسم الحساب للحساب الذي تمت فيه قيود يومية"

#. module: account_custom
#: model:ir.ui.menu,name:account_custom.menu_action_account_type
msgid "Accounts Type"
msgstr "تبويب الحسابات"

#. module: account
#: model:ir.actions.act_window,name:account.action_account_type_form
msgid "Account Types"
msgstr "تبويب الحسابات"

#. module: account
#: selection:account.move,state:0 selection:account.payment,state:0
#: model:ir.ui.view,arch_db:account.view_account_move_filter
#: model:ir.ui.view,arch_db:account.view_account_move_line_filter
#: model:ir.ui.view,arch_db:account.view_account_payment_search
msgid "Posted"
msgstr "مُرحلة  "

#. module: account
#: selection:account.move,state:0
#: model:ir.ui.view,arch_db:account.view_account_move_filter
#: model:ir.ui.view,arch_db:account.view_account_move_line_filter
msgid "Unposted"
msgstr "غير مُرحل "

#. module: account
#: model:ir.model.fields,field_description:account.field_account_abstract_payment_communication
#: model:ir.model.fields,field_description:account.field_account_payment_communication
#: model:ir.model.fields,field_description:account.field_account_register_payments_communication
msgid "Memo"
msgstr "مرجع"

#. module: account
#. openerp-web
#: code:addons/account/static/src/xml/account_payment.xml:64
#, python-format
msgid "Memo:"
msgstr "مرجع:"

#. module: account
#: model:ir.model.fields,field_description:account.field_account_abstract_payment_partner_type
#: model:ir.model.fields,field_description:account.field_account_payment_partner_type
#: model:ir.model.fields,field_description:account.field_account_register_payments_partner_type
msgid "Partner Type"
msgstr "نوع الشريك"

#. module: account
#: model:ir.ui.menu,name:account.account_analytic_tag_menu
msgid "Analytic Tags"
msgstr "تصنيفات مراكز التكلفة"

#. module: account
#: selection:account.abstract.payment,partner_type:0
#: selection:account.payment,partner_type:0
#: selection:account.register.payments,partner_type:0
#: model:ir.ui.view,arch_db:account.invoice_supplier_form
#: model:ir.ui.view,arch_db:account.invoice_supplier_tree
#: model:ir.ui.view,arch_db:account.view_account_invoice_report_search
#: model:ir.ui.view,arch_db:account.view_account_supplier_payment_tree
msgid "Vendor"
msgstr "المستفيد"

#. module: account
#: model:ir.ui.menu,name:account.menu_account_supplier
msgid "Vendors"
msgstr "المستفيدون"

#. module: account
#: selection:account.tax,type_tax_use:0
msgid "Out"
msgstr "خارجة"

#. module: account
#: selection:account.tax,type_tax_use:0
msgid "In"
msgstr "داخلة"

#. module: account
#: model:ir.actions.act_window,name:account.action_account_payments
#: model:ir.ui.menu,name:account.menu_action_account_payments_receivable
msgid "Payments"
msgstr "المقبوضات"

#. module: account
#: model:ir.actions.act_window,name:account.action_invoice_in_refund
#: model:ir.ui.menu,name:account.menu_action_invoice_in_refund
msgid "Vendor Credit Notes"
msgstr "إشعارات العملاء الدائنة"

#. module: account
#: code:addons/account/models/account_invoice.py:1229
#, python-format
msgid "Vendor Credit note"
msgstr "إشعار دائن للعميل"

#. module: account
#: model:ir.ui.menu,name:account.menu_finance_receivables
msgid "Sales"
msgstr "الإيرادات"

#. module: account
#: model:ir.ui.menu,name:account.menu_finance_payables
msgid "Purchases"
msgstr "المصروفات"

#. module: account
#: model:ir.ui.menu,name:account.menu_finance_payables_master_data
#: model:ir.ui.menu,name:account.menu_finance_receivables_master_data
msgid "Master Data"
msgstr "السجلات"

#. module: account_custom
#: code:addons/account_custom/models/account_custom.py:100
#, python-format
msgid "%s (copy)"
msgstr "%s (copy)"

#. module: account_custom
#: model:ir.model,name:account_custom.model_account_account
msgid "Account"
msgstr "الحساب"

#. module: account_custom
#: model:ir.model,name:account_custom.model_account_analytic_account
msgid "Analytic Account"
msgstr "مركز التكلفة"

#. module: account_custom
#: model:ir.model.fields,field_description:account_custom.field_account_analytic_account_childs_user_id
msgid "Child User"
msgstr "مسؤل الحساب الابن"

#. module: account_custom
#: model:ir.model.fields,field_description:account_custom.field_account_tax_code
#: model:ir.model.fields,field_description:account_custom.field_res_partner_code
#: model:ir.model.fields,field_description:account_custom.field_res_users_code
#: model:ir.ui.view,arch_db:account_custom.view_partner_form_inherit
#: model:ir.ui.view,arch_db:account_custom.account_journal_form_inherit
#: model:ir.ui.view,arch_db:account_custom.view_partner_form_inherit2
msgid "Code"
msgstr "الرمز"

#. module: account_custom
#: model:ir.ui.view,arch_db:account_custom.view_partner_form_inherit2
msgid "Category"
msgstr "التصنيف"

#. module: account_custom
#: model:ir.model,name:account_custom.model_res_partner
msgid "Contact"
msgstr "جهة الاتصال"

#. module: account_custom
#: selection:account.account,nature:0
msgid "Credit"
msgstr "دائن"

#. module: account_custom
#: model:ir.model.fields,field_description:account_custom.field_account_tax_date
msgid "Date"
msgstr "تاريخ البداية"

#. module: account_custom
#: selection:account.account,nature:0
msgid "Debit"
msgstr "مدين"

#. module: account_custom
#: model:ir.ui.view,arch_db:account_custom.view_account_tax_inherit_search_sa
msgid "In"
msgstr "داخل"

#. module: account_custom
#: model:ir.model,name:account_custom.model_account_invoice_line
msgid "Invoice Line"
msgstr "بند الفاتورة"

#. module: account_custom
#: model:ir.model,name:account_custom.model_account_move_line
msgid "Journal Item"
msgstr "عنصر يومية"

#. module: account_custom
#: model:ir.ui.view,arch_db:account_custom.view_partner_form_inherit
msgid "Name"
msgstr "الاسم"

#. module: account_custom
#: model:ir.model.fields,field_description:account_custom.field_account_account_nature
msgid "Nature"
msgstr "طبيعة الحساب"

#. module: account_custom
#: selection:account.analytic.account,type:0
msgid "Normal"
msgstr "عادي"

#. module: account_custom
#: model:ir.ui.view,arch_db:account_custom.view_account_tax_inherit_search_sa
msgid "Out"
msgstr "خارج"

#. module: account_custom
#: model:ir.model.fields,field_description:account_custom.field_account_analytic_account_parent_id
#: model:ir.model.fields,field_description:account_custom.field_project_project_parent_id
msgid "Parent"
msgstr "الرئيسي"

#. module: account_custom
#: code:addons/account_custom/models/account_custom.py:25
#, python-format
msgid "Please enter a valid email address."
msgstr "Please enter a valid email address."

#. module: account_custom
#: model:ir.model,name:account_custom.model_account_tax
msgid "Tax"
msgstr "الضريبة"

#. module: account_custom
#: code:addons/account_custom/models/account_custom.py:40
#, python-format
msgid "The amount can not be zero!"
msgstr "المبلغ لا يمكن ان يساوي صفر!"

#. module: account_custom
#: code:addons/account_custom/models/account_custom.py:72
#, python-format
msgid "The balance of credit account should not be more than zero  !!!!!  \n"
" -account:%s \n"
"-balance:%s "
msgstr "المبلغ لا يجب ان يكون أكبر من الصفر  !!!!!  \n"
" -الحساب:%s \n"
"-المبلغ:%s "

#. module: account_custom
#: code:addons/account_custom/models/account_custom.py:69
#, python-format
msgid "The balance of debit account should not be less than zero !!!!!  \n"
" -account:%s \n"
"-balance:%s "
msgstr "المبلغ لا يجب أن يكون أصغر من الصفر !!!!!  \n"
" -الحساب:%s \n"
"-المبلغ:%s "

#. module: account_custom
#: sql_constraint:account.analytic.account:0
msgid "The code must be unique per  company!"
msgstr "المرجع يجب أن يكون متفرداً!"

#. module: account_custom
#: sql_constraint:res.partner:0
msgid "The code,name must be unique per company !"
msgstr " عدم تكرار الاسم و الرمز في  نفس الشركة "

#. module: account_custom
#: sql_constraint:account.analytic.account:0
msgid "The name must be unique per  company!"
msgstr "الإسم يجب أن يكون متفرداً!"

#. module: account_custom
#: model:ir.model.fields,field_description:account_custom.field_account_analytic_account_type
#: model:ir.model.fields,field_description:account_custom.field_project_project_Type
msgid "Type"
msgstr "نوع"

#. module: account_custom
#: selection:account.analytic.account,type:0
#: selection:account.account.type,type:0
msgid "View"
msgstr "عرض"

#. module: account_custom
#: code:addons/account_custom/models/account_custom.py:48
#, python-format
msgid "can't delete this record, Because it is referred to in Default Taxes!"
msgstr "لا يمكن مسح هذا السجل، لأنه مشار إليه في إعدادت الحسابات!"

#. module: account_custom
#: model:ir.model.fields,field_description:account_custom.field_account_analytic_account_child_ids
#: model:ir.model.fields,field_description:account_custom.field_project_project_child_ids
msgid "childs"
msgstr "ابناء"

#. module: account
#: model:ir.actions.act_window,name:account.action_account_journal_form
#: model:ir.model.fields,field_description:account.field_account_aged_trial_balance_journal_ids
#: model:ir.model.fields,field_description:account.field_account_balance_report_journal_ids
#: model:ir.model.fields,field_description:account.field_account_common_account_report_journal_ids
#: model:ir.model.fields,field_description:account.field_account_common_journal_report_journal_ids
#: model:ir.model.fields,field_description:account.field_account_common_partner_report_journal_ids
#: model:ir.model.fields,field_description:account.field_account_common_report_journal_ids
#: model:ir.model.fields,field_description:account.field_account_print_journal_journal_ids
#: model:ir.model.fields,field_description:account.field_account_report_general_ledger_journal_ids
#: model:ir.model.fields,field_description:account.field_account_report_partner_ledger_journal_ids
#: model:ir.model.fields,field_description:account.field_accounting_report_journal_ids
#: model:ir.ui.menu,name:account.menu_action_account_journal_form
msgid "Journals"
msgstr "دفاتر اليومية"


