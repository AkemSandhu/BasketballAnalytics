import PlayerLineChart from './PlayerLineChart'
import PlayerRadarChart from './PlayerRadarChart'
import PlayerShotChart from './PlayerShotChart'
import SimilarSeasonsList from './SimilarSeasonsList'
import PlayerBadges from './PlayerBadges'

const PlayerProfileCard = ({ playerData, allData, globalTab }) => {
  const seasonData = allData.filter(d => d.season === playerData.season)
  const offFits = seasonData.map(d => d.offensive_fit).filter(v => v !== undefined && v !== null)
  const defFits = seasonData.map(d => d.defensive_fit).filter(v => v !== undefined && v !== null)

  const calculatePercentile = (value, arr) => {
    if (!arr.length) return 0
    const sorted = [...arr].sort((a, b) => a - b)
    const rank = sorted.filter(v => v <= value).length
    return Math.round((rank / sorted.length) * 100)
  }

  const offPercentile = calculatePercentile(playerData.offensive_fit, offFits)
  const defPercentile = calculatePercentile(playerData.defensive_fit, defFits)

  const teamFits = seasonData.map(d => d.team_fit).filter(v => v !== undefined && v !== null)
  const teamFitPercentile = calculatePercentile(playerData.team_fit, teamFits)

  const posEstimates = [
    { label: 'PG', value: playerData.pos_estimate_pg || 0 },
    { label: 'SG', value: playerData.pos_estimate_sg || 0 },
    { label: 'SF', value: playerData.pos_estimate_sf || 0 },
    { label: 'PF', value: playerData.pos_estimate_pf || 0 },
    { label: 'C', value: playerData.pos_estimate_c || 0 },
  ]

  const getPositionColor = (pos) => {
    const colors = {
      'PG': '#3b82f6',
      'SG': '#10b981',
      'SF': '#f59e0b',
      'PF': '#ef4444',
      'C': '#8b5cf6'
    }
    return colors[pos] || '#6b7280'
  }

  return (
    <div className="bg-surfaceLight rounded-lg border border-border p-4 transition-all hover:border-primary/30">
      <div className="mb-3 border-b border-border pb-2">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-xl font-bold text-primary">{playerData.player_name}</h3>
            <p className="text-textSecondary text-sm">Season {playerData.season}</p>
          </div>
          <div className="text-right text-xs text-textSecondary">
            <div>Team: {playerData.team || 'N/A'}</div>
            <div>Pos: {playerData.pos || 'N/A'}</div>
            <div>Age: {playerData.age || 'N/A'} • MIN: {playerData.mp || 'N/A'}</div>
          </div>
        </div>
      </div>

      {globalTab === 0 && (
        <div className="space-y-4">
          <div className="flex justify-center">
            <div className="w-20 h-20 rounded-full bg-primary/20 border-2 border-primary flex items-center justify-center text-3xl font-bold text-primary">
              {playerData.pos || 'N/A'}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-surface rounded-lg p-3 border border-border">
              <p className="text-textSecondary text-xs uppercase tracking-wider">Offensive Role Fit</p>
              <p className="text-lg font-semibold text-white">{playerData.offensive_role || 'N/A'}</p>
              <div className="flex justify-between items-center mt-1">
                <span className="text-2xl font-bold text-secondary">{playerData.offensive_fit?.toFixed(3) || '–'}</span>
                <span className="text-sm text-textSecondary">{offPercentile}th percentile</span>
              </div>
            </div>
            <div className="bg-surface rounded-lg p-3 border border-border">
              <p className="text-textSecondary text-xs uppercase tracking-wider">Defensive Role Fit</p>
              <p className="text-lg font-semibold text-white">{playerData.defensive_role || 'N/A'}</p>
              <div className="flex justify-between items-center mt-1">
                <span className="text-2xl font-bold text-secondary">{playerData.defensive_fit?.toFixed(3) || '–'}</span>
                <span className="text-sm text-textSecondary">{defPercentile}th percentile</span>
              </div>
            </div>
          </div>
          <div>
            <p className="text-textSecondary text-xs uppercase tracking-wider mb-2">Positional Distribution</p>
            <div className="space-y-1">
              {posEstimates.map(({ label, value }) => (
                <div key={label} className="flex items-center space-x-2">
                  <span className="w-8 text-xs font-medium text-textSecondary">{label}</span>
                  <div className="flex-1 h-3 bg-surfaceLight rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{ width: `${Math.max(value, 0)}%`, backgroundColor: getPositionColor(label) }}
                    />
                  </div>
                  <span className="w-12 text-xs text-textSecondary text-right">{value.toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {globalTab === 1 && (
        <div>
          <p className="text-textSecondary text-sm mb-3">Percentile rank over seasons (Impact, Talent, USG%, TS%)</p>
          <PlayerLineChart playerData={playerData} allData={allData} />
        </div>
      )}

      {globalTab === 2 && (
        <div>
          <p className="text-textSecondary text-sm mb-3">Skill badges for this season</p>
          <PlayerBadges badges={playerData.badges} />
        </div>
      )}

      {globalTab === 3 && (
        <div>
          <p className="text-textSecondary text-sm mb-3">Box-score percentage stats – percentile ranks</p>
          <div className="flex justify-center mb-4">
            <div className="bg-surface rounded-lg p-4 border-2 border-secondary w-full max-w-xs text-center">
              <p className="text-textSecondary text-xs uppercase tracking-wider">Team Fit</p>
              <p className="text-3xl font-bold text-secondary">{playerData.team_fit?.toFixed(3) || '–'}</p>
              <p className="text-sm text-textSecondary">{teamFitPercentile}th percentile</p>
            </div>
          </div>
          <PlayerRadarChart playerData={playerData} allData={allData} />
        </div>
      )}

      {globalTab === 4 && (
        <div>
          <PlayerShotChart playerData={playerData} allData={allData} />
        </div>
      )}

      {globalTab === 5 && (
        <div>
          <SimilarSeasonsList similarSeasons={playerData.similar_seasons} />
        </div>
      )}
    </div>
  )
}

export default PlayerProfileCard