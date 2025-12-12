from django.contrib.auth import get_user_model
from django.test import TestCase

from tasks.models import Comment, Task

User = get_user_model()


class TaskModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="test123")

    def test_create_task(self):
        task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            creator=self.user,
        )
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.creator, self.user)
        self.assertFalse(task.is_completed)
        self.assertIsNone(task.assignee)

    def test_task_str(self):
        task = Task.objects.create(title="My Task", creator=self.user)
        self.assertEqual(str(task), "My Task")

    def test_task_ordering(self):
        task1 = Task.objects.create(title="Task 1", creator=self.user)
        task2 = Task.objects.create(title="Task 2", creator=self.user)
        tasks = Task.objects.all()
        self.assertEqual(tasks[0], task2)
        self.assertEqual(tasks[1], task1)

    def test_cascade_delete_creator(self):
        user = User.objects.create_user(username="temp_user", password="test123")
        task = Task.objects.create(title="Task", creator=user)
        task_id = task.id
        user.delete()
        self.assertFalse(Task.objects.filter(id=task_id).exists())

    def test_set_null_assignee(self):
        assignee = User.objects.create_user(username="assignee", password="test123")
        task = Task.objects.create(title="Task", creator=self.user, assignee=assignee)
        assignee.delete()
        task.refresh_from_db()
        self.assertIsNone(task.assignee)


class CommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="test123")
        cls.task = Task.objects.create(title="Test Task", creator=cls.user)

    def test_create_comment(self):
        comment = Comment.objects.create(
            task=self.task, author=self.user, text="Test comment"
        )
        self.assertEqual(comment.task, self.task)
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.text, "Test comment")

    def test_comment_str(self):
        comment = Comment.objects.create(
            task=self.task, author=self.user, text="Comment"
        )
        expected = f"Comment by {self.user} on {self.task}"
        self.assertEqual(str(comment), expected)

    def test_cascade_delete_task(self):
        task = Task.objects.create(title="Temp Task", creator=self.user)
        comment = Comment.objects.create(task=task, author=self.user, text="Comment")
        comment_id = comment.id
        task.delete()
        self.assertFalse(Comment.objects.filter(id=comment_id).exists())

    def test_cascade_delete_author(self):
        user = User.objects.create_user(username="temp_author", password="test123")
        comment = Comment.objects.create(task=self.task, author=user, text="Comment")
        comment_id = comment.id
        user.delete()
        self.assertFalse(Comment.objects.filter(id=comment_id).exists())
