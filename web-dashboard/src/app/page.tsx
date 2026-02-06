import { redirect } from 'next/navigation';
import { getServerSession } from '@/lib/auth';
import { DashboardPage } from '@/components/dashboard/dashboard-page';

export default async function Home() {
  // For development, show dashboard without authentication
  const session = await getServerSession();

  // Uncomment below to require authentication
  // if (!session) {
  //   redirect('/login');
  // }

  return <DashboardPage />;
}
