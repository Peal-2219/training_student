from odoo import models, fields, api
from odoo.exceptions import UserError


class TrainingEnrollment(models.Model):
    _name = 'training.enrollment'
    _description = 'Training Enrollment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ----------------------------
    # FIELDS
    # ----------------------------
    enrollment_number = fields.Char(
        string="Enrollment Number",
        readonly=True,
        copy=False,
        default="New",
        tracking=True
    )

    student_id = fields.Many2one(
        'training.student',
        string="Student",
        required=True,
        tracking=True
    )

    course_id = fields.Many2one(
        'training.course',
        string="Course",
        required=True,
        tracking=True
    )

    enrollment_date = fields.Date(
        default=fields.Date.today,
        tracking=True
    )

    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], default='draft', tracking=True)

    # ----------------------------
    # CREATE
    # ----------------------------
    @api.model
    def create(self, vals):
        if vals.get('enrollment_number', 'New') == 'New':
            vals['enrollment_number'] = self.env['ir.sequence'].next_by_code(
                'training.enrollment'
            ) or 'New'
        return super().create(vals)

    # ----------------------------
    # SECURITY FOR STATUS CHANGE
    # ----------------------------
    def write(self, vals):
        if 'status' in vals:
            if not self.env.user.has_group('training_student.group_training_manager'):
                raise UserError("Only Manager can change status.")
        return super().write(vals)