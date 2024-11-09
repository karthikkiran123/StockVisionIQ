from django.db import models

class Order(models.Model):
    products = models.ManyToManyField('vendor.Product', related_name='orders')
    order_number = models.CharField(max_length=255, default=None, null=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    total_amount = models.FloatField(default=0.0)
    shipping_address = models.TextField(default=None, null=True)
    payment_mode = models.CharField(max_length=255, default=None, null=True)
    payment_id = models.CharField(max_length=255, null=True)
    is_paid = models.BooleanField(default=False)
    billing_address = models.TextField(default=None, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
    
    def get_status_display(self):
        if self.is_completed:
            return 'Completed'
        elif self.is_paid:
            return 'Paid'
        else:
            return 'Pending'