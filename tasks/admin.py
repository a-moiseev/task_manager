from django.contrib import admin

from tasks.models import Comment, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "creator", "assignee", "is_completed", "created_at"]
    list_filter = ["is_completed", "created_at"]
    search_fields = ["title", "description"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["task", "author", "text", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["text"]
    readonly_fields = ["created_at"]
