from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from tasks.models import Comment, Task
from tasks.permissions import (
    IsAuthorOrAdmin,
    IsCreatorOrAdmin,
    IsCreatorOrAssigneeOrAdmin,
)

User = get_user_model()


class IsCreatorOrAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.creator = User.objects.create_user(username="creator", password="pass123")
        cls.other_user = User.objects.create_user(username="other", password="pass123")
        cls.admin = User.objects.create_user(
            username="admin", password="pass123", is_staff=True
        )
        cls.task = Task.objects.create(title="Task", creator=cls.creator)
        cls.permission = IsCreatorOrAdmin()
        cls.factory = RequestFactory()

    def test_creator_has_permission(self):
        request = self.factory.get("/")
        request.user = self.creator
        self.assertTrue(self.permission.has_object_permission(request, None, self.task))

    def test_other_user_no_permission(self):
        request = self.factory.get("/")
        request.user = self.other_user
        self.assertFalse(
            self.permission.has_object_permission(request, None, self.task)
        )

    def test_admin_has_permission(self):
        request = self.factory.get("/")
        request.user = self.admin
        self.assertTrue(self.permission.has_object_permission(request, None, self.task))


class IsCreatorOrAssigneeOrAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.creator = User.objects.create_user(username="creator", password="pass123")
        cls.assignee = User.objects.create_user(username="assignee", password="pass123")
        cls.other_user = User.objects.create_user(username="other", password="pass123")
        cls.admin = User.objects.create_user(
            username="admin", password="pass123", is_staff=True
        )
        cls.task = Task.objects.create(
            title="Task", creator=cls.creator, assignee=cls.assignee
        )
        cls.permission = IsCreatorOrAssigneeOrAdmin()
        cls.factory = RequestFactory()

    def test_creator_has_permission(self):
        request = self.factory.get("/")
        request.user = self.creator
        self.assertTrue(self.permission.has_object_permission(request, None, self.task))

    def test_assignee_has_permission(self):
        request = self.factory.get("/")
        request.user = self.assignee
        self.assertTrue(self.permission.has_object_permission(request, None, self.task))

    def test_other_user_no_permission(self):
        request = self.factory.get("/")
        request.user = self.other_user
        self.assertFalse(
            self.permission.has_object_permission(request, None, self.task)
        )

    def test_admin_has_permission(self):
        request = self.factory.get("/")
        request.user = self.admin
        self.assertTrue(self.permission.has_object_permission(request, None, self.task))


class IsAuthorOrAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username="author", password="pass123")
        cls.other_user = User.objects.create_user(username="other", password="pass123")
        cls.admin = User.objects.create_user(
            username="admin", password="pass123", is_staff=True
        )
        cls.task = Task.objects.create(title="Task", creator=cls.author)
        cls.comment = Comment.objects.create(
            task=cls.task, author=cls.author, text="Comment"
        )
        cls.permission = IsAuthorOrAdmin()
        cls.factory = RequestFactory()

    def test_author_has_permission(self):
        request = self.factory.get("/")
        request.user = self.author
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.comment)
        )

    def test_other_user_no_permission(self):
        request = self.factory.get("/")
        request.user = self.other_user
        self.assertFalse(
            self.permission.has_object_permission(request, None, self.comment)
        )

    def test_admin_has_permission(self):
        request = self.factory.get("/")
        request.user = self.admin
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.comment)
        )
