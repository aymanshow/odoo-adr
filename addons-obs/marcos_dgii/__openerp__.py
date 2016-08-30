# -*- coding: utf-8 -*-
{
    'name': "Marcos DGII",
    'description': "Generador de reporte para la DGII modificacdo",
    'category': 'Hidden',
    'depends': ['base', ],
    'depends': ['web', 'account', 'debit_credit_note',],
    'data': [
        'marcos_dgii_view.xml',
#       'wizard/marcos_z_report_view.xml',
        'account_invoice_view.xml',
        'account_view.xml',
        'res_partner_view.xml',
        'res_company_view.xml'],
    #'js': ['static/src/js/marcos_dgii.js'],
    #'css': ['static/src/css/marcos_dgii.css'],
    #'qweb': ['static/src/xml/marcos_dgii.xml'],
}
