from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date


class TrainingStudent(models.Model):
    _name = 'training.student'
    _description = 'Training Student'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('alumni', 'Alumni')
        ],
        default='draft',
        tracking=True,
        string="Status"
    )

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

    def action_confirm(self):
        self._check_manager()
        self.state = 'confirmed'

    def action_alumni(self):
        self._check_manager()
        self.state = 'alumni'

    def action_reset_draft(self):
        self._check_manager()
        self.state = 'draft'

    def _check_manager(self):
        if not self.env.user.has_group('training_student.group_training_manager'):
            raise UserError("Only Manager can change student status.")

    def write(self, vals):
        if 'state' in vals or 'course_id' in vals:
            self._check_manager()
        return super().write(vals)