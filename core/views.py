from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import*
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.core.paginator import Paginator
from openpyxl import Workbook
from django.core.mail import send_mail
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum, Q
from decimal import Decimal




def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect('admin_dashboard')

            elif user.is_staff:
                return redirect('teacher_dashboard')

            else:
                return redirect('student_dashboard')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):

    total_students = Student.objects.count()
    total_classes = ClassRoom.objects.count()
    total_notices = Notice.objects.count()

    context = {
        'total_students': total_students,
        'total_classes': total_classes,
        'total_notices': total_notices,
    }

    return render(request, 'admin_dashboard.html', context)

def add_class(request):

    if request.method == "POST":

        name = request.POST.get("name")
        section = request.POST.get("section")

        ClassRoom.objects.create(
            name=name,
            section=section
        )

        return redirect('admin_dashboard')

    return render(request, 'add_class.html')

def edit_student(request, id):
    # Get the student data
    student = get_object_or_404(Student, id=id)
    classes = ClassRoom.objects.all()
    
    if request.method == "POST":
        # Update logic
        student.student_id = request.POST.get("student_id")
        student.name = request.POST.get("name")
        student.email = request.POST.get("email")
        student.phone = request.POST.get("phone")
        student.gender = request.POST.get("gender")
        student.dob = request.POST.get("dob")
        student.address = request.POST.get("address")
        student.classroom = ClassRoom.objects.get(id=request.POST.get("classroom"))
        student.save()
        return redirect('view_students')
    
    # Pass student data to template
    return render(request, 'add_student.html', {
        'classes': classes,
        'student': student,  # Ye data template mein jayega
        'is_edit': True
    })

def add_student(request):
    classes = ClassRoom.objects.all()
    
    if request.method == "POST":
        # Add new student logic
        student = Student.objects.create(
            student_id=request.POST.get("student_id"),
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            gender=request.POST.get("gender"),
            dob=request.POST.get("dob"),
            address=request.POST.get("address"),
            classroom=ClassRoom.objects.get(id=request.POST.get("classroom"))
        )
        return redirect('view_students')
    
    return render(request, 'add_student.html', {
        'classes': classes,
        'student': None,  # No data for add mode
        'is_edit': False
    })
def delete_student(request, id):
    student = Student.objects.get(id=id)
    student.delete()
    return redirect('view_students')

def search_student(request):
    query = request.GET.get('q')
    class_filter = request.GET.get('class_filter')
    gender_filter = request.GET.get('gender_filter')
    
    students = Student.objects.all()
    
    if query:
        students = students.filter(
            Q(name__icontains=query) |
            Q(student_id__icontains=query) |
            Q(email__icontains=query)
        )
    
    if class_filter:
        students = students.filter(classroom_id=class_filter)
    
    if gender_filter:
        students = students.filter(gender=gender_filter)
    
    classes = ClassRoom.objects.all()
    
    return render(request, 'search_student.html', {
        'students': students,
        'classes': classes
    })

def add_notice(request):

    if request.method == "POST":

        title = request.POST.get("title")
        message = request.POST.get("message")

        Notice.objects.create(
            title=title,
            message=message
        )

        return redirect('view_notices')

    return render(request, 'add_notice.html')

def view_notices(request):

    notices = Notice.objects.all().order_by('-id')

    return render(
        request,
        'view_notices.html',
        {'notices': notices}
    )

def delete_notice(request, id):

    notice = Notice.objects.get(id=id)

    notice.delete()

    return redirect('view_notices')

def student_report_pdf(request):

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = (
        'attachment; filename="students_report.pdf"'
    )

    p = canvas.Canvas(response)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 800, "Student Report")

    y = 760

    students = Student.objects.all()

    for student in students:

        text = (
            f"{student.student_id} | "
            f"{student.name} | "
            f"{student.email}"
        )

        p.drawString(50, y, text)

        y -= 20

        if y < 50:
            p.showPage()
            y = 800

    p.save()

    return response

def view_students(request):

    student_list = Student.objects.all()

    paginator = Paginator(
        student_list,
        10
    )

    page_number = request.GET.get('page')

    students = paginator.get_page(page_number)

    return render(
        request,
        'view_students.html',
        {'students': students}
    )

