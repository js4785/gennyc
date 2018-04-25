from wtforms import Form, fields, validators


class SurveyTestQuestion(Form):
    gender = fields.RadioField('What is your gender?',
                               choices=[('M', 'Male'), ('F', 'Female'), ('O', 'I prefer not to answer')],
                               validators=[validators.InputRequired()], default=('M', 'Male'))
    age = fields.RadioField('What is your age?',
                            choices=[('lt18', 'Younger than 18'), ('18-24', '18 to 24'), ('25-34', '25 to 34'),
                                     ('35-44', '35 to 44'), ('45-54', '45 to 54'), ('55', '55 years or older')],
                            validators=[validators.InputRequired()])
    education = fields.RadioField('Which of the following best describes your highest education level?',
                                  choices=[('Hsg', 'High school graduate'),
                                           ('Scnd', 'Some college, no degree'), ('Assoc', 'Associates Degree'),
                                           ('Bach', 'Bachelors degree'),
                                           ('Grad', 'Graduate degree (Masters, Doctorate, etc.)'),
                                           ('O', 'Other')],
                                  validators=[validators.InputRequired()])
    language = fields.StringField('What is your native language', validators=[validators.InputRequired()])


class UserInterests(Form):
    hobbies = fields.SelectMultipleField('What are some of your hobbies and interests?',
                                        choices=[('hobbies-crafts', 'Arts & Crafts'),
                                                 ('fashion-beauty', 'Fashion & Beauty'),
                                                 ('food', 'Food'),
                                                 ('language', 'Language'),
                                                 ('parents-family', 'Parenting & Family'),
                                                 ('tech', 'Technology'),
                                                 ('social', 'Social'),
                                                 ('none_hobbies', 'Not interested')],
                                        validators=[validators.InputRequired()])
    causes = fields.SelectMultipleField('What causes interest you?',
                                          choices=[('beliefs', 'Beliefs'),
                                                   ('education', 'Education'),
                                                   ('career-business', 'Career & Business'),
                                                   ('none_causes', 'Not interested')],
                                          validators=[validators.InputRequired()])
    fitness = fields.SelectMultipleField('What do you like to do for exercise?',
                                         choices=[('outdoors-adventure', 'Outoors Adventures'),
                                                  ('sports-fitness', 'Sports & Fitness'),
                                                  ('dancing', 'Dancing'),
                                                  ('none_fitness', 'Not interested')],
                                         validators=[validators.InputRequired()])
    arts_and_culture = fields.SelectMultipleField('What kinds of arts & culture interest you?',
                                         choices=[('arts-culture', 'General Arts & Culture'),
                                                  ('film', 'Film'),
                                                  ('music', 'Music'),
                                                  ('book-clubs', 'Book Clubs'),
                                                  ('none_arts', 'Not interested')],
                                         validators=[validators.InputRequired()])
