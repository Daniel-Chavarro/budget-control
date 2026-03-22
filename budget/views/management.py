"""Management views for units and users (admin only)."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from budget.decorators import admin_required
from budget.models import Unit, UserUnit
from budget.forms import UnitForm, UserUnitForm


@admin_required
def unit_list_view(request):
    """List all units."""
    units = Unit.objects.all()
    return render(request, 'budget/management/unit_list.html', {'units': units})


@admin_required
def unit_create_view(request):
    """Create new unit."""
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save()
            messages.success(request, f'Unit {unit.identifier} created successfully.')
            return redirect('budget:unit_list')
    else:
        form = UnitForm()
    
    return render(request, 'budget/management/unit_form.html', {
        'form': form,
        'action': 'Create'
    })


@admin_required
def unit_edit_view(request, pk):
    """Edit existing unit."""
    unit = get_object_or_404(Unit, pk=pk)
    
    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            unit = form.save()
            messages.success(request, f'Unit {unit.identifier} updated successfully.')
            return redirect('budget:unit_list')
    else:
        form = UnitForm(instance=unit)
    
    return render(request, 'budget/management/unit_form.html', {
        'form': form,
        'action': 'Edit',
        'unit': unit
    })


@admin_required
def unit_delete_view(request, pk):
    """Delete unit."""
    unit = get_object_or_404(Unit, pk=pk)
    identifier = unit.identifier
    unit.delete()
    messages.success(request, f'Unit {identifier} deleted successfully.')
    return redirect('budget:unit_list')
