import json

from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render

from . import services as s
from .models import Task
from .serializers import board_data, board_with_lists, list_data, task_data


def _member_board(request, board_id, slug, suffix=""):
    try:
        board = s.get_board(request.user, board_id)
    except s.ServiceError:
        raise Http404
    if slug != board.slug:
        return board, redirect(board.get_absolute_url() + suffix)
    return board, None


def home(request):
    own, shared = s.boards_for(request.user)
    return render(request, "boards/home.html", {
        "page_data": {"own": [board_data(b) for b in own], "shared": [board_data(b) for b in shared]},
    })


def board_page(request, board_id, slug):
    board, redirect_response = _member_board(request, board_id, slug)
    if redirect_response:
        return redirect_response
    s.board_content(board, states=[Task.OPEN, Task.DONE])
    return render(request, "boards/board.html", {"board": board, "page_data": board_with_lists(board)})


def archive_page(request, board_id, slug):
    board, redirect_response = _member_board(request, board_id, slug, "archive/")
    if redirect_response:
        return redirect_response
    s.board_content(board, states=[Task.ARCHIVED])
    return render(request, "boards/archive.html", {"board": board, "page_data": board_with_lists(board)})


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
    return _download(list_data(lst, s.ordered_tasks(Task.objects.filter(list=lst))), lst.slug)


def export_task(request, task_id):
    try:
        task = s.get_task(request.user, task_id)
    except s.ServiceError:
        raise Http404
    return _download(task_data(task), task.slug)
