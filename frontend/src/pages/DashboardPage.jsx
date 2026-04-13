import Navbar from "../components/Layout/Navbar";
import DashboardMain from "../components/Dashboard/DashboardMain";

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <Navbar />
      <main className="pt-20 pb-8 px-4 max-w-7xl mx-auto">
        <DashboardMain />
      </main>
    </div>
  );
}
