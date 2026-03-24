# Disable Units Feature and Account Editing

**Date:** 2026-03-24  
**Status:** Draft  
**Project:** Budget Control System

---

## 1. Overview

Two changes to the Budget Control app:
1. Disable (remove) the Units feature entirely
2. Add account editing capability for users to modify their own data

### 1.1 Scope Note

These two changes are combined in one spec because:
- Both are small, related changes to simplify the app
- Units removal is a cleanup task (no new feature)
- Account editing is the new feature
- They can be implemented in sequence within a single plan

---

## 2. Disable Units Feature

### 2.1 Description

Remove all code and data related to Unit and UserUnit models. This feature is currently not needed.

### 2.2 Components to Remove

| Component | File | Action |
|-----------|------|--------|
| Models | `budget/models/unit.py` | Delete file |
| Model imports | `budget/models/__init__.py` | Remove Unit, UserUnit imports |
| URLs | `budget/urls.py` | Remove unit-related paths |
| Views | `budget/views/management.py` | Remove unit_list_view, unit_create_view, unit_edit_view, unit_delete_view |
| Templates | `budget/templates/budget/management/unit_*.html` | Delete unit templates |
| Admin | `budget/admin.py` | Remove unit registrations |
| Navigation | `budget/templates/budget/base.html` | Remove unit links |
| Context | `budget/context_processors.py` | Remove unit-related context |

### 2.3 Database

Create a Django migration to:
- Remove the `user_units` table
- Remove the `units` table

---

## 3. Account Editing Feature

### 3.1 Description

Allow users to edit their own account data: username, email, phone, and password.

### 3.2 User Stories

| Story |
|-------|
| As a user, I want to edit my username so I can change it if needed |
| As a user, I want to edit my email address so I can update my contact info |
| As a user, I want to change my password so I can maintain account security |
| As a user, I want to edit my phone number in my profile |

### 3.3 Components to Add

| Component | File | Description |
|-----------|------|-------------|
| URL | `budget/urls.py` | Add path for account settings |
| View | `budget/views/account.py` | New file with account settings view |
| Form | `budget/forms/account_forms.py` | New file with account edit form |
| Template | `budget/templates/budget/account/account_settings.html` | New account settings page |
| Navigation | `budget/templates/budget/base.html` | Add "Account" link to nav |

### 3.3.1 UserProfile Integration

The view will access UserProfile via `request.user.userprofile` (one-to-one relationship). When updating phone:
1. Get `userprofile = request.user.userprofile`
2. Update `userprofile.phone = form.cleaned_data['phone']`
3. Save with `userprofile.save()`

### 3.4 Form Fields

The account settings form will include:
- **Username** - CharField, required, unique
- **Email** - EmailField, required, unique  
- **Phone** - CharField, optional (from UserProfile)
- **Password** - Separate change password form

### 3.5 Validation Rules

- Username: required, unique, max 150 chars
- Email: required, valid format, unique (excluding current user)
- Phone: optional, max 20 chars
- Password: must match current password to change, min 8 chars, max 128 chars

### 3.6 Edge Cases

- **Duplicate username/email**: Form validation error "A user with that username/email already exists"
- **New password same as current**: Form validation error "New password must be different from current password"
- **Phone blank**: Allow empty string, save as blank to UserProfile

### 3.7 Security

- Users can only edit their own account (request.user)
- Password change requires current password verification
- Email uniqueness check excludes current user
- After password change: call `update_session_auth_hash(request, user)` to maintain session

### 3.8 Session Handling

After password change, the user should stay logged in:
1. Call `user.set_password(new_password)`
2. Call `user.save()`
3. Call `update_session_auth_hash(request, user)` to refresh session

---

## 4. UI/UX

### 4.1 Navigation

Add "Account" link in the navigation bar (next to Logout):
- Position: Right side of nav bar
- Label: "Account" or user icon

### 4.2 Account Settings Page Layout

```
+------------------------------------------+
| Account Settings                         |
+------------------------------------------+
| Username:    [_______________]           |
| Email:       [_______________]           |
| Phone:       [_______________]           |
|                                          |
| [Save Changes]                           |
+------------------------------------------+

+------------------------------------------+
| Change Password                          |
+------------------------------------------+
| Current Password: [_______________]       |
| New Password:     [_______________]       |
| Confirm Password: [_______________]       |
|                                          |
| [Change Password]                        |
+------------------------------------------+
```

---

## 5. Data Flow

### 5.1 Account Update Flow

1. User clicks "Account" in nav
2. GET `/account/` loads current user data into form
3. User edits fields and submits
4. View validates data (unique checks)
5. If valid: update User.username, User.email, UserProfile.phone
6. Show success message, reload form
7. If invalid: show error messages, preserve form data

### 5.2 Password Change Flow

1. User fills current password, new password, confirm
2. View verifies current password with `user.check_password()`
3. If valid: set new password with `user.set_password()`
4. Show success message

---

## 6. Acceptance Criteria

### Units Removal

- [ ] No unit-related URLs accessible (404)
- [ ] No unit links in navigation
- [ ] Unit models removed from code
- [ ] Database tables removed via migration

### Account Editing

- [ ] Account page accessible via nav link
- [ ] Username can be edited and saved
- [ ] Email can be edited and saved
- [ ] Phone can be edited and saved
- [ ] Password can be changed with current password verification
- [ ] Form validation shows appropriate errors
- [ ] Success messages displayed after save
- [ ] Users cannot edit other users' accounts

---

## 7. Testing

### Unit Tests

**AccountForm:**
- Valid data passes validation
- Empty username fails validation
- Empty email fails validation
- Invalid email format fails validation
- Duplicate username fails validation (excluding current user)
- Duplicate email fails validation (excluding current user)
- Valid phone passes validation
- Empty phone passes validation

**PasswordChangeForm:**
- Wrong current password fails validation
- New password same as current fails validation
- Passwords not matching fails validation
- Password too short fails validation
- Valid password change passes validation

### View Tests
- GET /account/ returns 200 for authenticated users
- GET /account/ redirects to login for anonymous users
- POST with valid data updates user and shows success
- POST with invalid data shows errors
- Password change updates password correctly
- User cannot modify another user's account

### Manual Tests
- Edit own account data
- Try to change password with wrong current password
- Verify changes persist after logout/login
- Verify still logged in after password change
