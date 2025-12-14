from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, RadioField, SubmitField
from wtforms.validators import Length, InputRequired, Optional
from flask_wtf.file import FileField, FileAllowed, FileRequired, FileSize
from more_itertools import unique_everseen
from app.utils.form import RequiredIfField

# from app.utils.form import ValidImage


def create_image_field(before_extra_validators=[], after_extra_validators=[], **kwargs):
    return FileField(
        "",
        validators=[
            *before_extra_validators,
            FileAllowed(IMAGE_TYPES.keys()),
            FileSize(MAX_SIZE),
            *after_extra_validators,
        ],
        **kwargs,
    )


def create_display_name_field(
    field_name="اسم العرض",
    before_extra_validators=[],
    after_extra_validators=[],
    **kwargs,
):
    return StringField(
        field_name,
        validators=[
            *before_extra_validators,
            InputRequired(f"{field_name} لا يمكن أن يكون فارغا!"),
            Length(
                max=128, message=f"{field_name} لا يمكن أن يكون أكثر من %(max)d حرفا!"
            ),
            *after_extra_validators,
        ],
        **kwargs,
    )


def create_content_field(
    field_name="المحتوى",
    before_extra_validators=[],
    after_extra_validators=[],
    **kwargs,
):
    return TextAreaField(
        field_name,
        validators=[
            *before_extra_validators,
            InputRequired(f"{field_name} لا يمكن أن يكون فارغا!"),
            Length(
                max=512, message=f"{field_name} لا يمكن أن يكون أكثر من %(max)d حرفا!"
            ),
            *after_extra_validators,
        ],
        **kwargs,
    )


def create_reserve_length_field(
    before_extra_validators=[],
    after_extra_validators=[],
    **kwargs,
):
    return RadioField(
        "",
        choices=[("1", "شهر"), ("3", "3 أشهر"), ("6", "6 أشهر")],
        validators=[
            *before_extra_validators,
            *after_extra_validators,
        ],
        coerce=lambda value: int(value),
        **kwargs,
    )


class KelmasSearchForm(FlaskForm):
    search_text = StringField(
        "البحث",
        validators=[
            Length(max=512, message="البحث لا يمكن أن يكون أكثر من %(max)d حرفا!"),
        ],
    )

MAX_MBS = 5
MAX_SIZE = MAX_MBS * 1000 * 1000

# max length for extension is 4 chars, or edit image_fn column length.
IMAGE_TYPES = {
    "jpg": "image/jpeg",
    "jpe": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    # PIL doesn't support svg
    # "svg": "image/svg+xml",
    "bmp": "image/bmp",
    "webp": "image/webp",
    "avif": "image/avif"
}

IMAGE_EXTS = unique_everseen(IMAGE_TYPES.keys())
IMAGE_MIMES = unique_everseen(IMAGE_TYPES.values())
IMAGE_MIMES_STR = ", ".join(IMAGE_MIMES)


class KelmaForm(FlaskForm):
    display_name = create_display_name_field()
    content = create_content_field()
    image = create_image_field()
    kelma_type = RadioField(
        "",
        choices=[
            ("normal", "كلمه عاديه"),
            ("top_twenty", "اول 20"),
        ],
        validators=[
            InputRequired("نوع الاشتراك لا يمكن أن يكون فارغا!"),
        ],
        coerce=lambda value: str(value),
    )
    reserve_length = create_reserve_length_field(
        [RequiredIfField("kelma_type", "top_twenty", "هذا الحقل مطلوب!")]
    )
    create = SubmitField("أنشئ كلمتي")
    edit = SubmitField("تعديل كلمتي")
    delete = SubmitField("ازالة الكلمة")


class PremiumKelmaForm(FlaskForm):
    display_name = create_display_name_field()
    content = create_content_field()
    image = create_image_field()
    edit = SubmitField("تعديل كلمتي")
    delete = SubmitField("ازالة الكلمة")


class ExtendReserveForm(FlaskForm):
    reserve_length = create_reserve_length_field([InputRequired("هذا الحقل مطلوب!")])
    extend = SubmitField("تمديد الحجز")
