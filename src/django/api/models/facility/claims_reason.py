from django.db import models


class ClaimsReason(models.Model):
    text = models.CharField(
        max_length=100,
        unique=True,
        help_text="The text description of the claim reason",
        verbose_name="reason text"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this claim reason is currently active and selectable"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['text']
        verbose_name = "Claims Reason"
        verbose_name_plural = "Claims Reasons"

    def __str__(self):
        return self.text