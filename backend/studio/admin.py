from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone

from .models import Appointment, Barber, Break, DayOff, Service, User, WorkingHours


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["email"]
    list_display = ["email", "first_name", "is_staff", "is_active"]
    search_fields = ["email", "first_name"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Activity", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "first_name", "password1", "password2")}),)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["name", "duration_minutes", "base_price", "senior_price", "top_price", "training_for", "is_active", "display_order"]
    list_filter = ["is_active"]
    search_fields = ["name"]


class WorkingHoursInline(admin.TabularInline):
    model = WorkingHours
    extra = 0


class BreakInline(admin.TabularInline):
    model = Break
    extra = 0


class DayOffInline(admin.TabularInline):
    model = DayOff
    extra = 0


@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ["name", "level", "role", "supervisor", "is_active"]
    list_filter = ["level", "is_active"]
    filter_horizontal = ["services"]
    inlines = [WorkingHoursInline, BreakInline, DayOffInline]


@admin.register(WorkingHours, Break, DayOff)
class ScheduleAdmin(admin.ModelAdmin):
    list_filter = ["barber"]


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ["id", "contact_name", "service_name", "barber", "barber_level", "supervisor", "price", "starts_at", "ends_at", "status"]
    list_filter = ["status", "barber", "service", "starts_at"]
    search_fields = ["contact_name", "contact_email", "customer__email"]
    date_hierarchy = "starts_at"
    list_select_related = ["barber", "customer", "service"]
    readonly_fields = [field.name for field in Appointment._meta.fields]
    actions = ["cancel_selected"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Cancel selected future appointments", permissions=["change"])
    def cancel_selected(self, request, queryset):
        count = queryset.filter(status=Appointment.Status.CONFIRMED, starts_at__gt=timezone.now()).update(status=Appointment.Status.CANCELLED, cancelled_at=timezone.now())
        self.message_user(request, f"Cancelled {count} appointment(s).")
