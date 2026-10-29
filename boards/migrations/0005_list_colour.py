from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("boards", "0004_board_description")]

    operations = [migrations.AddField("list", "colour", models.CharField(default="none", max_length=10))]
