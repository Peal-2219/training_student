from odoo import models, fields, api


class TrainingEnrollment(models.Model):
    _name = 'training.enrollment'
    _description = 'Training Enrollment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    enrollment_number = fields.Char(
        string="Enrollment Number",
        required=True,
        copy=False,
        # readonly=True,
        # default="New"
    )

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

    enrollment_date = fields.Date(default=fields.Date.today)

    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('enrollment_number', 'New') == 'New':
            vals['enrollment_number'] = self.env['ir.sequence'].next_by_code(
                'training.enrollment'
            ) or 'New'
        return super().create(vals)