import flask

import models
import forms


app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "This is secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://coe:CoEpasswd@localhost:5432/coedb"
)

models.init_app(app)


@app.route("/")
def index():
    db = models.db
    notes = db.session.execute(
        db.select(models.Note).order_by(models.Note.title)
    ).scalars()
    return flask.render_template(
        "index.html",
        notes=notes,
    )


@app.route("/notes/create", methods=["GET", "POST"])
def notes_create():
    form = forms.NoteForm()
    if not form.validate_on_submit():
        print("error", form.errors)
        return flask.render_template(
            "notes-create.html",
            form=form,
        )
    note = models.Note()
    form.populate_obj(note)
    note.tags = []

    db = models.db
    for tag_name in form.tags.data:
        tag = (
            db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
            .scalars()
            .first()
        )

        if not tag:
            tag = models.Tag(name=tag_name)
            db.session.add(tag)

        note.tags.append(tag)

    db.session.add(note)
    db.session.commit()

    return flask.redirect(flask.url_for("index"))


@app.route("/tags/<tag_name>")
def tags_view(tag_name):
    db = models.db
    tag = (
        db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
        .scalars()
        .first()
    )
    notes = db.session.execute(
        db.select(models.Note).where(models.Note.tags.any(id=tag.id))
    ).scalars()

    return flask.render_template(
        "tags-view.html",
        tag_name=tag_name,
        notes=notes,
    )


@app.route("/tags/delete_<tag_name>")
def tags_delete(tag_name):
    db = models.db
    tag = db.session.execute(
        db.select(models.Tag).where(models.Tag.name == tag_name)
    ).scalar()
    notes = db.session.execute(
        db.select(models.Note).where(models.Note.tags.any(id=tag.id))
    ).scalars()
    for i in notes:
        db.session.delete(i)
    db.session.delete(tag)
    db.session.commit()
    return flask.redirect(flask.url_for("index"))


@app.route("/note/delete_<note_id>")
def node_delete(note_id):
    db = models.db
    note = db.session.execute(
        db.select(models.Note).where(models.Note.id == note_id)
    ).scalar()
    db.session.delete(note)
    db.session.commit()
    return flask.redirect(flask.url_for("index"))


@app.route("/notes/edit_<note_id>", methods=["GET", "POST"])
def notes_edit(note_id):
    form = forms.NoteForm()
    if not form.validate_on_submit():
        print("error", form.errors)
        return flask.render_template(
            "notes-edit.html",
            form=form,
        )
    note = models.Note()
    form.populate_obj(note)
    note.tags = []

    db = models.db
    for tag_name in form.tags.data:
        tag = (
            db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
            .scalars()
            .first()
        )

        if not tag:
            tag = models.Tag(name=tag_name)
            db.session.add(tag)

        note.tags.append(tag)

    db.session.execute(
        db.update(models.Note).values(title=note.title).where(models.Note.id == note_id)
    )
    db.session.execute(
        db.update(models.Note)
        .values(description=note.description)
        .where(models.Note.id == note_id)
    )
    db.session.commit()

    return flask.redirect(flask.url_for("index"))


@app.route("/tag/edit_<tag_name>", methods=["GET", "POST"])
def tag_edit(tag_name):
    form = forms.TagForm()
    if not form.validate_on_submit():
        print("error", form.errors)
        return flask.render_template(
            "tag_edit.html",
            form=form,
        )

    db = models.db
    tag = models.Tag()
    form.populate_obj(tag)
    db.session.execute(
        db.update(models.Tag).values(name=tag.name).where(models.Tag.name == tag_name)
    )
    db.session.commit()

    return flask.redirect(flask.url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
