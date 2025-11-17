from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Count, F, Sum
from django.utils import timezone


# Create your models here.
class TenantData(models.Model):
    name = models.CharField(max_length=15)
    contact = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=15)
    product_type = models.CharField(max_length=15, blank=True)
    expirable = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    def batch_count(self):
        return self.product_batch_set.count()
    batch_count.short_description = "Number of Batches"

    def total_quantity(self):
        return self.product_batch_set.aggregate(total=Sum('quantity'))['total'] or 0
    total_quantity.short_description = "Total Quantity"

    def total_cost_value(self):
        return self.product_batch_set.aggregate(total=Sum('total_cost_price'))['total'] or 0
    total_cost_value.short_description = "Total Cost Value"
    
    def total_selling_value(self):
        return self.product_batch_set.aggregate(total=Sum('total_selling_price'))['total'] or 0
    total_selling_value.short_description = "Total Selling Value"
    

class Product_Batch(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    batch_number = models.CharField(max_length=50, null=True)
    added_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True)
    quantity = models.PositiveIntegerField(default=0)
    selling_rate = models.DecimalField(max_digits=10,decimal_places=2, default=0)
    cost_rate = models.DecimalField(max_digits=10,decimal_places=2, default=0)
    total_selling_price = models.DecimalField(max_digits=12,decimal_places=2, blank=True, default=0)
    total_cost_price = models.DecimalField(max_digits=12,decimal_places=2, blank=True, default=0)
    
    
    def save(self, *args, **kwargs):
        self.total_selling_price = self.quantity * self.selling_rate
        self.total_cost_price = self.quantity * self.cost_rate

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.name} - {self.batch_number}"
    
    class Meta:
        verbose_name = "Product Batch"
        verbose_name_plural = "Product Batches"
        ordering = ['-added_date']
        


class PurchaseItem(models.Model):
    purchase = models.ForeignKey('Purchase', on_delete=models.CASCADE, related_name='items')
    product_batch = models.ForeignKey('Product_Batch', on_delete=models.PROTECT, related_name='purchase_items')
    product_name = models.CharField(max_length=100)
    batch_number = models.CharField(max_length=50, null=True)
    cost_rate = models.DecimalField(max_digits=10,decimal_places=2, default=0)
    selling_rate = models.DecimalField(max_digits=10,decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total_selling_price = models.DecimalField(max_digits=12,decimal_places=2, blank=True, default=0)
    total_cost_price = models.DecimalField(max_digits=12,decimal_places=2, blank=True, default=0)

    def save(self, *args, **kwargs):
        self.total_selling_price = self.quantity * self.selling_rate
        self.total_cost_price = self.quantity * self.cost_rate

        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Purchase Item"
        verbose_name_plural = "Purchase Items"

    def __str__(self):
        return f"{self.product_name} – {self.batch_number} × {self.quantity}"


class Purchase(models.Model):
    bill_no = models.CharField(max_length=30, unique=True, blank=True)
    supplier_name = models.CharField(max_length=100)
    purchase_date = models.DateTimeField(null=True, blank=True)   
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)  
    notes = models.TextField(blank=True)                        
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.bill_no} – {self.supplier_name}"

    def save(self, *args, **kwargs):
        if not self.bill_no:
            last = Purchase.objects.order_by('-id').first()
            seq = (last.id + 1) if last else 1
            self.bill_no = f"PUR-{seq:06d}"
        super().save(*args, **kwargs)


class Sale(models.Model):
    bill_no = models.CharField(max_length=30, unique=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)  
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    customer_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)    

    class Meta:
        verbose_name = "Sale"
        verbose_name_plural = "Sales"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.bill_no} – {self.customer_name}"


    def save(self, *args, **kwargs):
        if not self.bill_no:
            last = Sale.objects.order_by('-id').first()
            seq = (last.id + 1) if last else 1
            self.bill_no = f"SAL-{seq:06d}"
        super().save(*args, **kwargs)       
    
    
class SalesItem(models.Model):
    sale = models.ForeignKey(Sale,on_delete=models.CASCADE,related_name='items' )
    product_batch = models.ForeignKey('Product_Batch', on_delete=models.PROTECT, related_name='sales_items')
    product_name = models.CharField(max_length=100)     
    batch_number = models.CharField(max_length=50, null=True)      
    cost_rate = models.DecimalField(max_digits=10,decimal_places=2, default=0)
    selling_rate = models.DecimalField(max_digits=10,decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total_selling_price = models.DecimalField(max_digits=12,decimal_places=2, blank=True, default=0)
    total_cost_price = models.DecimalField(max_digits=12,decimal_places=2, blank=True, default=0)

    def save(self, *args, **kwargs):
        self.total_selling_price = self.quantity * self.selling_rate
        self.total_cost_price = self.quantity * self.cost_rate

        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Sales Item"
        verbose_name_plural = "Sales Items"
        ordering = ['-sale__created_at']

    def __str__(self):
        return f"{self.product_name} – {self.batch_number} × {self.quantity}"