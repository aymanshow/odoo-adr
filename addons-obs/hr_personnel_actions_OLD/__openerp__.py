{
'name':'Personnel Action',
'version': '1.0',
'author':'OBS',
'category':'Updates',
'description': """
A module that creates a personnel action for an employee that shows the current situation and requests changes if required.
""",
'depends':['base','hr','hr_contract', 'hr_payroll'],
'data':['hr_personnel_action_view.xml',
        'hr_personnel_action_workflow.xml',
        'security/ir.model.access.csv',
        'hr_holiday_types.xml'],
'installable':False,
'active': False,
}

