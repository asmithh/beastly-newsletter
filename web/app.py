import time
import uuid

from elasticsearch import Elasticsearch
import flask
from flask import Flask, render_template, redirect, session, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from forms import AskQuestionsForm, AnswerQuestionsForm, SignInForm

es = Elasticsearch(port=9200, hosts=[{"host": "host.docker.internal"}])
EMAIL_INDEX = "emails"
QUESTION_INDEX = "questions"
NEWSLETTER_INDEX = "newsletter"

app = Flask(__name__, template_folder="./")
# TODO: hide secret key before real deploy
app.config["SECRET_KEY"] = "POTATOSTARCHISDELICIOUS"
Bootstrap(app)


@app.route("/")
def whale():
    return render_template("home.html", message="whale hello there, stranger!")


@app.route("/oops")
def oops():
    return render_template("home.html", message=request.args.get("message"))


@app.route("/currently")
def currently():

    most_recent_ts = es.search(
        index=NEWSLETTER_INDEX,
        body={"query": {"match": {"title": "latest_newsletter"}}},
    )["hits"]["hits"][0]["_source"]["timestamp"]

    query = {"query": {"range": {"timestamp": {"gte": most_recent_ts}}}}
    qu_res = es.search(index=QUESTION_INDEX, body=query)
    uniques = set()

    answers = []
    questions = []
    for qu in qu_res["hits"]["hits"]:
        if qu["_id"] in uniques:
            continue
        else:
            answers.append(qu["_source"]["answers"])
            questions.append(
                {
                    "answers": qu["_source"]["answers"],
                    "question": qu["_source"]["question"],
                    "asker": qu["_source"]["asker"],
                }
            )
            uniques.add(qu["_id"])

    return render_template(
        "currently.html",
        questions=questions,
        length_of_thingus=len(answers),
        lengths_of_answers=[len(b) for b in answers],
    )


@app.route("/signup", methods=("GET", "POST"))
def signup():
    form = SignInForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        secret_code = form.secret_code.data
        msg = ""
        res = es.search(
            index=EMAIL_INDEX, body={"query": {"match": {"email": str(email)}}}
        )
        if len(res["hits"]["hits"]) >= 1:
            names = res["hits"]["hits"][0]["_source"]["names"]
            my_id = res["hits"]["hits"][0]["_id"]
            names_str = " ,".join(names)
            msg += f"you already exist with email {email} and aliases {names}"
            if name in set(names):
                msg += f"; you are reusing the alias {name}"
            else:
                msg += f"; we will add {name} to your aliases."
                es.update(
                    index=EMAIL_INDEX, id=my_id, body={"doc": {"names": names + [name]}}
                )

            msg += "and we are calling you {}".format(name)
            session["name"] = name
            session["email"] = email
            session["user_id"] = my_id
            return render_template("home.html", message=msg)

        else:
            doc = {"email": email, "names": [name]}
            es.index(index=EMAIL_INDEX, id=uuid.uuid4(), body=doc)
            return render_template(
                "home.html",
                message=msg
                + f"you are new here! your email is {email} and we are calling you {name}.",
            )

    elif flask.request.method == "POST" and not (form.validate_on_submit()):
        msg = (
            f"hey {name}. your email ({email}) is crap, buddy (or you forgot your name)"
        )
        return redirect(url_for("oops", message=msg))

    return render_template("index.html", form=form)


@app.route("/ask_questions", methods=("GET", "POST"))
def ask_questions():
    form = AskQuestionsForm()
    try:
        who_am_i = {
            "email": session["email"],
            "user_id": session["user_id"],
            "name": session["name"],
        }
    except KeyError as k:
        return render_template(
            "home.html", message="we don't know who you are. please sign in/up!"
        )

    if form.validate_on_submit():
        question = form.question.data
        fake_name = form.pseud.data
        if fake_name:
            asker = fake_name
        else:
            asker = who_am_i["name"]

        ts = time.time()
        doc = {"timestamp": ts, "question": question, "asker": asker, "answers": []}
        es.index(index=QUESTION_INDEX, id=uuid.uuid4(), body=doc)
        return render_template("home.html", message="question successfully submitted!")
    elif flask.request.method == "POST" and not (form.validate_on_submit()):
        return render_template(
            "home.html", message="whale your question did not work, buddy."
        )

    return render_template("ask.html", form=form)


@app.route("/answer_questions", methods=("GET", "POST"))
def answer_questions():
    most_recent_ts = es.search(
        index=NEWSLETTER_INDEX,
        body={"query": {"match": {"title": "latest_newsletter"}}},
    )["hits"]["hits"][0]["_source"]["timestamp"]

    query = {"query": {"range": {"timestamp": {"gte": most_recent_ts}}}}
    qu_res = es.search(index=QUESTION_INDEX, body=query)
    uniques = set()

    questions = []
    for qu in qu_res["hits"]["hits"]:
        if qu["_id"] in uniques:
            continue
        else:
            questions.append(qu)
            uniques.add(qu["_id"])

    qus = []
    for qu in questions:
        name = (
            qu["_source"]["asker"]
            + " is pondering this question: "
            + qu["_source"]["question"]
            + " -- what are your thoughts?"
        )
        qus.append(
            {"txt": name, "source": qu["_source"], "qu_id": qu["_id"]}
        )

    form, fields = AnswerQuestionsForm(questions=qus)
    try:
        who_am_i = {
            "email": session["email"],
            "user_id": session["user_id"],
            "name": session["name"],
        }
    except KeyError as k:
        return render_template(
            "home.html", message="we don't know who you are. please sign in/up!"
        )

    if form.validate_on_submit():
        answers = [getattr(form, f) for f in fields]
        answerer = form.pseud.data
        for ans, qu in zip(answers, qus):
            answers = qu["source"]['answers'] + [{'response': ans.data, 'answerer': answerer}]
            source = qu["source"]
            source["answers"] = answers
            es.delete(index=QUESTION_INDEX, id=qu['qu_id'])
            es.index(index=QUESTION_INDEX, id=qu["qu_id"], body=source)
        return render_template("home.html", message="successfully sent in!!")

    elif flask.request.method == "POST" and not (form.validate_on_submit()):
        return render_template(
            "home.html", message="whale sorry looks like the site broke"
        )

    return render_template("answers.html", form=form)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
