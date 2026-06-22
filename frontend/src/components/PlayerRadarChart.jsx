import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts'

const PlayerRadarChart = ({ playerData, allData }) => {
  // Compute percentiles for each box-score percentage stat for this season
  const seasonData = allData.filter(d => d.season === playerData.season)

  const getPercentile = (value, key) => {
    if (value === undefined || value === null) return 0
    const values = seasonData.map(d => d[key]).filter(v => v !== undefined && v !== null)
    if (values.length === 0) return 0
    const sorted = [...values].sort((a, b) => a - b)
    const rank = sorted.filter(v => v <= value).length
    return Math.round((rank / sorted.length) * 100)
  }

  // Stats in desired order: TOV%, AST%, ORB%, DRB%, BLK%, STL%
  const stats = [
    { key: 'tov_pct', label: 'TOV%', inverse: true },
    { key: 'ast_pct', label: 'AST%', inverse: false },
    { key: 'orb_pct', label: 'ORB%', inverse: false },
    { key: 'drb_pct', label: 'DRB%', inverse: false },
    { key: 'blk_pct', label: 'BLK%', inverse: false },
    { key: 'stl_pct', label: 'STL%', inverse: false },
  ]

  const chartData = stats.map(({ key, label, inverse }) => {
    const rawPercentile = getPercentile(playerData[key], key)
    const finalPercentile = inverse ? 100 - rawPercentile : rawPercentile
    return {
      stat: label,
      percentile: finalPercentile,
    }
  })

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={chartData}>
        <PolarGrid stroke="#2a2a35" />
        <PolarAngleAxis dataKey="stat" stroke="#a0a0b0" tick={{ fontSize: 10 }} />
        <PolarRadiusAxis domain={[0, 100]} stroke="#2a2a35" />
        <Tooltip formatter={(value) => `${value}%`} />
        <Radar
          name="Percentile"
          dataKey="percentile"
          stroke="#2b6ef0"
          fill="#2b6ef0"
          fillOpacity={0.6}
        />
      </RadarChart>
    </ResponsiveContainer>
  )
}

export default PlayerRadarChart