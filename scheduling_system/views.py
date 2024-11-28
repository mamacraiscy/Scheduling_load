from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .models import InstructorData, InstructorCourse, Program, Room,  RoomSchedule
from .forms import ProgramForm  # Ensure you have a form for Program

def home(request):
    return render(request, 'instructors_frontend/index.html')  # Original home page

# Create teaching load page
def create_teaching_load(request):
    return render(request, 'instructors_frontend/create_load.html')  # New page for teaching load

def teaching_load(request):
    return render(request,'instructors_frontend/teaching_load.html')

def search_instructors(request):
    if request.method == "GET":
        query = request.GET.get('q', '').strip()  # Get the search query
        filter_type = request.GET.get('filter', 'ALL')  # Get the filter type (ALL, regular, cos)

        # Debugging: Print query and filter
        print(f"Search Query: {query}, Filter: {filter_type}")

        # Start with all instructors
        instructors = InstructorData.objects.all()

        # Apply filtering logic based on employment type
        if filter_type == 'REGULAR':
            instructors = instructors.filter(employment_type='REGULAR')
        elif filter_type == 'COS':
            instructors = instructors.filter(employment_type='COS')

        # Apply query if present
        if query:
            # Split the query into parts (split by spaces)
            name_parts = query.split()

            # Dynamically build the query filters based on the parts
            filter_query = Q()

            for part in name_parts:
                filter_query |= Q(first_name__icontains=part) | Q(middle_initial__icontains=part) | Q(last_name__icontains=part)

            instructors = instructors.filter(filter_query)

        # Debugging: Print the number of instructors fetched
        print(f"Found {instructors.count()} instructors matching the query.")

        # Prepare the response for the search (as JSON for AJAX)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Prepare the list of instructor details to return
            data = [
                {
                    'name': f"{instructor.first_name} {instructor.middle_initial or ''} {instructor.last_name}".strip(),
                    'instructor_id': instructor.instructor_id,
                    'employment_type': instructor.employment_type,
                    'qualified_course': instructor.qualified_course,
                }
                for instructor in instructors
            ]



            return JsonResponse({'results': data})

        # For non-AJAX request, render the instructor list template
        return render(request, 'instructors_frontend/teaching_load.html', {
            'instructors': instructors,
            'filter': filter_type,  # Pass the employment type filter to the template
            'query': query,  # Pass the search query to the template
        })

@csrf_exempt
def instructor_details(request):
    instructor_id = request.GET.get('id')
    instructor = InstructorData.objects.get(instructor_id=instructor_id)

    # Prepare the instructor details to return as JSON
    data = {
        'instructor_id': instructor.instructor_id,
        'name': f"{instructor.first_name} {instructor.middle_initial or ''} {instructor.last_name}".strip(),
        'employment_type': instructor.employment_type,
        'qualified_courses': instructor.qualified_course,
    }

    return JsonResponse(data)


# List instructor courses
def instructor_course_list(request):
    courses = InstructorCourse.objects.all()
    return render(request, 'teaching_load.html', {'courses': courses})

# Add a program
def add_program(request):
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')  # Redirect to the home page or a specific list
    else:
        form = ProgramForm()
    return render(request, 'teaching_load.html', {'form': form})

# Edit a program
def edit_program(request, pk):
    program = get_object_or_404(Program, pk=pk)
    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ProgramForm(instance=program)
    return render(request, 'teaching_load.html', {'form': form})

def room_utilization(request):
    return render(request, 'instructors_frontend/room_util.html')  # Update path to match your template location

def search_rooms(request):
    query = request.GET.get('q', '')
    rooms = Room.objects.filter(room_number__icontains=query)[:10]  # Limit to 10 rooms
    rooms_data = [{"room_id": room.room_id, "room_number": room.room_number, "room_type": room.room_type} for room in rooms]
    return JsonResponse({'rooms': rooms_data})

def room_details(request):
    room_id = request.GET.get('room_id')
    try:
        room = Room.objects.get(room_id=room_id)
        data = {
            'room': {
                'room_number': room.room_number,
                'room_type': room.room_type,
                'building_name': room.building.building_name,
                'campus_name': room.campus.campus_name,
            }
        }
        return JsonResponse(data)
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)
    
def schedule_room(request):
    if request.method == 'POST':
        room_id = request.POST.get('room')  # Room ID from the hidden input field
        day = request.POST.get('day')
        start_time = request.POST.get('start-time')
        end_time = request.POST.get('end-time')

        # Error handling for room retrieval
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            # If the room doesn't exist, handle this gracefully (perhaps show an error message)
            return render(request, 'room_util.html', {'error': 'Room not found'})

        # Save the schedule to the database
        room_schedule = RoomSchedule(
            room=room,
            day=day,
            start_time=start_time,
            end_time=end_time,
        )

        try:
            room_schedule.save()
        except Exception as e:
            # Handle unexpected errors while saving
            return render(request, 'room_util.html', {'error': f'Error saving schedule: {e}'})

        # Redirect after saving
        return redirect('schedule_room')  # Redirect to the schedule page or wherever needed

    return render(request, 'room_util.html')  # Return the schedule page
