import { Link } from 'react-router-dom'

const Navbar = () => {
  return (
    <nav className="bg-surface border-b border-border sticky top-0 z-50">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
          NBA<span className="text-white">Analytics</span>
        </Link>
        <div className="space-x-6">
          <Link to="/" className="hover:text-primary transition">Leaderboard</Link>
          <a href="/docs" className="hover:text-primary transition" target="_blank">API Docs</a>
        </div>
      </div>
    </nav>
  )
}

export default Navbar