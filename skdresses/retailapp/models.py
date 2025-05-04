from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, unique=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    area = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    pin = models.CharField(max_length=10)
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    PAYMENT_FREQUENCY_CHOICES = [
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
    ]
    payment_frequency = models.CharField(max_length=10, choices=PAYMENT_FREQUENCY_CHOICES)

    def __str__(self):
        return self.user.get_full_name()

class DressPurchase(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    # item_name = models.CharField(max_length=255)
    # unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    # quantity = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    downpayment = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)

    @property
    def paid_amount(self):
        return self.downpayment + sum(p.amount_paid for p in self.payment_set.all())

    @property
    def due_amount(self):
        return self.total_amount - self.paid_amount

    def __str__(self):
        return f"{self.item_name} - {self.customer.name}"
    
class Payment(models.Model):
    purchase = models.ForeignKey('DressPurchase', on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=100, null=True, blank=True)
    payment_date = models.DateField(auto_now_add=True)
    payment_date_time = models.DateTimeField(auto_now_add=True, null=True)
    collected_by = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Payment of {self.amount_paid} on {self.payment_date}"

class ReturnOrExchange(models.Model):
    RETURN = 'return'
    EXCHANGE = 'exchange'
    REQUEST_TYPE_CHOICES = [
        (RETURN, 'Return'),
        (EXCHANGE, 'Exchange'),
    ]

    purchase = models.ForeignKey('DressPurchase', on_delete=models.CASCADE)
    request_type = models.CharField(max_length=10, choices=REQUEST_TYPE_CHOICES)
    condition_notes = models.TextField()
    request_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.request_type.title()} Request for {self.purchase.item_name}"
    

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(DressPurchase, related_name='items', on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.unit_price
    
class InventoryItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    hsn_sac_code = models.CharField(max_length=20, blank=True, null=True)
    actual_price = models.DecimalField(max_digits=10, decimal_places=2)
    markup_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name