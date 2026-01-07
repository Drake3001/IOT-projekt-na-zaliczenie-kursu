from django.db import models
from django.utils import timezone

class RfidCard(models.Model):
    uid = models.CharField(max_length=50, unique=True, verbose_name="UID Karty")
    expiry_date = models.DateTimeField(verbose_name="Ważna do")
    valid = models.BooleanField(default=True)

    def czy_wazna(self):
        return self.valid and self.exipiry_date > timezone.now()

    def __str__(self):
        return f"{self.uid}, {self.exipiry_date}, {self.valid}"

class EntryLog(models.Model):
    class AccessStatus(models.TextChoices):
        GRANTED = 'GRANTED', 'Access Granted'
        DENIED_EXPIRED = 'DENIED_EXPIRED', 'Denied (Expired)'
        DENIED_UNKNOWN = 'DENIED_UNKNOWN', 'Denied (Unknown Card)'
        DENIED_INACTIVE = 'DENIED_INACTIVE', 'Denied (Card Inactive)'

    card = models.ForeignKey(RfidCard, on_delete=models.SET_NULL, null=True, blank=True)
    uid_raw = models.CharField(max_length=50, verbose_name="Odczytany UID")
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=AccessStatus.choices,
        default=AccessStatus.DENIED_UNKNOWN
    )

    def __str__(self):
        return f"{self.uid_raw} - {self.timestamp} - {self.status}"