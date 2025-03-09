from django.contrib import admin
from .models import User, Child, Bracelet, RecentPlace, LocationRequest, Notification , BatteryStatus , Location

admin.site.register(User)
admin.site.register(Child)
admin.site.register(Bracelet)
admin.site.register(RecentPlace)
admin.site.register(LocationRequest)
admin.site.register(Notification)
admin.site.register(BatteryStatus)
admin.site.register(Location)