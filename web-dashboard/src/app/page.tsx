import { redirect } from 'next/navigation';
import { getServerSession } from '@/lib/auth';

/**
 * Main page - Routes to appropriate dashboard based on user role
 */
export default async function Home() {
  const session = await getServerSession();

  // Uncomment below to require authentication
  // if (!session) {
  //   redirect('/login');
  // }

  // For development, show admin dashboard by default
  // In production, this would redirect based on session.user.role
  // redirect('/dashboard');

  // For now, show a role selector for demonstration
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">HealthGuard</h1>
          <p className="text-xl text-gray-600">Restaurant Compliance Monitoring Platform</p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6 text-center">
            Select Your Role
          </h2>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Admin Dashboard */}
            <a
              href="/dashboard/admin"
              className="block p-6 border-2 border-purple-200 rounded-xl hover:border-purple-500 hover:bg-purple-50 transition-all"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                  <span className="text-2xl">👤</span>
                </div>
                <div>
                  <h3 className="font-semibold text-lg">Admin Dashboard</h3>
                  <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">ADMIN</span>
                </div>
              </div>
              <p className="text-sm text-gray-600">
                Organization-wide oversight, multi-restaurant management, user administration, billing
              </p>
            </a>

            {/* Manager Dashboard */}
            <a
              href="/dashboard/manager"
              className="block p-6 border-2 border-blue-200 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-all"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <span className="text-2xl">👨‍💼</span>
                </div>
                <div>
                  <h3 className="font-semibold text-lg">Manager Dashboard</h3>
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">MANAGER</span>
                </div>
              </div>
              <p className="text-sm text-gray-600">
                Single restaurant operations, staff scheduling, task management, compliance reporting
              </p>
            </a>

            {/* Staff Dashboard */}
            <a
              href="/dashboard/staff"
              className="block p-6 border-2 border-green-200 rounded-xl hover:border-green-500 hover:bg-green-50 transition-all"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <span className="text-2xl">👨‍🍳</span>
                </div>
                <div>
                  <h3 className="font-semibold text-lg">Staff Dashboard</h3>
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">STAFF</span>
                </div>
              </div>
              <p className="text-sm text-gray-600">
                Daily tasks, quick temperature logging, checklists, training materials
              </p>
            </a>

            {/* Inspector Dashboard */}
            <a
              href="/dashboard/inspector"
              className="block p-6 border-2 border-orange-200 rounded-xl hover:border-orange-500 hover:bg-orange-50 transition-all"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                  <span className="text-2xl">📋</span>
                </div>
                <div>
                  <h3 className="font-semibold text-lg">Inspector Dashboard</h3>
                  <span className="text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded">INSPECTOR</span>
                </div>
              </div>
              <p className="text-sm text-gray-600">
                Inspection scheduling, violation tracking, compliance scoring, follow-up management
              </p>
            </a>
          </div>

          <div className="mt-8 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600 text-center">
              <strong>Note:</strong> In production, users will be automatically routed to their appropriate dashboard based on their role.
              This selector is for demonstration purposes.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
