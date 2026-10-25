from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("export/board/<int:board_id>.json", views.export_board, name="export_board"),
    path("export/list/<int:list_id>.json", views.export_list, name="export_list"),
    path("export/task/<int:task_id>.json", views.export_task, name="export_task"),
    path("<slug:username>/<slug:slug>/", views.board_page, name="board"),
    path("<slug:username>/<slug:slug>/archive/", views.archive_page, name="archive"),
]
