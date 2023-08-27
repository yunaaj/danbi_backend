from django.test import TestCase
from .models import User, Task, SubTask
from .views import create_task, update_task, get_tasks, complete_subtask


class CreateTaskUnitTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(user_id=1, team='단비')


    def test_create_task_해피케이스(self):
        # given
        data = {
            'title': 'Happy case',
            'content': 'test1',
            'subtask_infos': [{'team': '단비'}, {'team': '다래'}, {'team': '철로'}]
        }

        # when
        create_task(requested_user_id=self.user.user_id, data=data)

        # then
        task_count = Task.objects.count()
        subtask_count = SubTask.objects.count()

        self.assertEqual(task_count, 1)
        self.assertEqual(subtask_count, 3)

        created_task = Task.objects.first()
        self.assertEqual(created_task.create_user, self.user.user_id)
        self.assertEqual(created_task.team, self.user.team)
        self.assertEqual(created_task.title, 'Happy case')
        self.assertEqual(created_task.content, 'test1')

        created_subtasks = SubTask.objects.all()
        self.assertEqual(created_subtasks[0].team, '단비')
        self.assertEqual(created_subtasks[1].team, '다래')
        self.assertEqual(created_subtasks[2].team, '철로')
        self.assertEqual(created_subtasks[0].task_id, created_task)
        self.assertEqual(created_subtasks[1].task_id, created_task)
        self.assertEqual(created_subtasks[2].task_id, created_task)


    def test_create_task_선택된_팀이_없음(self):
        # given
        data = {
            'title': 'no subtask case',
            'content': 'test1',
            'subtask_infos': []
        }

        # when
        with self.assertRaises(Exception) as context:
            create_task(requested_user_id=self.user.user_id, data=data)

        # then
        self.assertEqual(str(context.exception), 'No subtask found.')


    def test_create_task_주어진_7개_이외의_팀에게_할당(self):
        # given
        data = {
            'title': 'no subtask case',
            'content': 'test1',
            'subtask_infos': [{'team': '단비'}, {'team': '딴비'}]
        }

        # when
        with self.assertRaises(Exception) as context:
            create_task(requested_user_id=self.user.user_id, data=data)

        # then
        self.assertEqual(str(context.exception), 'Invalid team.')


class UpdateTaskUnitTest(TestCase):
    def setUp(self):
        self.task = Task.objects.create(create_user=1)


    def test_update_task_해피케이스(self):
        # given
        new_teams = ['단비', '다래']

        # when
        update_task(requested_user_id=1, requested_teams=new_teams, task_id=self.task.task_id)

        # then
        updated_task = Task.objects.get(task_id=self.task.task_id)
        updated_subtasks = SubTask.objects.filter(task_id=self.task.task_id)

        self.assertEqual(updated_task.create_user, 1)
        self.assertTrue(all(subtask.team in new_teams for subtask in updated_subtasks))


    def test_update_task_주어진_7개_이외의_팀에게_할당(self):
        # given
        invalid_teams = ['단비', '딴비']

        # when
        with self.assertRaises(Exception) as context:
            update_task(requested_user_id=1, requested_teams=invalid_teams, task_id=self.task.task_id)

        # then
        self.assertEqual(str(context.exception), 'Invalid team.')


    def test_update_task_0개팀에_할당(self):
        # given
        no_teams = None

        # when
        with self.assertRaises(Exception) as context:
            update_task(requested_user_id=1, requested_teams=no_teams, task_id=self.task.task_id)

        # then
        self.assertEqual(str(context.exception), 'No teams requested.')


    def test_update_task_태스크_생성자가_아님(self):
        # given
        new_teams = ['단비', '다래']

        # when
        with self.assertRaises(Exception) as context:
            update_task(requested_user_id=2, requested_teams=new_teams, task_id=self.task.task_id)

        # then
        self.assertEqual(str(context.exception), 'Only users who have created it can modify.')


    def test_update_task_해피케이스_completed_처리된_태스크_포함(self):
        # given
        new_teams = ['단비', '다래']
        SubTask.objects.create(task_id=self.task, team='철로', is_complete=True)

        # when
        update_task(requested_user_id=1, requested_teams=new_teams, task_id=self.task.task_id)

        # then
        self.assertEqual(SubTask.objects.filter(task_id=self.task.task_id).count(), 3)


class GetTasksUnitTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='user1', pwd='1234', team='단비')
        self.user2 = User.objects.create(username='user2', pwd='1234', team='단비')
        self.user3 = User.objects.create(username='user3', pwd='1234', team='다래')
        self.task1 = Task.objects.create(create_user=self.user2.user_id, team=self.user2.team)
        self.task2 = Task.objects.create(create_user=self.user3.user_id, team=self.user3.team)
        self.task3 = Task.objects.create(create_user=self.user3.user_id, team=self.user3.team)
        self.subtask1 = SubTask.objects.create(task_id=self.task1, team=self.user1.team)
        self.subtask2 = SubTask.objects.create(task_id=self.task2, team=self.user2.team)
        self.subtask3 = SubTask.objects.create(task_id=self.task2, team=self.user3.team)
        self.subtask4 = SubTask.objects.create(task_id=self.task3, team=self.user3.team)


    def test_retrieve_tasks_해피케이스(self):
        # when
        response = get_tasks(requested_user_id=self.user1.user_id)

        # then
        self.assertTrue('tasks' in response)
        self.assertEqual(len(response['tasks']), 2)

        task1_info = response['tasks'][1]
        self.assertEqual(task1_info['task_id'], self.task1.task_id)
        self.assertEqual(task1_info['create_user'], self.user2.user_id)
        self.assertEqual(task1_info['team'], self.user2.team)

        task2_info = response['tasks'][0]
        self.assertEqual(task2_info['task_id'], self.task2.task_id)
        self.assertEqual(task2_info['create_user'], self.user3.user_id)
        self.assertEqual(task2_info['team'], self.user3.team)

        self.assertEqual(len(task1_info['subtasks']), 1)
        self.assertEqual(len(task2_info['subtasks']), 2)


class CompleteSubTasksUnitTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='user1', pwd='1234', team='단비')
        self.user2 = User.objects.create(username='user2', pwd='1234', team='다래')
        self.task = Task.objects.create(create_user=self.user1.user_id, team=self.user1.team)
        self.subtask1 = SubTask.objects.create(task_id=self.task, team=self.user1.team)
        self.subtask2 = SubTask.objects.create(task_id=self.task, team=self.user1.team)


    def test_complete_subtask_해피케이스(self):
        # when
        complete_subtask(requested_user_id=self.user1.user_id, subtask_id=self.subtask1.subtask_id)

        # then (subtask1: 완료, subtask2: 미완료, task: 미완료)
        updated_subtask1 = SubTask.objects.get(subtask_id=self.subtask1.subtask_id)
        self.assertTrue(updated_subtask1.is_complete)
        self.assertIsNotNone(updated_subtask1.completed_date)

        updated_subtask2 = SubTask.objects.get(subtask_id=self.subtask2.subtask_id)
        self.assertFalse(updated_subtask2.is_complete)
        self.assertIsNone(updated_subtask2.completed_date)

        updated_task = Task.objects.get(task_id=self.task.task_id)
        self.assertFalse(updated_task.is_complete)
        self.assertIsNone(updated_task.completed_date)

        # when
        self.subtask2.is_complete = True
        self.subtask2.save()
        complete_subtask(requested_user_id=self.user1.user_id, subtask_id=self.subtask2.subtask_id)

        # then (subtask2: 완료 -> task: 완료)
        updated_task = Task.objects.get(task_id=self.task.task_id)
        self.assertTrue(updated_task.is_complete)
        self.assertIsNotNone(updated_task.completed_date)


    def test_complete_subtask_우리팀이_아님(self):
        # when
        with self.assertRaises(Exception) as context:
            complete_subtask(requested_user_id=self.user2.user_id, subtask_id=self.subtask1.subtask_id)

        # then
        self.assertEqual(str(context.exception), 'This team cannot update this subtask.')
