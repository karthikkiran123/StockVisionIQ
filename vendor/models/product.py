from django.db import models

class Product(models.Model):
    PRODUCT_TYPE = [
        (1, 'New'),
        (2, 'Used'),
        (3, 'Scrapyard'),
    ]
    name = models.CharField(max_length=255)
    price = models.FloatField()
    is_active = models.BooleanField(default=True)
    type = models.IntegerField(default=1, choices=PRODUCT_TYPE)
    views = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    reported = models.IntegerField(default=0)
    featured = models.BooleanField(default=False)
    discount = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products', blank=True, null=True)
    vendor = models.ForeignKey('vendor.Vendor', on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def final_price(self):
        return self.price - (self.price * self.discount / 100)
    
    def get_id_by_category(category):
        for id, list_category in Product.PRODUCT_TYPE:
            if list_category.lower() == category:
                return id
        return None