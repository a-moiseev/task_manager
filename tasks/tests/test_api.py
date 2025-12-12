from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from tasks.models import Comment, Task

User = get_user_model()


class TaskAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username="user1", password="pass123")
        cls.user2 = User.objects.create_user(username="user2", password="pass123")

    def test_create_task_authenticated(self):
        self.client.force_authenticate(user=self.user1)
        data = {"title": "New Task", "description": "Task description"}
        response = self.client.post("/api/tasks/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Task")
        self.assertEqual(Task.objects.count(), 1)
        task = Task.objects.first()
        self.assertEqual(task.creator, self.user1)

    def test_create_task_unauthenticated(self):
        data = {"title": "New Task"}
        response = self.client.post("/api/tasks/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_tasks(self):
        Task.objects.create(title="Task 1", creator=self.user1)
        Task.objects.create(title="Task 2", creator=self.user2)
        self.client.force_authenticate(user=self.user1)
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_task(self):
        task = Task.objects.create(title="Task", creator=self.user1)
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f"/api/tasks/{task.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Task")

    def test_update_own_task(self):
        task = Task.objects.create(title="Old Title", creator=self.user1)
        self.client.force_authenticate(user=self.user1)
        data = {"title": "New Title", "description": "Updated"}
        response = self.client.patch(f"/api/tasks/{task.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, "New Title")

    def test_update_other_user_task_forbidden(self):
        task = Task.objects.create(title="Task", creator=self.user1)
        self.client.force_authenticate(user=self.user2)
        data = {"title": "Hacked"}
        response = self.client.patch(f"/api/tasks/{task.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_task(self):
        task = Task.objects.create(title="Task", creator=self.user1)
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f"/api/tasks/{task.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    def test_delete_other_user_task_forbidden(self):
        task = Task.objects.create(title="Task", creator=self.user1)
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f"/api/tasks/{task.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_complete_task_by_creator(self):
        task = Task.objects.create(title="Task", creator=self.user1)
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(f"/api/tasks/{task.id}/complete/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertTrue(task.is_completed)

    def test_complete_task_by_assignee(self):
        task = Task.objects.create(
            title="Task", creator=self.user1, assignee=self.user2
        )
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f"/api/tasks/{task.id}/complete/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertTrue(task.is_completed)

    def test_complete_task_by_other_user_forbidden(self):
        task = Task.objects.create(title="Task", creator=self.user1)
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f"/api/tasks/{task.id}/complete/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assign_task_by_creator(self):
        task = Task.objects.create(title="Task", creator=self.user1)
        self.client.force_authenticate(user=self.user1)
        data = {"assignee_id": self.user2.id}
        response = self.client.post(f"/api/tasks/{task.id}/assign/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.assignee, self.user2)

    def test_assign_task_by_other_user_forbidden(self):
        task = Task.objects.create(title="Task", creator=self.user1)
        self.client.force_authenticate(user=self.user2)
        data = {"assignee_id": self.user2.id}
        response = self.client.post(f"/api/tasks/{task.id}/assign/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assign_nonexistent_user(self):
        task = Task.objects.create(title="Task", creator=self.user1)
        self.client.force_authenticate(user=self.user1)
        data = {"assignee_id": 9999}
        response = self.client.post(f"/api/tasks/{task.id}/assign/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CommentAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username="user1", password="pass123")
        cls.user2 = User.objects.create_user(username="user2", password="pass123")
        cls.task = Task.objects.create(title="Task", creator=cls.user1)

    def test_create_comment(self):
        self.client.force_authenticate(user=self.user1)
        data = {"task": self.task.id, "text": "Great task!"}
        response = self.client.post("/api/comments/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.author, self.user1)
        self.assertEqual(comment.text, "Great task!")

    def test_list_comments_for_task(self):
        Comment.objects.create(task=self.task, author=self.user1, text="Comment 1")
        Comment.objects.create(task=self.task, author=self.user2, text="Comment 2")
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f"/api/comments/?task={self.task.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_delete_own_comment(self):
        comment = Comment.objects.create(
            task=self.task, author=self.user1, text="My comment"
        )
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f"/api/comments/{comment.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_delete_other_user_comment_forbidden(self):
        comment = Comment.objects.create(
            task=self.task, author=self.user1, text="Comment"
        )
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f"/api/comments/{comment.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AuthAPITest(APITestCase):
    def test_user_registration(self):
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "pass123",
        }
        response = self.client.post("/api/auth/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_jwt_token_obtain(self):
        user = User.objects.create_user(username="testuser", password="pass123")
        data = {"username": "testuser", "password": "pass123"}
        response = self.client.post("/api/auth/token/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_authenticated_request_with_token(self):
        user = User.objects.create_user(username="testuser", password="pass123")
        token_response = self.client.post(
            "/api/auth/token/", {"username": "testuser", "password": "pass123"}
        )
        token = token_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_request_forbidden(self):
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
