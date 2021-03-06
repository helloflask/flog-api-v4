from random import randint

from faker import Faker
from flask import current_app
from rich import print
from rich.progress import track

from .models import Column
from .models import Comment
from .models import db
from .models import Group
from .models import Message
from .models import Notification
from .models import Post
from .models import User
from .utils import lower_username

fake = Faker()


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#           WARNING:   DO NOT USE FAKE DATA IN PRODUCTION ENVIRONMENT!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


def progress_bar(name: str, count: int) -> None:
    if not current_app.config:
        print(f"\ngenerating {name}: [magenta]{count}[/magenta]")


def users(count: int = 10) -> None:
    """Generates fake users"""
    progress_bar("users", count)
    for _ in track(range(count), description="progress"):
        name = fake.name()
        username = lower_username(name)
        # Ensure the username is unique.
        if User.query.filter_by(username=username).first() is not None:
            continue
        user = User(
            username=username,
            name=name,
            email=fake.email(),
            confirmed=True,
        )
        user.set_password("123456")
        db.session.add(user)
    db.session.commit()


def posts(count: int = 10, private: bool = None) -> None:
    """Generates fake posts"""
    progress_bar("posts", count)
    for _ in track(range(count), description="progress"):
        post = Post(
            title=fake.word() + " " + fake.word(),
            content=fake.text(randint(100, 300)),
            timestamp=fake.date_time_this_year(),
            author=User.query.get(randint(1, User.query.count())),
            private=bool(randint(0, 1)) if private is None else private,
        )
        db.session.add(post)
    db.session.commit()


def comments(count: int = 10) -> None:
    """Generates fake comments for posts."""
    progress_bar("comments", count)
    for _ in track(range(count), description="progress"):
        filt = Post.query.filter(~Post.private)
        comment = Comment(
            author=User.query.get(randint(1, User.query.count())),
            post=filt.all()[randint(1, filt.count() - 1)],
            body=fake.text(),
        )
        db.session.add(comment)
    db.session.commit()


def notifications(count: int, receiver: User = None) -> None:
    """Generates fake notifications"""
    progress_bar("notifications", count)
    for _ in track(range(count), description="progress"):
        if receiver is None:
            admin = User.query.filter_by(is_admin=True).first()
            receiver = admin
        notification = Notification(
            message=fake.sentence(),
            receiver=receiver,
        )
        db.session.add(notification)
    db.session.commit()


def groups(count: int) -> None:
    """Generates fake user groups"""
    progress_bar("groups", count)
    for _ in track(range(count), description="progress"):
        manager = User.query.get(randint(1, User.query.count()))
        group = Group(name=fake.sentence(), manager=manager)
        if manager:
            manager.join_group(group)
            db.session.add(group)
    db.session.commit()


def columns(count: int) -> None:
    progress_bar("columns", count)
    for _ in track(range(count), description="progress"):
        posts = list({Post.query.get(randint(1, Post.query.count())) for _ in range(5)})
        author = User.query.get(randint(1, User.query.count()))
        column = Column(name=fake.sentence(), author=author, posts=posts)
        db.session.add(column)
    db.session.commit()
    top = Column.query.get(randint(1, Column.query.count()))
    while top is None:
        top = Column.query.get(randint(1, Column.query.count()))
    db.session.commit()


def messages(count: int) -> None:
    progress_bar("messages", count)
    for _ in track(range(count), description="progress"):
        group = Group.query.get(randint(1, Group.query.count()))
        message = Message(group=group, body=fake.sentence())
        db.session.add(message)
    db.session.commit()
