from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("export/board/<int:board_id>.json", views.export_board, name="export_board"),
    path("export/list/<int:list_id>.json", views.export_list, name="export_list"),
    path("export/task/<int:task_id>.json", views.export_task, name="export_task"),
    re_path(r"^(?P<board_id>\d+)-(?P<slug>[-\w]*)/$", views.board_page, name="board"),
    re_path(r"^(?P<board_id>\d+)-(?P<slug>[-\w]*)/archive/$", views.archive_page, name="archive"),
]
