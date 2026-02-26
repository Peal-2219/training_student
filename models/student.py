from odoo import models, fields


class TrainingStudent(models.Model):
    _name = 'training.student'
    _description = 'Training Student'

    name = fields.Char(string="Student Name", required=True)
    email = fields.Char(string="Email")
    age = fields.Integer(string="Age")
    admission_date = fields.Date(string="Admission Date")
    active = fields.Boolean(default=True)

    # Many2one → One student belongs to one course
    course_id = fields.Many2one(
        'training.course',
        string="Course"
    )

    # One2many → One student can have many enrollments
    enrollment_ids = fields.One2many(
        'training.enrollment',
        'student_id',
        string="Enrollments"
    )

class TrainingEnrollment(models.Model):
    _name = 'training.enrollment'
    _description = 'Training Enrollment'

    name = fields.Char(string="Reference", required=True)

    student_id = fields.Many2one(
        'training.student',
        string="Student",
        required=True
    )

    course_id = fields.Many2one(
        'training.course',
        string="Course",
        required=True
    )

    enrollment_date = fields.Date(string="Enrollment Date")
    status = fields.Selection([
        ('draft', 'Draft'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed')
    ], default='draft')