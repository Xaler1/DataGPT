from peewee import SqliteDatabase, Model, CharField, IntegerField, BooleanField

db = SqliteDatabase('auth.db')


class User(Model):
    """
    A database user model.
    Stores the username, name, email, password, gmail token and whether the user is approved.
    """
    username = CharField(unique=True)
    name = CharField()
    email = CharField()
    password = CharField()
    gmail_token = CharField(null=True)
    approved = BooleanField(default=False)

    class Meta:
        database = db

    def gmail_linked(self):
        return self.gmail_token is not None

    def __str__(self):
        return f"User {self.username} ({self.name})"


db.connect()
db.create_tables([User])