from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AdminProfile, TeacherProfile, StudentProfile, ParentProfile

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active', 'created_at']
    list_filter = ['role', 'is_staff', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Profile', {'fields': ('role', 'phone_number', 'date_of_birth', 'address', 'profile_picture', 'is_active_user')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role & Profile', {'fields': ('role', 'phone_number', 'date_of_birth', 'address')}),
    )

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'department', 'permissions_level']
    list_filter = ['permissions_level', 'department']
    search_fields = ['user__username', 'user__email', 'employee_id', 'department']
    readonly_fields = ['employee_id']

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'teacher_id', 'employee_id', 'department', 'experience_years', 'hire_date']
    list_filter = ['department', 'hire_date', 'experience_years']
    search_fields = ['user__username', 'user__email', 'teacher_id', 'employee_id', 'department']
    readonly_fields = ['teacher_id', 'employee_id']
    date_hierarchy = 'hire_date'

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'roll_number', 'grade', 'classroom', 'admission_date']
    list_filter = ['grade', 'classroom', 'admission_date']
    search_fields = ['user__username', 'user__email', 'student_id', 'roll_number', 'parent_guardian_name']
    readonly_fields = ['student_id']
    date_hierarchy = 'admission_date'

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'relationship', 'occupation', 'get_children_count']
    list_filter = ['relationship', 'occupation']
    search_fields = ['user__username', 'user__email', 'occupation', 'workplace']
    filter_horizontal = ['students']
    
    def get_children_count(self, obj):
        return obj.students.count()
    get_children_count.short_description = 'Number of Children'

admin.site.register(CustomUser, CustomUserAdmin)
