from django.db import models


class DownloadLocationPayment(models.Model):
    """
    Model to store information about successful payments made
    for purchasing of additional records for downloading production
    locations data.
    """

    user = models.ForeignKey(
        'User',
        null=False,
        on_delete=models.CASCADE,
        related_name='download_location_payments',
        help_text='The user who made the payment.',
    )
    stripe_session_id = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        unique=True,
        help_text='The unique identifier for the Stripe checkout session.',
    )
    payment_id = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        unique=True,
        help_text='The unique identifier for the payment, if available.',
    )
    amount_subtotal = models.IntegerField(
        null=False,
        blank=False,
        help_text='The subtotal amount of the payment, stored in cents.',
    )
    amount_total = models.IntegerField(
        null=False,
        blank=False,
        help_text='The total amount of the payment, stored in cents.',
    )
    discounts = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            'List of discount objects applied to the payment, '
            'each containing coupon and promotion_code.'
        ),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    def __str__(self):
        return f"Payment {self.payment_id} by {self.user}"
