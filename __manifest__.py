{
    'name': 'Training Student',
    'version': '1.0',
    'summary': 'Student Training Management',
    'description': 'Manage students, courses and enrollments',
    'author': 'Peal-wb',
    'category': 'Training',
    'depends': ['base', 'mail', 'base_automation', 'website'],
    'data': [
        'security/training_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/student_email_template.xml',
        'data/student_automation.xml',
        'data/cron.xml',

        'reports/student_report_template.xml',
        'reports/student_report_action.xml',

        'views/training_student_views.xml',
        'views/enrollment_views.xml',
        'views/course_views.xml',
        'views/website_templates.xml',
    ],
    'demo': [
        'demo/course_demo.xml',
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
