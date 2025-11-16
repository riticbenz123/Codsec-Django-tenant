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
    batch_number = models.CharField(max_length=50,unique=True)
    added_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
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
        


class Purchase(models.Model):
    bill_no = models.CharField(max_length=30, unique=True, blank=True)
    product_batch = models.ForeignKey(
        'Product_Batch', on_delete=models.PROTECT, related_name='purchases'
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    cost_price = models.DecimalField(default=0,
        max_digits=10, decimal_places=2,
        help_text="Cost price per unit at the time of purchase"
    )
    supplier_name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Purchase"
        verbose_name_plural = "Purchases"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.bill_no} – {self.product_batch} ({self.quantity})"

    def save(self, *args, **kwargs):
        if not self.bill_no:
            last = Purchase.objects.order_by('-id').first()
            seq = (last.id + 1) if last else 1
            self.bill_no = f"PUR-{seq:06d}"
        super().save(*args, **kwargs)
        if self.pk is not None:PurchaseItem.objects.create(purchase=self,product_name=self.product_batch.product.name,batch_number=self.product_batch.batch_number,quantity=self.quantity)


class Sale(models.Model):
    bill_no = models.CharField(max_length=30, unique=True, blank=True)
    product_batch = models.ForeignKey(
        'Product_Batch', on_delete=models.PROTECT, related_name='sales'
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    selling_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Selling price per unit at the time of sale"
    )
    customer_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sale"
        verbose_name_plural = "Sales"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.bill_no} – {self.product_batch} ({self.quantity})"


    def save(self, *args, **kwargs):
        if not self.bill_no:
            last = Sale.objects.order_by('-id').first()
            seq = (last.id + 1) if last else 1
            self.bill_no = f"SAL-{seq:06d}"
            
        if self.pk is None:   
            # sold = self.product_batch.sales.aggregate(s=Sum('quantity'))['s'] or 0
            available = self.product_batch.quantity

            if self.quantity > available:
                from django.core.exceptions import ValidationError
                raise ValidationError(
                    f"Only {available} units available in batch {self.product_batch.batch_number}"
                )
            Product_Batch.objects.filter(pk=self.product_batch_id).update(quantity=F('quantity') - self.quantity)
            
        super().save(*args, **kwargs)
        if self.pk is not None:
            SalesItem.objects.create(sale=self,product_name=self.product_batch.product.name,batch_number=self.product_batch.batch_number,quantity=self.quantity)
        
    def clean(self):
        from django.core.exceptions import ValidationError
        available = self.product_batch.quantity - self.product_batch.sales.aggregate(
            sold=Sum('quantity')
        )['sold'] or 0
        if self.quantity > available:
            raise ValidationError(
                f"Only {available} units available in batch {self.product_batch.batch_number}"
            )
            
class PurchaseItem(models.Model):
    purchase = models.ForeignKey('Purchase',on_delete=models.CASCADE,related_name='items')
    product_name = models.CharField(max_length=100)   
    batch_number = models.CharField(max_length=50)   
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = "Purchase Item"
        verbose_name_plural = "Purchase Items"
        ordering = ['-purchase__created_at']

    def __str__(self):
        return f"{self.product_name} – {self.batch_number} × {self.quantity}"

class SalesItem(models.Model):
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items'         
    )
    product_name = models.CharField(max_length=100)     
    batch_number = models.CharField(max_length=50)      
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = "Sales Item"
        verbose_name_plural = "Sales Items"
        ordering = ['-sale__created_at']

    def __str__(self):
        return f"{self.product_name} – {self.batch_number} × {self.quantity}"