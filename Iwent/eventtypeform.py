class EventtypeForm(FlaskForm):
    eventtype_name = StringField('Event Type Name', validators=[DataRequired(), Length(min=2, max=50)])
    eventtype_info = StringField('Event Type Information', validators=[DataRequired(), Length(min=2, max=50)])
    submit_event_type = SubmitField('Create Event Type')
    submit_update_event = SubmitField('Update Event Type')