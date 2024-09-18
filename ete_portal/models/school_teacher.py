from odoo import api, models, _
 
class SchoolTeacher(models.Model):
    """Defining a Teacher information."""

    _inherit = "school.teacher"
    
    @api.onchange('standard_ids')
    def _onchange_standard_ids(self):
        for std_id in self._origin.standard_ids:
            std_id.user_id = self._origin.id
            

class SchoolStandard(models.Model):
    _inherit = "school.standard"
    
    @api.onchange("user_id")
    def onchange_user_id(self):
        for teacher in self:
            teacher.user_id.standard_ids = [(4, teacher._origin.id)]