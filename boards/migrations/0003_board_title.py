from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("boards", "0002_board_slug")]

    operations = [migrations.RenameField("board", "name", "title")]
