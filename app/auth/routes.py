from flask import render_template, session, redirect, url_for, g, flash, current_app
from app.auth import auth
from app.auth.forms import (
    RegistrationForm,
    LoginForm,
    EditAccountInfoForm,
    EditAccountPasswordForm,
    LogOutForm,
    DeleteAccountForm,
    ForgotPasswordForm,
    ResetPasswordForm,
)
from sqlalchemy import select
from app import db, mail
from app.models import User, PasswordReset
from app.utils.auth import (
    login_user,
    generate_hash,
    login_required,
    generate_password_reset_token,
)
from app.utils.form import EmailUnique, UsernameUnique
from app.utils.main import delete_kelma
from flask import request
from datetime import datetime, timedelta

# TODO: Add show password option in register, login, change password, reset password
# TODO: Add confirm password field in register, change password


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,  # pyright: ignore[reportCallIssue]
            email=form.email.data,  # pyright: ignore[reportCallIssue]
            password=generate_hash(
                form.password.data
            ),  # pyright: ignore[reportCallIssue]
        )
        db.session.add(user)
        db.session.commit()
        login_user(user.id, form.remember_me.data)
        return redirect(url_for("main.home"))
    return render_template("auth.html.j2", form=form, register=True)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = generate_hash(form.password.data)
        user = db.session.execute(
            db.select(User).filter_by(
                username=form.username_or_email.data, password=password
            )
        ).scalar_one_or_none()
        if not user:
            user = db.session.execute(
                db.select(User).filter_by(
                    email=form.username_or_email.data, password=password
                )
            ).scalar_one_or_none()
        if not user:
            flash("بيانات تسجيل دخول خاطئه!", "error")
        else:
            login_user(user.id, form.remember_me.data)
            return redirect(url_for("main.home"))
    return render_template("auth.html.j2", form=form, register=False)


@auth.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        email = form.email.data
        user = db.session.execute(select(User).filter_by(email=email)).scalar_one()

        if user.password_reset is None:
            user.password_reset = PasswordReset(
                token=generate_password_reset_token(),
            )

        user.password_reset.expire = datetime.now() + timedelta(days=1)
        reset_url = url_for(
            "auth.reset_password", token=user.password_reset.token, _external=True
        )
        mail.send_message(
            subject="Reset Password For Your Kelma Account",
            sender=("Kelma", current_app.config["MAIL_DEFAULT_SENDER"]),
            recipients=[email],
            body=f"Here is you Kelma reset password link:\n{reset_url}\n\nIf you haven't requested this just ignore this email.",
        )
        flash(f"تم ارسال رابط اعاده تعيين كلمة المرور بنجاح ل {email}", "success")
        db.session.commit()
        return redirect(url_for("auth.forgot_password"))

    return render_template("forgot_password.html.j2", form=form)


@auth.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    token = request.args.get("token")

    if token is None:
        flash("لم يتم ادخال اي رمز!", "error")
        return render_template("status.html.j2")

    reset_entry = db.session.execute(
        select(PasswordReset).filter_by(token=token)
    ).scalar_one_or_none()

    if reset_entry is None:
        flash("هذا الرابط غير صالح!", "error")
        return render_template("status.html.j2")

    if datetime.now() >= reset_entry.expire:
        flash("لقد انتهت صلاحية هذا الرابط!", "error")
        return render_template("status.html.j2")

    form = ResetPasswordForm()

    if form.validate_on_submit():
        password = form.password.data
        password_hash = generate_hash(password)
        reset_entry.user.password = password_hash
        flash("لقد تم تغيير كلمة مرورك بنجاح!", "success")
        db.session.delete(reset_entry)
        db.session.commit()
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html.j2", form=form)


@auth.route("/account-settings", methods=["GET", "POST"])
@login_required
def account_settings():
    edit_acc_form = EditAccountInfoForm(obj=g.user, prefix="edit_acc")
    edit_pass_form = EditAccountPasswordForm(prefix="edit_pass")
    logout_form = LogOutForm(prefix="logout")
    delete_acc_form = DeleteAccountForm(prefix="delete_acc")
    err_in_password_form = False

    if edit_acc_form.edit_info.data and edit_account(edit_acc_form):
        return redirect(url_for("auth.account_settings"))
    elif edit_pass_form.edit_password.data:
        if edit_password(edit_pass_form):
            return redirect(url_for("auth.account_settings"))
        err_in_password_form = True
    elif logout_form.logout.data and logout():
        return redirect(url_for("main.home"))
    elif delete_acc_form.delete.data and delete_account():
        return redirect(url_for("main.home"))

    return render_template(
        "account_settings.html.j2",
        edit_acc_form=edit_acc_form,
        edit_pass_form=edit_pass_form,
        logout_form=logout_form,
        delete_acc_form=delete_acc_form,
        err_in_password_form=err_in_password_form,
    )


def edit_account(edit_acc_form):
    valid = edit_acc_form.validate(
        extra_validators={
            "username": [
                UsernameUnique(
                    message="هذا الاسم للمستخدم موجود بالفعل!",
                    exclude=[g.user.username],
                )
            ],
            "email": [
                EmailUnique(
                    message="هذا البريد الالكتروني موجود بالفعل!",
                    exclude=[g.user.email],
                )
            ],
        }
    )

    if valid:
        g.user.username = edit_acc_form.username.data
        g.user.email = edit_acc_form.email.data
        try:
            db.session.commit()
        except Exception as e:
            flash("لقد حدثت مشكلة غير متوقعة أثناء تحديث بياناتك!", "error")
        else:
            flash("لقد تم تحديث بياناتك بنجاح!", "success")
            return True

    return False


def edit_password(edit_pass_form):
    if edit_pass_form.validate():
        old_password = edit_pass_form.old_password.data
        if g.user.password == generate_hash(old_password):
            new_password = edit_pass_form.new_password.data
            g.user.password = generate_hash(new_password)
            try:
                db.session.commit()
            except:
                flash(
                    "لقد حدثت مشكلة غير متوقعة أثناء تحديث كلمة المرور لحسابك!", "error"
                )
            else:
                flash("لقد تم تحديث كلمة المرور لحسابك بنجاح!", "success")
                return True
        else:
            flash("كلمة المرور القديمة غير صحيحة!")

    return False


def logout():
    session.clear()
    return True


def delete_account():
    if g.user.public_kelma:
        delete_kelma(g.user.public_kelma)
    db.session.delete(g.user)
    try:
        db.session.commit()
    except:
        flash("لقد حدثت مشكلة غير متوقعة أثناء حذف حسابك!", "error")
    else:
        return True

    return False


@auth.route("/testing")
def testing():
    return render_template("forgot_password_status.html.j2")
