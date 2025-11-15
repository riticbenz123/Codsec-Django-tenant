from django.db import models


# Create your models here.
class TenantData(models.Model):
    name = models.CharField(max_length=15)
    contact = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=15)
    product_type = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return self.name
    

class Product_Batch(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    batch_number = models.CharField(max_length=50,unique=True)
    added_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    quantity = models.PositiveIntegerField(default=0)
    rate = models.DecimalField(max_digits=10,decimal_places=2)
    total_price = models.DecimalField(max_digits=12,decimal_places=2, blank=True)
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.rate
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.name} - {self.batch_number}"
    
    class Meta:
        verbose_name = "Product Batch"
        verbose_name_plural = "Product Batches"
        ordering = ['-added_date']