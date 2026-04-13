import Navbar from "../components/Layout/Navbar";
import AdminDashboard from "../components/Admin/AdminDashboard";

export default function AdminPage() {
  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <Navbar />
      <main className="pt-20 pb-8 px-4 max-w-7xl mx-auto">
        <AdminDashboard />
      </main>
    </div>
  );
}
