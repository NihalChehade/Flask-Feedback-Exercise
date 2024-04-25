
from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///user_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

connect_db(app)

with app.app_context():
 db.create_all()

toolbar = DebugToolbarExtension(app)


@app.route("/")
def homepage():
    """redirects to registration Form"""

    return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user: produce form & handle form submission."""

    form = RegisterForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username, password, email, first_name, last_name)

        db.session.add(user)
        db.session.commit()

        session["username"] = user.username

        # if logged in, redirect to secret page and flash msg
        flash("Welcome on board!!", "success")
        return redirect(f"/users/{user.username}")

    else:
        return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Generate login form and handle login"""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
     
        user = User.authenticate(username, password)

        if user:
            session["username"] = user.username 
            flash("Login successful", "success")
            return redirect(f"/users/{user.username}")

        else:
            flash("Login unsuccessful", "danger")
            form.username.errors = ["username or password is incorrect!"]

    return render_template("login.html", form=form)



@app.route("/users/<username>")
def user_page(username):
    """Example hidden page for logged-in users only."""
    user=User.query.filter_by(username=username).first()
    if session['username'] != user.username:
        flash("You must be logged in to view!", "warning")
        return redirect("/")
    else:
        
       
        return render_template("user_info.html", user=user)


@app.route("/users/<username>/delete", methods=['POST'])
def delete_user(username):
    """Example hidden page for logged-in users only."""
    user=User.query.filter_by(username=username).first()
    if session['username'] != user.username:
        flash("You do not have permission to delete!", "warning")
        return redirect("/")
    else:
        
        db.session.delete(user)
        db.session.commit()
        session.pop("username")
        flash(f"{user.first_name} {user.last_name} was deleted.", "success")
        return redirect("/")

@app.route("/logout")
def logout():
    """Logs user out, redirects to homepage"""

    session.pop("username")

    return redirect("/")

@app.route("/users/<username>/feedback/add", methods=['GET', 'POST'])
def feedback_form(username):
    
    form = FeedbackForm()
    user = User.query.get_or_404(username)
    if session['username'] != user.username:
        flash("you need to login first!", "warning")
        return redirect("/")
    else:
       if form.validate_on_submit():
           
           title= form.title.data
           content = form.content.data

           feedback = Feedback(title=title, content=content, username=username)
           db.session.add(feedback)
           db.session.commit()
           return redirect(f"/users/{session['username']}")
       
           
    return render_template("feedback_form.html", form=form, user=user)


@app.route("/feedback/<feedback_id>/update", methods=['GET','POST'])
def update_feedback(feedback_id):
    feedback=Feedback.query.get_or_404(feedback_id)
    form = FeedbackForm(title=feedback.title, content=feedback.content)
     
    if session['username'] != feedback.username:
        flash("you need to login first!", "warning")
        return redirect("/")
    else:
      
       if form.validate_on_submit():           
           feedback.title = form.title.data
           feedback.content = form.content.data
           db.session.add(feedback)
           db.session.commit()
           flash("Your feedback is updated successfully", "success")
           return redirect(f"/users/{session['username']}")
    return render_template("edit_feedback.html", form=form, feedback=feedback)


@app.route("/feedback/<feedback_id>/delete", methods=['POST'])
def delete_feedback(feedback_id):
     feedback=Feedback.query.get_or_404(feedback_id)
     if session['username'] != feedback.username:
        flash("You do not have permission to delete!", "warning")
        return redirect("/")
     else:
        
        db.session.delete(feedback)
        db.session.commit()
        
        flash(f"{feedback.title} was deleted.", "success")
        return redirect(f"/users/{session['username']}")





       
    
