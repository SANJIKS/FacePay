from django.db import models


class User(models.Model):
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    balance = models.FloatField(default=0)
    pin_code = models.CharField(max_length=4)
    email = models.EmailField(
        max_length=255, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    face_encoding = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    CHOICES = [
        ('error', 'Ошибка транзакции'),
        ('waiting_for_pin', 'Ожидание ввода пин-кода'),
        ('payment_confirmed', 'Оплата подтверждена')
    ]

    state = models.CharField(
        max_length=40, choices=CHOICES, default='waiting_for_scan')

    def __str__(self):
        return f"{self.user} - {self.amount} - {self.date}"
