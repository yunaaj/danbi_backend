from django.db import transaction
from django.forms.models import model_to_dict
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User, Task, SubTask

TEAMS = {'단비', '다래', '블라블라', '철로', '땅이', '해태', '수피'}


@api_view(['GET', 'POST'])
def tasks_handler(request):
    try:
        if request.method == 'POST':
            create_task(request.COOKIES.get('user_id'), request.data)
            return Response(status=status.HTTP_201_CREATED)
        elif request.method == 'GET':
            res = get_tasks(request.COOKIES.get('user_id'))
            return Response(res, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except ValueError as v:
        error_message = f'Bad request: {v}'
        return Response({'error': error_message}, status=status.HTTP_200_OK)
    except Exception:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def task_handler(request, task_id):
    try:
        if request.method == 'PUT':
            update_task(request.COOKIES.get('user_id'), request.data.get('teams'), task_id)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except ValueError as v:
        error_message = f'Bad request: {v}'
        return Response({'error': error_message}, status=status.HTTP_200_OK)
    except Exception:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def subtask_handler(request, subtask_id):
    try:
        if request.method == 'PUT':
            complete_subtask(request.COOKIES.get('user_id'), subtask_id)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except ValueError as v:
        error_message = f'Bad request: {v}'
        return Response({'error': error_message}, status=status.HTTP_200_OK)
    except Exception:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@transaction.atomic
def get_tasks(requested_user_id):
    team = User.objects.get(user_id=requested_user_id).team

    task_id_set = set(
        subtask.task_id.task_id for subtask in SubTask.objects.select_related('task_id').filter(team=team)
    ).union(set(
        task.task_id for task in Task.objects.filter(team=team))
    )

    response = {'tasks': []}
    tasks = Task.objects.filter(task_id__in=task_id_set).order_by('-task_id')
    subtasks = SubTask.objects.filter(task_id__in=task_id_set)

    # task, subtask 조립
    for task in tasks:
        task_info = model_to_dict(task)
        subtask_infos = []

        for subtask in subtasks:
            subtask_info = model_to_dict(subtask)

            if subtask_info['task_id'] == task_info['task_id']:
                subtask_infos.append(subtask_info)

        task_info['subtasks'] = subtask_infos
        response['tasks'].append(task_info)

    return response


@transaction.atomic
def create_task(requested_user_id, data):
    team = User.objects.get(user_id=requested_user_id).team
    title = data.get('title')
    content = data.get('content')

    task = Task.objects.create(create_user=requested_user_id, team=team, title=title, content=content)

    subtask_infos = data.get('subtask_infos')
    if not subtask_infos:
        raise ValueError('No subtask found.')

    for subtask_info in subtask_infos:
        if subtask_info['team'] in TEAMS:
            SubTask.objects.create(task_id=task, team=subtask_info['team'])
        else:
            raise ValueError('Invalid team.')


@transaction.atomic
def update_task(requested_user_id, requested_teams, task_id):
    user_id = int(requested_user_id)
    tasks = Task.objects.get(task_id=task_id)
    if tasks.create_user != user_id:
        raise ValueError('Only users who have created it can modify.')

    SubTask.objects.filter(task_id=task_id, is_complete=False).delete()

    if not requested_teams:
        raise ValueError('No teams requested.')
    for team in requested_teams:
        if team not in TEAMS:
            raise ValueError('Invalid team.')
        SubTask.objects.create(task_id=tasks, team=team)


@transaction.atomic
def complete_subtask(requested_user_id, subtask_id):
    user_info = User.objects.get(user_id=requested_user_id)
    subtask_info = SubTask.objects.get(subtask_id=subtask_id)

    if subtask_info.team != user_info.team:
        raise ValueError('This team cannot update this subtask.')

    now = timezone.now()
    subtask_info.is_complete = True
    subtask_info.completed_date = now
    subtask_info.save()

    task_id = subtask_info.task_id.task_id
    subtask_infos = SubTask.objects.filter(task_id=task_id)
    for subtask in subtask_infos:
        if subtask.is_complete is False:
            return

    task_info = Task.objects.get(task_id=task_id)
    task_info.is_complete = True
    task_info.completed_date = now
    task_info.save()
