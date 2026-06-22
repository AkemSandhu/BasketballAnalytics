const PlayerShotChart = ({ playerData, allData }) => {
  const seasonData = allData.filter(d => d.season === playerData.season)

  const getPercentile = (value, key) => {
    if (value === undefined || value === null) return 0
    const values = seasonData.map(d => d[key]).filter(v => v !== undefined && v !== null)
    if (values.length === 0) return 0
    const sorted = [...values].sort((a, b) => a - b)
    const rank = sorted.filter(v => v <= value).length
    return Math.round((rank / sorted.length) * 100)
  }

  const zones = [
    { key: 'at_rim', label: 'At Rim', accKey: 'at_rim_accuracy', fgaKey: 'at_rim_fga' },
    { key: 'short_mid', label: 'Short Mid', accKey: 'short_mid_range_accuracy', fgaKey: 'short_mid_range_fga' },
    { key: 'long_mid', label: 'Long Mid', accKey: 'long_mid_range_accuracy', fgaKey: 'long_mid_range_fga' },
    { key: 'corner3', label: 'Corner 3', accKey: 'corner3_accuracy', fgaKey: 'corner3_fga' },
    { key: 'arc3', label: 'Arc 3', accKey: 'arc3_accuracy', fgaKey: 'arc3_fga' },
  ]

  const chartData = zones.map(zone => {
    const acc = playerData[zone.accKey]
    const fga = playerData[zone.fgaKey]
    const accPct = getPercentile(acc, zone.accKey)
    const volPct = getPercentile(fga, zone.fgaKey)
    const hue = 120 * (accPct / 100)
    const color = `hsl(${hue}, 80%, 50%)`
    const opacity = 0.1 + 0.9 * (volPct / 100)
    return {
      ...zone,
      accPct,
      volPct,
      color,
      opacity,
      accDisplay: acc !== undefined && acc !== null ? acc.toFixed(1) : '–',
      fgaDisplay: fga !== undefined && fga !== null ? fga.toFixed(1) : '–',
    }
  })

  return (
    <div className="w-full">
      <p className="text-textSecondary text-sm mb-3">Shot efficiency (color) and volume (opacity) – percentile ranks</p>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
        {chartData.map((zone) => (
          <div
            key={zone.key}
            className="rounded-lg border border-border p-3 text-center flex flex-col items-center justify-center min-h-[120px] transition-all"
            style={{
              backgroundColor: `rgba(0,0,0,0.4)`,
              borderColor: zone.color,
              opacity: zone.opacity,
            }}
          >
            <div className="text-xs font-semibold text-textSecondary uppercase tracking-wider mb-1">{zone.label}</div>
            <div className="text-lg font-bold text-white">{zone.accDisplay}</div>
            <div className="text-xs text-textSecondary">Acc: {zone.accPct}%</div>
            <div className="text-xs text-textSecondary">Vol: {zone.volPct}%</div>
            <div className="text-xs text-textSecondary">FGA: {zone.fgaDisplay}</div>
          </div>
        ))}
      </div>
      <div className="flex flex-wrap justify-between items-center mt-3 text-xs text-textSecondary gap-2">
        <span>🔴 Low efficiency → 🟢 High efficiency</span>
        <span>⬜ Low volume → 🟩 High volume</span>
      </div>
    </div>
  )
}

export default PlayerShotChart