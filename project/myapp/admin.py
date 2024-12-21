from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Event)

class EventAdmin(admin.ModelAdmin):
    list_display = ('event_username','event_name', 'event_date', 'event_location', 'event_category')
    search_fields = ('event_name')
    
    
admin.site.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name')
    
admin.site.register(EventApplication)
class EventApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'status', 'event_id')
    
admin.site.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_type', 'location', 'is_available')
    
admin.site.register(RoomBooking)
class RoomBookingAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'contact_email', 'number_of_attendees', 'booking_date')
    

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'verification_token', 'is_email_verified')
    def username(self, obj):
        return obj.user.username
    search_fields = ('user__username', 'user__email')

admin.site.register(UserProfile, UserProfileAdmin)

