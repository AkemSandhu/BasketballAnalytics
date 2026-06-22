const PlayerBadges = ({ badges }) => {
  if (!badges || Object.keys(badges).length === 0) {
    return <div className="text-textSecondary text-center py-8">No badge data available for this season.</div>
  }

  // Sort badges alphabetically for display
  const sortedBadges = Object.entries(badges).sort((a, b) => a[0].localeCompare(b[0]))

  const tierColors = {
    'Diamond': 'bg-purple-600 border-purple-400 text-white',
    'Gold': 'bg-yellow-600 border-yellow-400 text-white',
    'Silver': 'bg-gray-400 border-gray-300 text-black',
    'Bronze': 'bg-amber-700 border-amber-500 text-white',
  }

  const tierBadge = (tier) => {
    return tierColors[tier] || 'bg-surface border-border text-textSecondary'
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
      {sortedBadges.map(([name, tier]) => (
        <div
          key={name}
          className={`px-3 py-2 rounded-lg border text-center text-sm font-medium ${tierBadge(tier)}`}
        >
          {name}
          <br />
          <span className="text-xs opacity-80">{tier}</span>
        </div>
      ))}
    </div>
  )
}

export default PlayerBadges