import RegisterForm from "../components/Auth/RegisterForm";
import AnimatedBackground from "../components/3DBackground/AnimatedBackground";
import Navbar from "../components/Layout/Navbar";

export default function RegisterPage() {
  return (
    <div className="min-h-screen relative">
      <AnimatedBackground />
      <Navbar />
      <div className="relative z-10 pt-24 pb-8 px-4 flex items-center justify-center min-h-screen">
        <RegisterForm />
      </div>
    </div>
  );
}