def export_students_excel(request):

    wb = Workbook()

    ws = wb.active

    ws.append([
        'Student ID',
        'Name',
        'Email'
    ])

    for s in Student.objects.all():

        ws.append([
            s.student_id,
            s.name,
            s.email
        ])

    response = HttpResponse(
        content_type=
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename=students.xlsx'

    wb.save(response)

    return response

def get_students_by_class(request):
    class_id = request.GET.get('class_id')
    if class_id:
        students = Student.objects.filter(classroom_id=class_id).values('id', 'student_id', 'name')
        return JsonResponse({'students': list(students)})
    return JsonResponse({'students': []})


@csrf_exempt
def save_attendance(request):
    if request.method == 'POST':
        class_id = request.POST.get('classroom')
        date = request.POST.get('date')
        
        if class_id and date:
            students = Student.objects.filter(classroom_id=class_id)
            
            for student in students:
                status = request.POST.get(f'status_{student.id}')
                if status:
                    existing = Attendance.objects.filter(
                        student=student,
                        date=date
                    ).first()
                    
                    if existing:
                        existing.status = status
                        existing.save()
                    else:
                        Attendance.objects.create(
                            student=student,
                            date=date,
                            status=status
                        )
            
            # Redirect to attendance list page
            return redirect('attendance_list')
    
    return redirect('mark_attendance')


@login_required
def mark_attendance(request):
    classrooms = ClassRoom.objects.all()
    return render(request, 'mark_attendance.html', {'classrooms': classrooms})

def attendance_list(request):
    classrooms = ClassRoom.objects.all()
    selected_class = request.GET.get('class_id')
    selected_date = request.GET.get('date')
    
    attendance_records = Attendance.objects.all().order_by('-date')
    
    if selected_class:
        attendance_records = attendance_records.filter(student__classroom_id=selected_class)
    
    if selected_date:
        attendance_records = attendance_records.filter(date=selected_date)

    return render(request, 'attendance_list.html', {
        'classrooms': classrooms,
        'attendance': attendance_records,
        'selected_class': selected_class,
        'selected_date': selected_date
    })

def add_teacher(request):

    classes = ClassRoom.objects.all()

    if request.method == "POST":

        Teacher.objects.create(

            name=request.POST.get("name"),
            email=request.POST.get("email"),
            subject=request.POST.get("subject"),

            classroom=ClassRoom.objects.get(
                id=request.POST.get("classroom")
            )

        )

        return redirect('view_teachers')

    return render(
        request,
        'add_teacher.html',
        {'classes': classes}
    )

def view_teachers(request):

    teachers = Teacher.objects.all()

    return render(
        request,
        'view_teachers.html',
        {'teachers': teachers}
    )

@login_required
@user_passes_test(lambda u: u.is_staff)
def teacher_dashboard(request):
    # Get teacher record for logged-in user
    try:
        teacher = Teacher.objects.get(email=request.user.email)
    except Teacher.DoesNotExist:
        # If teacher not found by email, try to get first teacher or show error
        teacher = Teacher.objects.first()
        if not teacher:
            return render(request, 'teacher_dashboard.html', {'error': 'No teacher profile found'})
    
    # Get all students in teacher's class
    students = Student.objects.filter(classroom=teacher.classroom)
    total_students = students.count()
    
    # Calculate today's attendance percentage
    today = timezone.now().date()
    today_attendance_records = Attendance.objects.filter(
        student__classroom=teacher.classroom,
        date=today
    )
    today_present = today_attendance_records.filter(status='Present').count()
    today_attendance = int((today_present / total_students * 100)) if total_students > 0 else 0
    
    # Calculate attendance percentage for each student
    for student in students:
        total_days = Attendance.objects.filter(student=student).count()
        present_days = Attendance.objects.filter(student=student, status='Present').count()
        student.attendance_percentage = int((present_days / total_days * 100)) if total_days > 0 else 0
    
    # Get latest notice
    latest_notice = Notice.objects.first()
    
    context = {
        'teacher': teacher,
        'students': students,
        'total_students': total_students,
        'today_attendance': today_attendance,
        'latest_notice': latest_notice,
    }
    
    return render(request, 'teacher_dashboard.html', context)

@login_required
def student_dashboard(request):

    if request.user.is_superuser or request.user.is_staff:
        return HttpResponse("Access Denied")

    student = Student.objects.get(
        email=request.user.username
    )

    attendance = Attendance.objects.filter(student=student)
    notices = Notice.objects.all()

    return render(
        request,
        'student_dashboard.html',
        {
            'student': student,
            'attendance': attendance,
            'notices': notices
        }
    )

def delete_teacher(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    teacher.delete()
    messages.success(request, 'Teacher deleted successfully!')
    return redirect('view_teachers')



