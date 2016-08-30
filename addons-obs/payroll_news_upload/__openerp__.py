# -*- coding: utf-8 -*-
{
    'name': 'Employee Contract News',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'author': "Jose Ernesto Mendez Diaz",
    'website': 'https://nowebsitefornow.com',
    'depends': [
        'hr_payroll',
        'hr_salary_rule_reference',
    ],

    # always loaded
    'data': [
        'views/hr_contract.xml',
        'views/hr_contract_news_categories.xml',
        'views/hr_contract_news_concepts.xml',
        'views/hr_payslip.xml',
        'views/hr_salary_rule.xml',
        'wizard/contract_news_upload.xml',
        'wizard/contract_news_unlink.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}