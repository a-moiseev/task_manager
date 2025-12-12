from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from tasks.models import Comment, Task
from tasks.permissions import (
    IsAuthorOrAdmin,
    IsCreatorOrAdmin,
    IsCreatorOrAssigneeOrAdmin,
)
from tasks.serializers import (
    AssignSerializer,
    CommentSerializer,
    TaskCreateUpdateSerializer,
    TaskDetailSerializer,
    TaskListSerializer,
    UserRegistrationSerializer,
)

User = get_user_model()


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return TaskListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return TaskCreateUpdateSerializer
        return TaskDetailSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsCreatorOrAdmin()]
        return super().get_permissions()

    @action(
        detail=True, methods=["post"], permission_classes=[IsCreatorOrAssigneeOrAdmin]
    )
    def complete(self, request, pk=None):
        task = self.get_object()
        task.is_completed = True
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsCreatorOrAdmin])
    def assign(self, request, pk=None):
        task = self.get_object()
        serializer = AssignSerializer(data=request.data)
        if serializer.is_valid():
            task.assignee = User.objects.get(
                id=serializer.validated_data["assignee_id"]
            )
            task.save()
            return Response(TaskDetailSerializer(task).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAuthorOrAdmin()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        task_id = self.request.query_params.get("task")
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        return queryset


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
