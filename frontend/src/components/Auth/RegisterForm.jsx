import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { FiCheckCircle } from "react-icons/fi";

import { useAuth } from "../../context/AuthContext";

export default function RegisterForm() {
  const [formData, setFormData] = useState({ username: "", email: "", password: "", confirmPassword: "", full_name: "" });
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (event) => {
    setFormData((prev) => ({ ...prev, [event.target.name]: event.target.value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    setLoading(true);
    try {
      await register(formData);
      toast.success("Registration successful");
      navigate("/dashboard");
    } catch (error) {
      toast.error(error.response?.data?.error || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-lg mx-auto glass rounded-2xl p-8 md:p-9">
      <h2 className="text-3xl font-bold text-center mb-2">Create your account</h2>
      <p className="text-sm text-slate-300 text-center mb-6">Start with secure authentication and real-time hijacking detection.</p>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="field-label">Full name</label>
          <input name="full_name" value={formData.full_name} onChange={handleChange} placeholder="Your full name" className="pro-input" autoComplete="name" />
        </div>
        <div>
          <label className="field-label">Username</label>
          <input name="username" value={formData.username} onChange={handleChange} placeholder="Choose a username" required className="pro-input" autoComplete="username" />
        </div>
        <div>
          <label className="field-label">Email address</label>
          <input name="email" type="email" value={formData.email} onChange={handleChange} placeholder="you@example.com" required className="pro-input" autoComplete="email" />
        </div>
        <div>
          <label className="field-label">Password</label>
          <input name="password" type="password" value={formData.password} onChange={handleChange} placeholder="Create a password" required className="pro-input" autoComplete="new-password" />
        </div>
        <div>
          <label className="field-label">Confirm password</label>
          <input name="confirmPassword" type="password" value={formData.confirmPassword} onChange={handleChange} placeholder="Re-enter password" required className="pro-input" autoComplete="new-password" />
        </div>

        <div className="rounded-xl border border-slate-500/30 bg-slate-900/40 p-3 text-xs text-slate-300">
          <p className="flex items-center gap-2"><FiCheckCircle className="text-emerald-400" /> Use at least 8 characters with letters, numbers and symbols.</p>
        </div>

        <button type="submit" disabled={loading} className="w-full cyber-btn py-3.5">
          {loading ? "Creating account..." : "Create secure account"}
        </button>
      </form>
      <p className="mt-6 text-center text-slate-300">Already have an account? <Link to="/login" className="text-sky-300 hover:text-sky-200">Login</Link></p>
    </div>
  );
}
