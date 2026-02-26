{
    'name': 'Training Student',
    'version': '1.0',
    'summary': 'Student Training Management',
    'description': 'Manage students, courses and enrollments',
    'author': 'Peal-wb',
    'category': 'Training',
    'depends': ['base'],
    'data': [
    'security/ir.model.access.csv',
    'views/training_student_views.xml',
],
    'installable': True,
    'application': True,
}