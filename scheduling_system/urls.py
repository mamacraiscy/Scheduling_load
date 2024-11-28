from django.urls import path
from .views import (
    home,
    create_teaching_load,
    search_instructors,
    teaching_load,
    instructor_details, 
    room_utilization,
    search_rooms,
    room_details,
    schedule_room
)

urlpatterns = [
    path('', home, name='index'),
    path('create_teaching_load/', create_teaching_load, name='create_teaching_load'),
    path('teaching_load/',teaching_load,name='teaching_load'),
    path('search_instructors/', search_instructors, name='search_instructors'),
    path('teaching_load/',teaching_load,name='teaching_load'),
    path('details/', instructor_details, name='instructor_details'),
    path('room-utilization/',room_utilization, name='room_utilization'),
    path('search_rooms/', search_rooms, name='search_rooms'),
    path('room_details/', room_details, name='room_details'),
    path('schedule-room/',schedule_room, name='schedule_room'),
]
