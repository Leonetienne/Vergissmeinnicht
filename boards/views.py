import json

from django.http import Http404, HttpResponse
from django.shortcuts import render

from . import services as s
from .models import Task
from .serializers import board_data, board_with_lists, list_data, task_data


def _member_board(request, username, slug):
    try:
        return s.get_board_by_slug(request.user, username, slug)
    except s.ServiceError:
        raise Http404


def home(request):
    own, shared = s.boards_for(request.user)
    return render(request, "boards/home.html", {
        "page_data": {"own": [board_data(b) for b in own], "shared": [board_data(b) for b in shared]},
    })


def board_page(request, username, slug, archive=False):
    board = _member_board(request, username, slug)
    states = [Task.ARCHIVED] if archive else [Task.OPEN, Task.DONE]
    s.board_content(board, states=states)
    return render(request, "boards/board.html", {
        "board": board, "archive": archive, "page_data": board_with_lists(board),
    })


def archive_page(request, username, slug):
    return board_page(request, username, slug, archive=True)


def _download(data, slug):
    response = HttpResponse(json.dumps(data, indent=2, ensure_ascii=False), content_type="application/json")
    response["Content-Disposition"] = f'attachment; filename="{slug}.json"'
    return response


def export_board(request, board_id):
    try:
        board = s.board_content(s.get_board(request.user, board_id))
    except s.ServiceError:
        raise Http404
    return _download(board_with_lists(board), board.slug)


def export_list(request, list_id):
    try:
        lst = s.get_list(request.user, list_id)
    except s.ServiceError:
        raise Http404
    return _download(list_data(lst, s.ordered_tasks(Task.objects.filter(list=lst))), f"{lst.board.slug}-{lst.slug}")


def export_task(request, task_id):
    try:
        task = s.get_task(request.user, task_id)
    except s.ServiceError:
        raise Http404
    return _download(task_data(task), task.slug)
