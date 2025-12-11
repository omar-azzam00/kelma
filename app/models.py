from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, func, CHAR, TEXT, DATE
from sqlalchemy.dialects.mysql import TINYTEXT, TINYINT
from app import db
from datetime import date, datetime, timedelta
from sqlalchemy import case, func, Index, literal
from app.utils.paymob import PAYMENT_STATUS_CODE
from typing import Optional
from flask import url_for, current_app
import os



class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    # any valid email address must not exceed 254 characters
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password: Mapped[str] = mapped_column(CHAR(64))
    kelma: Mapped[Kelma] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    orders: Mapped[list[Order]] = relationship(
        back_populates="user", passive_deletes=True
    )
    password_reset: Mapped[PasswordReset] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @property
    def public_kelma(self):
        kelma = self.kelma
        if kelma and kelma.sort is None:
            kelma = None
        return kelma


class Kelma(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    # after you learn about join use this
    # user_id: Mapped[int] = mapped_column(
    #     ForeignKey("user.username", onupdate="CASCADE", ondelete="CASCADE"),
    #     unique=True,
    # )
    image_fn: Mapped[str] = mapped_column(CHAR(28))
    display_name: Mapped[str] = mapped_column(TINYTEXT())
    username: Mapped[str] = mapped_column(
        ForeignKey("user.username", onupdate="CASCADE", ondelete="CASCADE"),
        unique=True,
    )
    content: Mapped[str] = mapped_column(TEXT())
    # when sort is null this mean that this kelma is not committed and user should be considered not to have any kelma.
    # sort is supposed to be unique but we can't enforce this constraint as some function like shift_sort_from
    # make the kelmas sort temporarily not unique and mysql don't have a deferred constraint like postgresql
    sort: Mapped[Optional[int]] = mapped_column(unique=True)
    reserve_end: Mapped[Optional[date]] = mapped_column(DATE())
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp()
    )
    version: Mapped[int] = mapped_column(server_default=literal(0))
    user: Mapped[User] = relationship(back_populates="kelma")

    @property
    def public(self):
        return self.sort != None

    @property
    def normal(self):
        return self.reserve_end == None

    @property
    def premium(self):
        return self.reserve_end != None

    @property
    def image_url(self):
        if self.image_fn is None:
            return None

        return url_for(
            "static",
            filename=f'{current_app.config["PROFILE_IMGS_PATH_URL"]}/{self.image_fn}',
            _external=True,
        )

    @property
    def image_path(self):
        if self.image_fn is None:
            return None

        return os.path.join(
            current_app.static_folder,
            current_app.config["PROFILE_IMGS_PATH_OS"],
            self.image_fn,
        )

    def _to_json(self):
        """It returns a public json serializable dict that contains the specific fields to be used with kelmas_api"""

        return {
            "id": self.id,
            "username": self.username,
            "image_url": self.image_url,
            "display_name": self.display_name,
            "content": self.content,
            "sort": self.sort,
            "premium": self.premium,
        }
        
Index("kelmas_search", Kelma.username, Kelma.display_name, Kelma.content, mysql_prefix="FULLTEXT")

class Order(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("user.id", onupdate="CASCADE", ondelete="SET NULL"),
    )
    email: Mapped[str] = mapped_column(String(254))
    price_for_month: Mapped[int]
    months: Mapped[int] = mapped_column(TINYINT())
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp()
    )
    reserve_end: Mapped[Optional[date]] = mapped_column(DATE())
    status_code: Mapped[int] = mapped_column(
        TINYINT(), default=PAYMENT_STATUS_CODE["ERROR_UNKNOWN"]
    )
    user: Mapped[User] = relationship(back_populates="orders")

from app.utils.auth import generate_password_reset_token

class PasswordReset(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"), unique=True
    )
    token: Mapped[str] = mapped_column(String(12))
    expire: Mapped[datetime]
    user: Mapped[User] = relationship(back_populates="password_reset")
