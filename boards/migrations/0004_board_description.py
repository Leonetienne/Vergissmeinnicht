from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("boards", "0003_board_title")]

    operations = [migrations.AddField("board", "description", models.TextField(blank=True))]
