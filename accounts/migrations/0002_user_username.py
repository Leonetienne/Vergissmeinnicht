from django.db import migrations, models


def fill_usernames(apps, schema_editor):
    from accounts.models import RESERVED_USERNAMES, unique_slug

    User = apps.get_model("accounts", "User")
    taken = set(RESERVED_USERNAMES)
    for user in User.objects.order_by("id"):
        user.username = unique_slug(user.display_name or user.email.split("@")[0], taken, "user")
        taken.add(user.username)
        user.save(update_fields=["username"])


class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial")]

    operations = [
        migrations.AddField("user", "username", models.SlugField(max_length=70, null=True)),
        migrations.RunPython(fill_usernames, migrations.RunPython.noop),
        migrations.AlterField("user", "username", models.SlugField(max_length=70, unique=True)),
    ]
