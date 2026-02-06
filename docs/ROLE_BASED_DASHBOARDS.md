# HealthGuard Role-Based Dashboards

## Overview

HealthGuard provides **four specialized dashboards**, each tailored to a specific user role. This ensures users see only the features and information relevant to their responsibilities.

---

## Dashboard Types

### 1. Admin Dashboard 👤

**Role:** `ADMIN`

**Users:** Organization owners, multi-location managers, executives

**Key Features:**
- Multi-restaurant portfolio oversight
- Aggregate compliance analytics across all locations
- User and team management
- Billing and subscription management
- System-wide alert monitoring
- Performance benchmarking between locations
- Revenue tracking and reporting

**View:** Organization-wide, strategic level

**Tabs:**
- Restaurants (portfolio view)
- Users (team management)
- Analytics (organization trends)
- System Alerts (critical issues across locations)
- Billing (invoices, payments)
- Settings (organization configuration)

---

### 2. Manager Dashboard 👨‍💼

**Role:** `MANAGER`

**Users:** Restaurant managers, general managers, location owners

**Key Features:**
- Single restaurant comprehensive view
- Real-time sensor monitoring
- Staff scheduling and shift management
- Task assignment and tracking
- Manual log review and approval
- Alert management and response
- Compliance report generation
- Performance analytics for their location

**View:** Single-location, operational level

**Tabs:**
- Sensors (real-time monitoring)
- Tasks (today's checklist, assignments)
- Staff (scheduling, performance)
- Manual Logs (review and approve)
- Reports (generate compliance reports)
- Alerts (active alerts for this location)

---

### 3. Staff Dashboard 👨‍🍳

**Role:** `STAFF`

**Users:** Line cooks, servers, kitchen staff, front-of-house staff

**Key Features:**
- Simplified, mobile-optimized interface
- Today's task checklist
- Quick temperature logging
- Real-time sensor status verification
- Training materials and guides
- Personal task completion tracking
- Relevant alerts only

**View:** Personal, task-focused level

**Tabs:**
- Tasks (my assigned tasks)
- Sensors (quick temp verification)
- Alerts (relevant notifications)
- Training (learning materials)

**Design:**
- Large, touch-friendly buttons
- Progress tracking
- Minimal reading required
- Quick completion focus

---

### 4. Inspector Dashboard 📋

**Role:** `INSPECTOR`

**Users:** Health department inspectors, third-party auditors

**Key Features:**
- Inspection routing and queue management
- Digital inspection forms
- Violation documentation
- Compliance scoring
- Follow-up scheduling
- Historical inspection data
- Restaurant lookup and search

**View:** Regulatory, enforcement level

**Tabs:**
- Scheduled (upcoming inspections)
- Conduct Inspection (digital form)
- History (past inspections)
- Violations (tracking and follow-up)
- Follow-ups (re-inspection schedule)

---

## Access Control

### Restaurant Access Levels

In addition to **user roles**, users have **access levels** for each restaurant:

| Access Level | Permissions |
|-------------|-------------|
| **OWNER** | Full control, can manage other users, billing, settings |
| **MANAGER** | Can manage operations, tasks, reports, but not billing/user management |
| **VIEWER** | Read-only access to view data and reports |

### Example Combinations

```
User: Jane Smith
Role: MANAGER
Access: OWNER at Downtown Location
       MANAGER at Midtown Location
       VIEWER at Uptown Location
```

Jane can:
- Fully manage Downtown Location
- Manage operations at Midtown (but not billing)
- Only view data at Uptown

---

## Routing Logic

Users are automatically routed based on their role:

```python
if session.user.role == 'ADMIN':
    redirect('/dashboard/admin')
elif session.user.role == 'MANAGER':
    redirect('/dashboard/manager')
elif session.user.role == 'STAFF':
    redirect('/dashboard/staff')
elif session.user.role == 'INSPECTOR':
    redirect('/dashboard/inspector')
```

---

## Feature Comparison

| Feature | Admin | Manager | Staff | Inspector |
|---------|-------|---------|-------|-----------|
| Multi-restaurant view | ✅ | ❌ | ❌ | ❌ |
| Single-restaurant details | ✅ | ✅ | ✅ | ✅ |
| Real-time sensor data | ✅ | ✅ | ✅ | ❌ |
| Task management | ✅ | ✅ | ✅ (own) | ❌ |
| Staff scheduling | ✅ | ✅ | ❌ | ❌ |
| Report generation | ✅ | ✅ | ❌ | ✅ |
| User management | ✅ | ❌ | ❌ | ❌ |
| Billing | ✅ | ❌ | ❌ | ❌ |
| Inspections | ❌ | ❌ | ❌ | ✅ |
| Training | ❌ | ❌ | ✅ | ❌ |
| System alerts | ✅ | ✅ (own) | ✅ (relevant) | ❌ |

---

## Technical Implementation

### Backend Models

```python
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        MANAGER = 'MANAGER', 'Manager'
        STAFF = 'STAFF', 'Staff'
        INSPECTOR = 'INSPECTOR', 'Inspector'

    role = models.CharField(max_length=20, choices=Role.choices)
    organization = models.ForeignKey('Organization', ...)
    restaurants = models.ManyToManyField('Restaurant', through='RestaurantAccess')

class RestaurantAccess(models.Model):
    class AccessLevel(models.TextChoices):
        OWNER = 'OWNER', 'Owner'
        MANAGER = 'MANAGER', 'Manager'
        VIEWER = 'VIEWER', 'Viewer'

    user = models.ForeignKey('User', ...)
    restaurant = models.ForeignKey('Restaurant', ...)
    access_level = models.CharField(max_length=20, choices=AccessLevel.choices)
```

### Frontend Routing

```typescript
// app/dashboard/[role]/page.tsx
export default async function RoleBasedDashboard() {
  const session = await getServerSession();

  switch (session.user?.role) {
    case 'ADMIN':
      redirect('/dashboard/admin');
    case 'MANAGER':
      redirect('/dashboard/manager');
    case 'STAFF':
      redirect('/dashboard/staff');
    case 'INSPECTOR':
      redirect('/dashboard/inspector');
  }
}
```

---

## Screenshots Overview

### Admin Dashboard
- Restaurant portfolio grid with performance metrics
- Aggregate compliance trends chart
- User management table
- Billing summary

### Manager Dashboard
- Single-restaurant KPI cards
- Real-time sensor chart
- Staff schedule calendar
- Task checklist with assignments

### Staff Dashboard
- Large progress indicator
- Checklist with big checkboxes
- Quick temperature verification
- Mobile-optimized layout

### Inspector Dashboard
- Inspection queue with routing
- Digital inspection form
- Violation tracking
- Follow-up calendar

---

## Customization

Each dashboard can be further customized based on:
- Organization preferences
- User permissions
- Restaurant type (fine dining, fast food, etc.)
- Local regulations
- Specific operational needs

---

**Last Updated:** 2026-02-06
**Version:** 2.0.0
