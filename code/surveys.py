from wtforms import Form, fields, validators

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
