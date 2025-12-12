from django.contrib.auth import get_user_model
from rest_framework import serializers

from tasks.models import Comment, Task

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "task", "author", "text", "created_at"]
        read_only_fields = ["author", "created_at"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    assignee = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "creator",
            "assignee",
            "is_completed",
            "created_at",
        ]


class TaskDetailSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    assignee = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "creator",
            "assignee",
            "is_completed",
            "created_at",
            "updated_at",
            "comments",
        ]


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["title", "description"]

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)


class AssignSerializer(serializers.Serializer):
    assignee_id = serializers.IntegerField()

    def validate_assignee_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User does not exist")
        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user
