from django.db import models

class Payment(models.Model):
    vendor = models.ForeignKey('vendor.Vendor', on_delete=models.CASCADE, related_name='payments')
    order = models.ForeignKey('store.Order', on_delete=models.CASCADE, related_name='payments')
    amount = models.FloatField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name