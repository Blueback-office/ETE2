from odoo import models, fields, api, tools


class StudentPivotReport(models.Model):
    _name = 'survey.pivot.report'
    _auto = False

    id = fields.Id()
    student_id = fields.Many2one('res.partner', string="Student")
    survey_id = fields.Many2one('survey.survey', string="Survey")
    subject_category_id = fields.Many2one(
        'sub.category', string="Subject Category"
    )
    total_answers = fields.Integer(string="Total Answers")
    total_score = fields.Float(string="Total Score")
    percentage_score = fields.Float(string="Percentage (%)")

    def init(self):
        """Create or replace the SQL View for Student Answer Pivot"""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW survey_pivot_report AS (
                SELECT 
                    row_number() OVER () AS id,
                    sul.student_id AS student_id,        
                    sul.survey_id AS survey_id,           
                    sq.sub_category_id AS subject_category_id,   

                    COUNT(sul.id) AS total_answers,      
                    SUM(sul.answer_score) AS total_score,                    
                    (SUM(sul.answer_score) * 100.0 / COUNT(sul.id)) AS percentage_score 

                FROM survey_user_input_line sul
                JOIN survey_question sq ON sq.id = sul.question_id

                GROUP BY sul.student_id, sul.survey_id, sq.sub_category_id
            )
        """)
