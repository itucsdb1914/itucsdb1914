@app.route("/eventtype", methods=['GET', 'POST'])
@login_required
def eventtype():
    eventtypes = Eventtypes().retrieve("*")
    print(eventtypes)
    return render_template('createEventtype.html', title='eventtypes', eventtypes=eventtypes)


@app.route("/createEventtype", methods=['GET', 'POST'])
@login_required
def createEventtype():
    form = EventtypeForm()
    if form.validate_on_submit():
        event_type = Eventtypes(eventtype_name=form.eventtype_name.data,
                      eventtype_info=form.eventtype_info.data)
        event_type.create()
    return render_template('createEventtype.html', title='createEventtype', form=form)


@app.route("/eventtype/<int:eventtype_id>/deleteEventtype", methods=['GET', 'POST'])
@login_required
def deleteEventtype(eventtype_id):
    Eventtypes().delete("id = %s", (eventtype_id,))
    flash('Event type has been deleted!', 'alert alert-success alert-dismissible fade show')
    return redirect(url_for('eventtype'))


@app.route("/eventtype/<int:eventtype_id>/updateEventtype", methods=['GET', 'POST'])
@login_required
def updateEventtype(eventtype_id):
    form = EventtypeForm()
    if form.validate_on_submit():
        event_type = Eventtypes(eventtype_name=form.eventtype_name.data,
                      eventtype_info=form.eventtype_info.data,
                      eventtype_id=eventtype_id)
        event_type.update()
        print(event_type)
        return redirect(url_for('eventtype'))

    return render_template('createEventtype.html', title='updateEventtype', form=form)