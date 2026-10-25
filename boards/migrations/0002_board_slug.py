from django.db import migrations, models


def fill_slugs(apps, schema_editor):
    from accounts.models import unique_slug

    Board = apps.get_model("boards", "Board")
    taken = {}
    for board in Board.objects.order_by("id"):
        owned = taken.setdefault(board.owner_id, set())
        board.slug = unique_slug(board.name, owned, "board")
        owned.add(board.slug)
        board.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [("boards", "0001_initial"), ("accounts", "0002_user_username")]

    operations = [
        migrations.AddField("board", "slug", models.SlugField(max_length=70, default="")),
        migrations.RunPython(fill_slugs, migrations.RunPython.noop),
        migrations.AlterField("board", "slug", models.SlugField(max_length=70)),
        migrations.AddConstraint("board", models.UniqueConstraint(fields=["owner", "slug"], name="board_slug_per_owner")),
    ]
