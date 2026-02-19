from django.db import models
import uuid

class User(models.Model):
    telegram_id = models.BigIntegerField(primary_key=True, verbose_name="Telegram ID")
    username = models.CharField(max_length=255, null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    tier = models.CharField(max_length=50, default="free", choices=[
        ("free", "Free"),
        ("pro", "Pro"),
        ("agency", "Agency"),
    ])
    subscription_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.telegram_id})"

class Audit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="audits")
    instagram_url = models.CharField(max_length=500, null=True, blank=True)
    telegram_url = models.CharField(max_length=500, null=True, blank=True)
    audit_type = models.CharField(max_length=50, default="standard")
    status = models.CharField(max_length=50, default="pending")
    collected_data_json = models.JSONField(null=True, blank=True)
    report_json = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Audit {self.id} for {self.user}"
