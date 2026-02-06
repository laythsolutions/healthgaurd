# HealthGuard Web Dashboard

Multi-location restaurant compliance monitoring dashboard built with Next.js 14, React, and Tailwind CSS.

## Features

- **Real-Time Monitoring**: Live sensor data updates
- **Multi-Location Dashboard**: Overview of all restaurants
- **Alert Management**: View and acknowledge alerts
- **Compliance Reports**: Generate PDF reports
- **Dark Mode**: Full dark mode support
- **Responsive**: Works on all screen sizes

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **UI**: shadcn/ui + Radix UI
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **State**: Zustand + React Query
- **TypeScript**: Full type safety

## Getting Started

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Configuration

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
src/
├── app/              # Next.js app directory
├── components/       # React components
│   ├── dashboard/   # Dashboard components
│   ├── sensors/     # Sensor monitoring
│   ├── alerts/      # Alert management
│   └── ui/          # shadcn/ui components
├── lib/             # Utilities
├── hooks/           # React hooks
└── types/           # TypeScript types
```

## API Integration

The dashboard connects to the Django backend via REST API:

```typescript
import { sensorsApi } from '@/lib/api';

const readings = await sensorsApi.latest(restaurantId);
```
