# models/student.py

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class TrainingStudent(models.Model):
    _name = 'training.student'
    _description = 'Training Student'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    # =========================
    # BASIC FIELDS
    # =========================
    name = fields.Char(string="Student Name", required=True, tracking=True)
    email = fields.Char(string="Email", required=True, tracking=True)
    dob = fields.Date(string="Date of Birth", tracking=True)

    student_age = fields.Integer(
        string="Age",
        compute="_compute_student_age",
        store=True,
        tracking=True
    )

    user_id = fields.Many2one(
        'res.users',
        string="Responsible User",
        default=lambda self: self.env.user,
        tracking=True
    )

    admission_date = fields.Date(string="Admission Date", tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    course_id = fields.Many2one(
        'training.course',
        string="Course",
        tracking=True
    )

    course_name = fields.Char(
        related="course_id.name",
        store=True
    )

    enrollment_ids = fields.One2many(
        'training.enrollment',
        'student_id',
        string="Enrollments"
    )

    enrollment_count = fields.Integer(
        string="Enrollment Count",
        compute="_compute_enrollment_count"
    )

    # =========================
    # COMPUTE METHODS
    # =========================
    @api.depends('dob')
    def _compute_student_age(self):
        for record in self:
            if record.dob:
                today = date.today()
                record.student_age = today.year - record.dob.year - (
                    (today.month, today.day) < (record.dob.month, record.dob.day)
                )
            else:
                record.student_age = 0

    @api.depends('enrollment_ids')
    def _compute_enrollment_count(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)

    # =========================
    # CONSTRAINT
    # =========================
    @api.constrains('student_age')
    def _check_age(self):
        for record in self:
            if record.student_age < 5:
                raise ValidationError("Student age must be greater than 5!")

    # =========================
    # ONCHANGE
    # =========================
    @api.onchange('course_id')
    def _onchange_course_id(self):
        if self.course_id:
            return {
                'warning': {
                    'title': "Course Selected",
                    'message': f"You selected {self.course_id.name} course."
                }
            }

    # =========================
    # ORM METHODS
    # =========================
    @api.model
    def create(self, vals):
        if 'email' in vals:
            vals['email'] = vals['email'].lower()
        return super().create(vals)

    def write(self, vals):
        if 'email' in vals:
            vals['email'] = vals['email'].lower()
        return super().write(vals)

    def unlink(self):
        for record in self:
            if record.enrollment_ids:
                raise ValidationError("Cannot delete student with enrollments.")
        return super().unlink()

    _sql_constraints = [
        ('unique_email', 'unique(email)', 'Email must be unique!')
    ]