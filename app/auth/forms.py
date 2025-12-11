from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from app.utils.form import UsernameUnique, EmailUnique, EmailExists


def create_password_field(
    field_name, before_extra_validators=[], after_extra_validators=[]
):
    return PasswordField(
        field_name,
        validators=[
            *before_extra_validators,
            DataRequired("كلمة المرور لا يمكن أن تكون فارغة!"),
            Length(
                max=255, message="كلمة المرور لا يمكن أن تكون أكثر من %(max)d حرفا!"
            ),
            *after_extra_validators,
        ],
    )


def create_username_field(
    field_name, before_extra_validators=[], after_extra_validators=[]
):
    return StringField(
        field_name,
        validators=[
            *before_extra_validators,
            DataRequired("اسم المستخدم لا يمكن أن يكون فارغا!"),
            Regexp(
                r"\A\w*\Z",
                message="!اسم المستخدم يجب ان يحتوي علي الأرقام والأحرف الأبجدية أو _ فقط",
            ),
            Length(
                max=50, message="اسم المستخدم لا يمكن أن يكون أكثر من %(max)d حرفا!"
            ),
            *after_extra_validators,
        ],
    )


def create_email_field(
    field_name, before_extra_validators=[], after_extra_validators=[]
):
    return EmailField(
        field_name,
        validators=[
            *before_extra_validators,
            DataRequired("البريد الإلكتروني لا يمكن أن يكون فارغا!"),
            Length(
                max=254,
                message="البريد الإلكروني لا يمكن أن يكون أكثر من %(max)d حرفا!",
            ),
            Email("البريد الإلكتروني غير صالح!"),
            *after_extra_validators,
        ],
    )


def create_remember_me_field(field_name, default=True):
    return BooleanField(field_name, default=default)


def create_username_or_email_field(
    field_name, before_extra_validators=[], after_extra_validators=[]
):
    return StringField(
        field_name,
        validators=[
            *before_extra_validators,
            DataRequired("اسم المستخدم أو البريد الإلكتروني لا يمكن أن يكون فارغا!"),
            Length(
                max=254,
                message="اسم المستخدم أو البريد الإلكتروني لا يمكن أن يكون أكثر من %(max)d حرفا!",
            ),
            *after_extra_validators,
        ],
    )


# Example usage in a form:
class RegistrationForm(FlaskForm):
    username = create_username_field(
        "اسم المستخدم",
        after_extra_validators=[UsernameUnique("اسم المستخدم موجود بالفعل!")],
    )
    email = create_email_field(
        "البريد الإلكتروني",
        after_extra_validators=[EmailUnique("البريد الإلكتروني موجود بالفعل!")],
    )
    password = create_password_field("كلمة المرور")
    remember_me = create_remember_me_field("تذكرني")
    submit = SubmitField("انضم الآن")


class LoginForm(FlaskForm):
    username_or_email = create_username_or_email_field(
        "اسم المستخدم أو البريد الإلكتروني"
    )
    password = create_password_field("كلمة المرور")
    remember_me = create_remember_me_field("تذكرني")
    submit = SubmitField("تسجيل الدخول")


class ForgotPasswordForm(FlaskForm):
    email = create_email_field(
        "البريد الإلكتروني", after_extra_validators=[EmailExists()]
    )
    cont = SubmitField("متابعة")

class ResetPasswordForm(FlaskForm):
    password = create_password_field("كلمة المرور الجديدة")
    confirm_password = create_password_field("تأكيد كلمة المرور الجديدة", before_extra_validators=[
        EqualTo("password", "يحب ان يكون الحقلان متطابقان!")
    ])
    save = SubmitField("حفظ")
    

class EditAccountInfoForm(FlaskForm):
    username = create_username_field("اسم المستخدم")
    email = create_email_field("البريد الإلكتروني")
    edit_info = SubmitField("حفظ")


class EditAccountPasswordForm(FlaskForm):
    old_password = create_password_field("كلمة المرور القديمة")
    new_password = create_password_field("كلمة المرور الجديدة")
    edit_password = SubmitField("حفظ")


class DeleteAccountForm(FlaskForm):
    delete = SubmitField("حذف الحساب")


class LogOutForm(FlaskForm):
    logout = SubmitField("تسجيل الخروج")
