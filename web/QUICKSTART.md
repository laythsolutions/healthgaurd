# Running HealthGuard Dashboards

## Quick Start

### 1. Install Dependencies

```bash
cd web-dashboard
npm install
```

### 2. Run Development Server

```bash
npm run dev
```

### 3. Access Dashboards

Open http://localhost:3000 in your browser

You'll see a **Role Selector** with 4 options:

1. **Admin Dashboard** - Organization management
2. **Manager Dashboard** - Restaurant operations
3. **Staff Dashboard** - Daily tasks
4. **Inspector Dashboard** - Health inspections

---

## Dashboard URLs

Once running, you can directly access:

- http://localhost:3000/dashboard/admin
- http://localhost:3000/dashboard/manager
- http://localhost:3000/dashboard/staff
- http://localhost:3000/dashboard/inspector

---

## File Structure

```
web-dashboard/src/
├── app/
│   ├── page.tsx                    # Main page (role selector)
│   └── dashboard/
│       ├── [role]/page.tsx         # Role router (fixed)
│       ├── admin/page.tsx          # Admin dashboard page
│       ├── manager/page.tsx        # Manager dashboard page
│       ├── staff/page.tsx          # Staff dashboard page
│       └── inspector/page.tsx      # Inspector dashboard page
└── components/dashboard/
    ├── admin-dashboard.tsx         # Admin UI
    ├── manager-dashboard.tsx       # Manager UI
    ├── staff-dashboard.tsx         # Staff UI
    ├── inspector-dashboard.tsx     # Inspector UI
    └── index.ts                    # Exports
```

---

## Fixed Issues

✅ Removed `next-auth` dependency (not installed yet)
✅ Created route pages for each role
✅ Fixed module resolution errors
✅ Added proper component exports

---

## Next Steps

1. Install dependencies: `npm install`
2. Run dev server: `npm run dev`
3. View dashboards at http://localhost:3000

---

**Note:** In production, the `[role]/page.tsx` router will automatically redirect users based on their authenticated session role. For development, we use the manual role selector on the homepage.
