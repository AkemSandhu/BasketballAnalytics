import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts'

const PlayerLineChart = ({ playerData, allData }) => {
  // Get all seasons for this player up to the selected season
  const playerSeasons = allData
    .filter(d => d.player_name === playerData.player_name && d.season <= playerData.season)
    .sort((a, b) => a.season - b.season)

  if (playerSeasons.length === 0) {
    return <div className="text-textSecondary text-center py-8">No historical data available.</div>
  }

  // Compute percentiles per season for each metric
  const chartData = playerSeasons.map((ps, idx) => {
    const season = ps.season
    // All players for that season
    const seasonPlayers = allData.filter(d => d.season === season)

    const getPercentile = (value, key) => {
      if (value === undefined || value === null) return null
      const values = seasonPlayers.map(d => d[key]).filter(v => v !== undefined && v !== null)
      if (values.length === 0) return null
      const sorted = [...values].sort((a, b) => a - b)
      const rank = sorted.filter(v => v <= value).length
      return Math.round((rank / sorted.length) * 100)
    }

    return {
      season,
      impact: getPercentile(ps.impact_score, 'impact_score'),
      talent: getPercentile(ps.talent_score, 'talent_score'),
      usage: getPercentile(ps.usg_pct, 'usg_pct'),
      ts: getPercentile(ps.ts_pct, 'ts_pct'),
    }
  })

  // Filter out any nulls for each line if needed, but we'll keep them as gaps in line chart

  const colors = {
    impact: '#2b6ef0',
    talent: '#10b981',
    usage: '#f59e0b',
    ts: '#ef4444',
  }

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a35" />
          <XAxis dataKey="season" stroke="#a0a0b0" />
          <YAxis domain={[0, 100]} stroke="#a0a0b0" tickFormatter={(value) => `${value}%`} />
          <Tooltip
            contentStyle={{ backgroundColor: '#14141c', borderColor: '#2a2a35' }}
            formatter={(value) => `${value}%`}
          />
          <Legend wrapperStyle={{ color: '#a0a0b0' }} />
          <Line type="monotone" dataKey="impact" stroke={colors.impact} name="Impact Score" strokeWidth={2} dot={{ r: 3 }} />
          <Line type="monotone" dataKey="talent" stroke={colors.talent} name="Talent Score" strokeWidth={2} dot={{ r: 3 }} />
          <Line type="monotone" dataKey="usage" stroke={colors.usage} name="USG%" strokeWidth={2} dot={{ r: 3 }} />
          <Line type="monotone" dataKey="ts" stroke={colors.ts} name="TS%" strokeWidth={2} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default PlayerLineChart