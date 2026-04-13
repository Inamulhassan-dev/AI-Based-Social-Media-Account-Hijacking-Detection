import Navbar from "../components/Layout/Navbar";
import AlertPanel from "../components/Alerts/AlertPanel";

export default function AlertsPage() {
  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <Navbar />
      <main className="pt-20 pb-8 px-4 max-w-7xl mx-auto">
        <AlertPanel />
      </main>
    </div>
  );
}
