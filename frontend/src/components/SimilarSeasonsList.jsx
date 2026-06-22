const SimilarSeasonsList = ({ similarSeasons }) => {
  if (!similarSeasons || similarSeasons.length === 0) {
    return <p className="text-textSecondary text-center py-8">No similar seasons found.</p>
  }

  const seasons = similarSeasons.map(item => {
    if (Array.isArray(item)) {
      return { player_name: item[0], season: item[1], similarity: item[2] }
    }
    return item
  })

  return (
    <div className="space-y-2">
      <p className="text-textSecondary text-sm mb-3">Most similar playstyle seasons</p>
      {seasons.map((s, idx) => (
        <div key={idx} className="bg-surfaceLight rounded-lg p-3 border border-border flex justify-between items-center">
          <div>
            <span className="font-semibold text-white">{s.player_name}</span>
            <span className="text-textSecondary text-sm ml-2">({s.season})</span>
          </div>
          <span className="text-secondary text-sm font-mono">{s.similarity?.toFixed(4) || '–'}</span>
        </div>
      ))}
    </div>
  )
}

export default SimilarSeasonsList