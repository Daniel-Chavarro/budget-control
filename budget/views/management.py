"""Management views for users and categories (admin only)."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from budget.decorators import admin_required
from budget.models import UserProfile, Category
from budget.forms import UserCreateForm, CategoryForm


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
        
        if user_form.is_valid():
            user = user_form.save()
            messages.success(request, f'Usuario {user.username} creado exitosamente.')
            return redirect('budget:user_management')
    else:
        user_form = UserCreateForm()
    
    return render(request, 'budget/management/user_form.html', {
        'form': user_form,
        'action': 'Create',
    })


@admin_required
def user_delete_view(request, pk):
    """Delete a user."""
    user = get_object_or_404(User.objects.select_related('userprofile'), pk=pk)
    
    if user.is_superuser:
        messages.error(request, 'No se pueden eliminar cuentas de superadministrador.')
        return redirect('budget:user_management')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Usuario {username} eliminado exitosamente.')
        return redirect('budget:user_management')
    
    return render(request, 'budget/management/user_delete_confirm.html', {
        'user': user
    })


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
            messages.success(request, f'Categoria {category.name} creada exitosamente.')
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
            messages.success(request, f'Categoria {category.name} actualizada exitosamente.')
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
        messages.success(request, f'Categoria {category.name} desactivada.')
        return redirect('budget:category_list')
    
    return render(request, 'budget/management/category_delete.html', {
        'category': category
    })
