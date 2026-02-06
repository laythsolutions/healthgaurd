import { redirect } from 'next/navigation';
import { getServerSession } from '@/lib/auth';
import { DashboardPage } from '@/components/dashboard/dashboard-page';

export default async function Home() {
  const session = await getServerSession();

  if (!session) {
    redirect('/login');
  }

  return <DashboardPage />;
}
