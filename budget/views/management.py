"""Management views for units, users, and categories (admin only)."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from budget.decorators import admin_required
from budget.models import Unit, UserUnit, UserProfile, Category
from budget.forms import UnitForm, UserUnitForm, UserCreateForm, CategoryForm


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


@admin_required
def user_management_view(request):
    """List all users with their profiles."""
    users = User.objects.select_related('userprofile').all()
    return render(request, 'budget/management/user_list.html', {'users': users})


@admin_required
def user_create_view(request):
    """Create a new tenant or unlinked_user."""
    if request.method == 'POST':
        user_form = UserCreateForm(request.POST)
        role = request.POST.get('role', 'tenant')
        
        if user_form.is_valid():
            user = user_form.save()
            profile = UserProfile.objects.get_or_create(user=user)[0]
            profile.role = role
            profile.save()
            messages.success(request, f'User {user.username} created successfully.')
            return redirect('budget:user_management')
    else:
        user_form = UserCreateForm()
        role = 'tenant'
    
    return render(request, 'budget/management/user_form.html', {
        'form': user_form,
        'action': 'Create',
        'role': role
    })


@admin_required
def user_delete_view(request, pk):
    """Delete a user."""
    user = get_object_or_404(User, pk=pk)
    
    if user.is_superuser:
        messages.error(request, 'Cannot delete superuser accounts.')
        return redirect('budget:user_management')
    
    username = user.username
    user.delete()
    messages.success(request, f'User {username} deleted successfully.')
    return redirect('budget:user_management')


@admin_required
def category_list_view(request):
    """List all categories."""
    categories = Category.objects.all()
    return render(request, 'budget/management/category_list.html', {'categories': categories})


@admin_required
def category_create_view(request):
    """Create new category."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Categoria {category.name_es} creada exitosamente.')
            return redirect('budget:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'budget/management/category_form.html', {
        'form': form,
        'action': 'Crear'
    })


@admin_required
def category_edit_view(request, pk):
    """Edit existing category."""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Categoria {category.name_es} actualizada exitosamente.')
            return redirect('budget:category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'budget/management/category_form.html', {
        'form': form,
        'action': 'Editar',
        'category': category
    })


@admin_required
def category_delete_view(request, pk):
    """Delete category (soft delete by deactivating)."""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category.is_active = False
        category.save()
        messages.success(request, f'Categoria {category.name_es} desactivada.')
        return redirect('budget:category_list')
    
    return render(request, 'budget/management/category_delete.html', {
        'category': category
    })
