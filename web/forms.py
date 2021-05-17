from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, StringField, SubmitField
from wtforms.validators import DataRequired, Email
from wtforms.widgets import PasswordInput

class SignInForm(FlaskForm):
	name = StringField('what is your name?', validators=[DataRequired()])
	email = StringField('what is your email?', validators=[DataRequired(), Email()])
	secret_code = StringField('the secret code', validators=[DataRequired()])
	submit = SubmitField('submit')


class AskQuestionsForm(FlaskForm):
    question = StringField('what question do you want to ask?', validators=[DataRequired()])
    pseud = StringField('pick a pseudonuym if you want')
    submit = SubmitField('submit')
 

def AnswerQuestionsForm(questions):
    class AnswerQuestionsPlz(FlaskForm)
        pass
    idx = 0

    for qu in questions:
        setattr(AnswerQuestionsPlz, 'field_{}'.format(str(idx)), StringField(qu['name'])) 
        idx += 1

    AnswerQuestionsPlz.pseud = StringField('pick a pseudonuym if you want')
    AnswerQuestionsPlz.submit = SubmitField('submit')

    return AnswerQuestionsPlz()
