from django.db import models
from datetime import datetime

# Create your models here.
from django.db import models


class ClassRoom(models.Model):
    name = models.CharField(max_length=100)
    section = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=10)
    dob = models.DateField()
    address = models.TextField()
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profiles/',null=True,blank=True)

    def __str__(self):
        return self.name


class Notice(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
from django.utils import timezone

class Attendance(models.Model):

    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10,choices=[('Present', 'Present'),('Absent', 'Absent')])

    def __str__(self):
        return f"{self.student.name} - {self.date}"
    
class Teacher(models.Model):

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    classroom = models.ForeignKey(ClassRoom,on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
# Fee Structure

class FeeStructure(models.Model):
    """Fee structure for each class"""
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=20)
    tuition_fee = models.IntegerField(default=0)  # Changed from Decimal to Integer
    exam_fee = models.IntegerField(default=0)
    library_fee = models.IntegerField(default=0)
    transport_fee = models.IntegerField(default=0)
    hostel_fee = models.IntegerField(default=0)
    other_fees = models.IntegerField(default=0)
    late_fee_penalty = models.IntegerField(default=100)
    
    def total_fee(self):
        return self.tuition_fee + self.exam_fee + self.library_fee + self.transport_fee + self.hostel_fee + self.other_fees
    
    def __str__(self):
        return f"{self.classroom.name} - {self.academic_year}"

class FeePayment(models.Model):
    """Individual student fee payments"""
    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Partial', 'Partial'),
        ('Paid', 'Paid'),
        ('Overdue', 'Overdue'),
    ]
    
    PAYMENT_METHODS = [
        ('Cash', 'Cash'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Credit Card', 'Credit Card'),
        ('Online', 'Online'),
        ('Cheque', 'Cheque'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_payments')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    amount_paid = models.IntegerField(default=0)  # Changed from Decimal to Integer
    due_amount = models.IntegerField(default=0)
    payment_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='Cash')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    receipt_number = models.CharField(max_length=50, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending')
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            from datetime import datetime
            self.receipt_number = f"RCP-{datetime.now().strftime('%Y%m%d')}-{self.student.id}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.name} - ₹{self.amount_paid} - {self.payment_date}"

class FeeInstallment(models.Model):
    """Installment schedule for fees"""
    INSTALLMENT_TYPES = [
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
        ('Half-Yearly', 'Half-Yearly'),
        ('Yearly', 'Yearly'),
    ]
    
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    installment_type = models.CharField(max_length=20, choices=INSTALLMENT_TYPES)
    installment_number = models.IntegerField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.fee_structure.classroom.name} - {self.installment_type} {self.installment_number}"
    
class PaymentRequest(models.Model):
    """Online payment requests from students"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.IntegerField()
    order_id = models.CharField(max_length=100, unique=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    signature = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, default='Pending')  # Pending, Success, Failed
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.name} - ₹{self.amount} - {self.status}"