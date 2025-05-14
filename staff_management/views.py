from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Staff, WeekendGroup, WorkShift, Unit

# View function to handle adding a new staff member
def add_staff(request):
    '''View function to handle adding a new staff member.
    This function processes the form submission, validates the data,'''
  
    # Check if the form was submitted via POST
    if request.method == 'POST':

        # Extract individual form values from POST data
        staff_name = request.POST.get('staff_name')
        gender = request.POST.get('gender')
        weekend_groups = request.POST.getlist('weekend_groups')  # Multiple selection (ManyToMany)
        work_shifts = request.POST.getlist('work_shifts')        # Multiple selection (ManyToMany)
        unit_restrictions = request.POST.getlist('unit_restrictions')  # Multiple selection (ManyToMany)
        assigned_unit = request.POST.getlist('assigned_unit')        # Multiple selection (ManyToMany)
        contract_type = request.POST.get('contract_type')
        status = request.POST.get('status')

        # Create a new Staff instance — ManyToMany relationships must be added after save
        staff = Staff(
            staff_name=staff_name,
            gender=gender,
            contract_type=contract_type,
            status=status
        )

        # Save the basic staff data to generate a primary key
        staff.save()

        # Set ManyToMany relationships now that staff has a primary key
        staff.weekend_groups.set(weekend_groups)
        staff.work_shifts.set(work_shifts)
        staff.unit_restrictions.set(unit_restrictions)
        staff.assigned_unit.set(assigned_unit)

        # Redirect to a page named 'staff_management' after successful creation
        return redirect('staff_management')
    
    # Context for form dropdowns
    context = {
        'weekend_groups': WeekendGroup.objects.all(),
        'work_shifts': WorkShift.objects.all(),
        'units': Unit.objects.all(),
    }
    
    # If request method is GET, render the empty staff creation form
    return render(request, 'add_staff.html', context)