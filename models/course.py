from odoo import models, fields

class TrainingCourse(models.Model):
    _name = 'training.course'
    _description = 'Training Course'

    name = fields.Char(string="Course Name", required=True)
    code = fields.Char(string="Course Code")
    duration = fields.Integer(string="Duration (Days)")
    fees = fields.Float(string="Fees")
    start_date = fields.Date(string="Start Date")
    is_available = fields.Boolean(default=True)

    student_ids = fields.One2many(
        'training.student',
        'course_id',
        string="Students"
    )

    enrollment_ids = fields.One2many(
        'training.enrollment',
        'course_id',
        string="Enrollments"
    )