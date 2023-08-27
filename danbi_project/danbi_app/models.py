from django.db import models


# Create your models here.
class User(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=16)
    pwd = models.CharField(max_length=16)
    team = models.CharField(max_length=16)


class Task(models.Model):
    task_id = models.BigAutoField(primary_key=True)
    create_user = models.BigIntegerField()
    team = models.CharField(max_length=16, db_index=True)
    title = models.CharField(max_length=32)
    content = models.TextField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    completed_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['team']),
        ]


class SubTask(models.Model):
    subtask_id = models.BigAutoField(primary_key=True)
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE, db_column='task_id')
    team = models.CharField(max_length=16, db_index=True)
    is_complete = models.BooleanField(default=False)
    completed_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['team']),
        ]


# CREATE TABLE danbi_app_user (
#     user_id BIGINT AUTO_INCREMENT PRIMARY KEY,
#     username VARCHAR(16),
#     pwd VARCHAR(16),
#     team VARCHAR(16)
# );
# CREATE TABLE danbi_app_task (
#     task_id BIGINT AUTO_INCREMENT PRIMARY KEY,
#     create_user BIGINT,
#     team VARCHAR(16),
#     title VARCHAR(32),
#     content LONGTEXT,
#     is_complete BOOLEAN DEFAULT FALSE,
#     completed_date DATETIME,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
# );
# CREATE TABLE danbi_app_subtask (
#     subtask_id BIGINT AUTO_INCREMENT PRIMARY KEY,
#     task_id BIGINT,
#     team VARCHAR(16),
#     is_complete BOOLEAN DEFAULT FALSE,
#     completed_date DATETIME,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#     FOREIGN KEY (task_id) REFERENCES danbi_app_task(task_id) ON DELETE CASCADE
# );