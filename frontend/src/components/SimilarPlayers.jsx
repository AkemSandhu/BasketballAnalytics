import { Link } from 'react-router-dom'

const SimilarPlayers = ({ players }) => {
  if (!players || players.length === 0) return <p className="text-textSecondary">No similar seasons found.</p>
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
      {players.map((p, idx) => (
        <Link to={`/player/${p.player_id}`} key={idx} className="bg-surfaceLight p-3 rounded-lg hover:bg-surface transition group">
          <div className="font-semibold group-hover:text-primary">{p.player_name}</div>
          <div className="text-textSecondary text-sm">{p.season} • similarity {p.similarity?.toFixed(2)}</div>
        </Link>
      ))}
    </div>
  )
}
export default SimilarPlayers