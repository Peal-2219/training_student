from odoo import models, fields, api

class TrainingStudent(models.Model):
    _name = 'training.student'
    _description = 'Training Student'

    name = fields.Char(string="Student Name", required=True)
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    age = fields.Integer(string="Age")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string="Gender")
    admission_date = fields.Date(string="Admission Date")
    active = fields.Boolean(string="Active", default=True)
    bio = fields.Text(string="Biography")
    image = fields.Binary(string="Profile Image")

    enrollment_ids = fields.One2many(
        'training.enrollment',
        'student_id',
        string="Enrollments"
    )

class TrainingCourse(models.Model):
    _name = 'training.course'
    _description = 'Training Course'

    name = fields.Char(string="Course Name", required=True)
    code = fields.Char(string="Course Code")
    duration = fields.Integer(string="Duration (Days)")
    fees = fields.Float(string="Fees")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    is_available = fields.Boolean(string="Available", default=True)
    description = fields.Text(string="Description")

    enrollment_ids = fields.One2many(
        'training.enrollment',
        'course_id',
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
    completion_date = fields.Date(string="Completion Date")
    status = fields.Selection([
        ('draft', 'Draft'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string="Status", default='draft')

    confirmed = fields.Boolean(string="Confirmed", default=False)
    notes = fields.Text(string="Notes")