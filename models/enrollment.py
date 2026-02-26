from odoo import models, fields


class TrainingEnrollment(models.Model):
    _name = 'training.enrollment'
    _description = 'Training Enrollment'

    name = fields.Char(string="Reference", required=True)

    student_id = fields.Many2one(
        'training.student',
        string="Student",
        required=True,
        ondelete='cascade'
    )

    course_id = fields.Many2one(
        'training.course',
        string="Course",
        required=True,
        ondelete='cascade'
    )

    enrollment_date = fields.Date(string="Enrollment Date")

    status = fields.Selection([
        ('draft', 'Draft'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed')
    ], default='draft')