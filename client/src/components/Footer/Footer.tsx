import { Link } from "react-router-dom"

export default function Footer() {
  return (
    <footer className="w-full py-12 px-4 sm:px-6 lg:px-8 bg-neutral-900 text-neutral-400">
      <div className="max-w-6xl mx-auto grid md:grid-cols-4 gap-8">
        <div>
          <p className="font-bold text-xl text-white mb-4">CareerPath</p>
          <p className="text-sm">Plan your career with confidence using AI-powered simulations.</p>
        </div>
        <div>
          <p className="font-semibold text-white mb-4">Product</p>
          <ul className="space-y-2 text-sm">
            <li><Link to="/features" className="hover:text-white transition-colors">Features</Link></li>
            <li><Link to="/dashboard" className="hover:text-white transition-colors">Dashboard</Link></li>
            <li><Link to="/reports" className="hover:text-white transition-colors">Reports</Link></li>
          </ul>
        </div>
        <div>
          <p className="font-semibold text-white mb-4">Company</p>
          <ul className="space-y-2 text-sm">
            <li><Link to="/about" className="hover:text-white transition-colors">About</Link></li>
            <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
          </ul>
        </div>
        <div>
          <p className="font-semibold text-white mb-4">Legal</p>
          <ul className="space-y-2 text-sm">
            <li><a href="#" className="hover:text-white transition-colors">Privacy</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Terms</a></li>
          </ul>
        </div>
      </div>
      <div className="max-w-6xl mx-auto mt-8 pt-8 border-t border-neutral-800 text-center text-sm">
        <p>&copy; 2025 CareerPath. All rights reserved.</p>
      </div>
    </footer>
  )
}