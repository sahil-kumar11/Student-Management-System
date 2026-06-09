from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('add-class/', views.add_class, name='add_class'),
    path('add-student/', views.add_student, name='add_student'),
    path('students/', views.view_students, name='view_students'),
    path('delete-student/<int:id>/', views.delete_student, name='delete_student'),
    path('edit-student/<int:id>/', views.edit_student, name='edit_student'),
    path('search-student/',views.search_student,name='search_student'),
    path('add-notice/',views.add_notice,name='add_notice'),
    path('view-notices/',views.view_notices,name='view_notices'),
    path('delete-notice/<int:id>/',views.delete_notice,name='delete_notice'),
    path('student-report-pdf/',views.student_report_pdf,name='student_report_pdf'),
    path('export-excel/',views.export_students_excel,name='export_excel'),
    path('mark-attendance/',views.mark_attendance,name='mark_attendance'),
    path('get-students-by-class/', views.get_students_by_class, name='get_students_by_class'),
    path('save-attendance/', views.save_attendance, name='save_attendance'),
    path('attendance-list/',views.attendance_list,name='attendance_list'),
    path('add-teacher/',views.add_teacher,name='add_teacher'),
    path('view-teachers/',views.view_teachers,name='view_teachers'),
    path('delete-teacher/<int:id>/', views.delete_teacher, name='delete_teacher'),
    path('teacher-dashboard/',views.teacher_dashboard,name='teacher_dashboard'),
    path('change-password/',auth_views.PasswordChangeView.as_view(template_name='change_password.html'),name='change_password'),
]