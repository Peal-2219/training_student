from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date, timedelta


class TrainingStudent(models.Model):
    _name = 'training.student'
    _description = 'Training Student'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    # =========================
    # STATE
    # =========================
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled')
    ], default='draft', tracking=True)

    # =========================
    # BASIC FIELDS
    # =========================
    name = fields.Char(required=True, tracking=True)
    email = fields.Char(required=True, tracking=True)
    dob = fields.Date(tracking=True)

    student_age = fields.Integer(
        compute="_compute_student_age",
        store=True
    )

    admission_date = fields.Date()
    active = fields.Boolean(default=True)

    user_id = fields.Many2one(
        'res.users',
        string="Assigned User",
        default=lambda self: self.env.user,
        tracking=True
    )

    course_id = fields.Many2one(
        'training.course',
        string="Course",
        tracking=True
    )

    enrollment_ids = fields.One2many(
        'training.enrollment',
        'student_id',
        string="Enrollments"
    )

    # =========================
    # STATE BUTTON ACTIONS
    # =========================
    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_approve(self):
        for rec in self:
            rec.state = 'approved'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'

    def action_reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    # =========================
    # COMPUTE AGE
    # =========================
    @api.depends('dob')
    def _compute_student_age(self):
        for rec in self:
            if rec.dob:
                today = date.today()
                rec.student_age = today.year - rec.dob.year - (
                    (today.month, today.day) < (rec.dob.month, rec.dob.day)
                )
            else:
                rec.student_age = 0

    # =========================
    # SECURITY
    # =========================
    def write(self, vals):
        if 'course_id' in vals:
            if not self.env.user.has_group('training_student.group_training_manager'):
                raise UserError("Only Manager can assign course.")
        return super().write(vals)

    # =========================
    # CRON JOB METHOD
    # =========================
    @api.model
    def cron_auto_update_student_state(self):

        today = date.today()

        students = self.search([])

        for student in students:

            # Draft → Cancelled after 3 days
            if student.state == 'draft' and student.admission_date:
                if student.admission_date <= today - timedelta(days=3):
                    student.state = 'cancelled'

            # Confirmed → Approved after 7 days
            if student.state == 'confirmed' and student.admission_date:
                if student.admission_date <= today - timedelta(days=7):
                    student.state = 'approved'