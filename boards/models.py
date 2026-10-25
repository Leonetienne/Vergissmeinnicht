from django.conf import settings
from django.db import models
from django.utils.text import slugify


def slug_for(name, fallback):
    return slugify(name)[:60] or fallback


class Board(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="boards")
    name = models.CharField(max_length=100)
    emoji = models.CharField(max_length=32, blank=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return self.name

    @property
    def slug(self):
        return slug_for(self.name, "board")

    def get_absolute_url(self):
        return f"/{self.id}-{self.slug}/"


class Share(models.Model):
    OBSERVER = "observer"
    EDITOR = "editor"
    ROLES = [(OBSERVER, "Observer"), (EDITOR, "Editor")]

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="shares")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shares")
    role = models.CharField(max_length=8, choices=ROLES, default=OBSERVER)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["board", "user"], name="one_share_per_user")]


class List(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="lists")
    title = models.CharField(max_length=100, blank=True)
    is_default = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    @property
    def slug(self):
        return slug_for(self.title, "list")


class Task(models.Model):
    OPEN = "open"
    DONE = "done"
    ARCHIVED = "archived"
    STATES = [OPEN, DONE, ARCHIVED]
    COLOURS = ["none", "red", "orange", "yellow", "green", "blue", "purple", "grey", "turquoise"]

    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    state = models.CharField(max_length=8, default=OPEN)
    position = models.PositiveIntegerField(default=0)
    due_date = models.DateField(null=True, blank=True)
    colour = models.CharField(max_length=10, default="none")
    note = models.TextField(blank=True)
    reminded_soon = models.BooleanField(default=False)
    reminded_due = models.BooleanField(default=False)

    @property
    def slug(self):
        return slug_for(self.title, "task")

    @property
    def state_rank(self):
        return self.STATES.index(self.state)
