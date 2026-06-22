import { useState, useEffect } from 'react'

const FilterPanel = ({ isOpen, onClose, rowData, onFilter }) => {
  const [filters, setFilters] = useState({})
  const [roleOptions, setRoleOptions] = useState({ offensive: [], defensive: [] })

  useEffect(() => {
    if (!rowData || rowData.length === 0) return
    const offRoles = [...new Set(rowData.map(r => r.offensive_role).filter(Boolean))].sort()
    const defRoles = [...new Set(rowData.map(r => r.defensive_role).filter(Boolean))].sort()
    setRoleOptions({ offensive: offRoles, defensive: defRoles })
  }, [rowData])

  // All columns that should NOT appear as numeric filters in the panel
  const excludedKeys = new Set([
    // Already displayed in the leaderboard table (user can filter via AG Grid)
    'season', 'age', 'mp',
    'offensive_fit', 'defensive_fit',
    'impact_score', 'o_lebron', 'd_lebron', 'war', 'vorp', 'ws_per_48',
    'talent_score', 'obpm', 'dbpm', 'team_fit',
    'usg_pct', 'ts_pct', 'per',
    // On/off metrics
    'on_court_plus_minus', 'on_off_plus_minus', 'on_off_rtg', 'on_def_rtg',
    // Shooting percentages (not wanted in panel)
    'fg_pct', 'fg3_pct', 'fg2_pct', 'efg_pct'
  ])

  // All numeric columns available – we will filter out excludedKeys
  const allNumericFilters = [
    // Core (but season/age/mp are excluded)
    { key: 'season', label: 'Season' },
    { key: 'age', label: 'Age' },
    { key: 'mp', label: 'Minutes' },
    // Shooting efficiency (fg_pct, fg3_pct, fg2_pct, efg_pct are excluded)
    { key: 'fg_pct', label: 'FG%' },
    { key: 'fg3_pct', label: '3P%' },
    { key: 'fg2_pct', label: '2P%' },
    { key: 'efg_pct', label: 'eFG%' },
    { key: 'ts_pct', label: 'TS%' },
    { key: 'ft_pct', label: 'FT%' },
    { key: 'ftr', label: 'FTr' },
    { key: 'three_par', label: '3PAr' },
    // Zone shooting
    { key: 'at_rim_fga', label: 'At Rim FGA' },
    { key: 'at_rim_accuracy', label: 'At Rim Acc.' },
    { key: 'short_mid_range_fga', label: 'Short Mid FGA' },
    { key: 'short_mid_range_accuracy', label: 'Short Mid Acc.' },
    { key: 'long_mid_range_fga', label: 'Long Mid FGA' },
    { key: 'long_mid_range_accuracy', label: 'Long Mid Acc.' },
    { key: 'corner3_fga', label: 'Corner3 FGA' },
    { key: 'corner3_accuracy', label: 'Corner3 Acc.' },
    { key: 'arc3_fga', label: 'Arc3 FGA' },
    { key: 'arc3_accuracy', label: 'Arc3 Acc.' },
    // Advanced percentages
    { key: 'orb_pct', label: 'ORB%' },
    { key: 'drb_pct', label: 'DRB%' },
    { key: 'trb_pct', label: 'TRB%' },
    { key: 'ast_pct', label: 'AST%' },
    { key: 'stl_pct', label: 'STL%' },
    { key: 'blk_pct', label: 'BLK%' },
    { key: 'tov_pct', label: 'TOV%' },
    // Advanced impact (some excluded like per, ws_per_48, obpm, dbpm, vorp, war, o_lebron, d_lebron, but we keep others)
    { key: 'per', label: 'PER' },
    { key: 'ws_per_48', label: 'WS/48' },
    { key: 'ows', label: 'OWS' },
    { key: 'dws', label: 'DWS' },
    { key: 'bpm', label: 'BPM' },
    { key: 'obpm', label: 'OBPM' },
    { key: 'dbpm', label: 'DBPM' },
    { key: 'vorp', label: 'VORP' },
    { key: 'war', label: 'WAR' },
    { key: 'lebron', label: 'LEBRON' },
    { key: 'o_lebron', label: 'O-LEBRON' },
    { key: 'd_lebron', label: 'D-LEBRON' },
    // Position estimates
    { key: 'pos_estimate_pg', label: 'PG%' },
    { key: 'pos_estimate_sg', label: 'SG%' },
    { key: 'pos_estimate_sf', label: 'SF%' },
    { key: 'pos_estimate_pf', label: 'PF%' },
    { key: 'pos_estimate_c', label: 'C%' },
    // On/off metrics (excluded)
    { key: 'on_court_plus_minus', label: 'OnCourt +/-' },
    { key: 'on_off_plus_minus', label: 'On/Off +/-' },
    { key: 'on_off_rtg', label: 'On/Off Rating' },
    { key: 'on_def_rtg', label: 'On Def. Rating' },
    // Derived (already in table – excluded)
    { key: 'impact_score', label: 'Impact Score' },
    { key: 'talent_score', label: 'Talent Score' },
    { key: 'team_fit', label: 'Team Fit' },
    { key: 'offensive_fit', label: 'Offensive Fit' },
    { key: 'defensive_fit', label: 'Defensive Fit' },
  ]

  // Filter out excluded keys
  const numericFilters = allNumericFilters.filter(item => !excludedKeys.has(item.key))

  const handleNumericChange = (key, minVal, maxVal) => {
    setFilters(prev => ({
      ...prev,
      [key]: { min: minVal, max: maxVal }
    }))
  }

  const handleRoleToggle = (type, role) => {
    const current = filters[type] || []
    if (current.includes(role)) {
      setFilters(prev => ({
        ...prev,
        [type]: current.filter(r => r !== role)
      }))
    } else {
      setFilters(prev => ({
        ...prev,
        [type]: [...current, role]
      }))
    }
  }

  const handleRoleExclusive = (type, role) => {
    if (filters[`${type}_exclusive`] === role) {
      setFilters(prev => {
        const newFilters = { ...prev }
        delete newFilters[`${type}_exclusive`]
        return newFilters
      })
    } else {
      setFilters(prev => ({
        ...prev,
        [`${type}_exclusive`]: role
      }))
    }
  }

  const applyFilters = () => {
    onFilter(filters)
  }

  const resetFilters = () => {
    setFilters({})
    onFilter({})
  }

  return (
    <div
      className={`fixed top-0 left-0 h-full w-96 bg-surface border-r border-border transition-transform duration-300 ease-in-out z-50 overflow-y-auto p-6 ${isOpen ? 'translate-x-0' : '-translate-x-full'}`}
    >
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-textPrimary">Filters</h2>
        <button onClick={onClose} className="text-textSecondary hover:text-textPrimary text-2xl">&times;</button>
      </div>

      {/* Role Filters */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2 text-textPrimary">Offensive Role</h3>
        <div className="space-y-1">
          {roleOptions.offensive.map(role => (
            <div key={role} className="flex items-center justify-between">
              <label className="flex items-center space-x-2 text-textSecondary">
                <input
                  type="checkbox"
                  checked={(filters.offensive || []).includes(role)}
                  onChange={() => handleRoleToggle('offensive', role)}
                  className="accent-primary"
                />
                <span>{role}</span>
              </label>
              <button
                onClick={() => handleRoleExclusive('offensive', role)}
                className={`text-xs px-2 py-1 rounded ${filters.offensive_exclusive === role ? 'bg-primary text-white' : 'bg-surfaceLight text-textSecondary hover:text-textPrimary'}`}
              >
                Exclusive
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2 text-textPrimary">Defensive Role</h3>
        <div className="space-y-1">
          {roleOptions.defensive.map(role => (
            <div key={role} className="flex items-center justify-between">
              <label className="flex items-center space-x-2 text-textSecondary">
                <input
                  type="checkbox"
                  checked={(filters.defensive || []).includes(role)}
                  onChange={() => handleRoleToggle('defensive', role)}
                  className="accent-primary"
                />
                <span>{role}</span>
              </label>
              <button
                onClick={() => handleRoleExclusive('defensive', role)}
                className={`text-xs px-2 py-1 rounded ${filters.defensive_exclusive === role ? 'bg-primary text-white' : 'bg-surfaceLight text-textSecondary hover:text-textPrimary'}`}
              >
                Exclusive
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Numeric Filters – only columns NOT in excludedKeys */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2 text-textPrimary">Numeric Ranges</h3>
        <p className="text-textSecondary text-sm mb-3">Filter by stats not shown in the table</p>
        {numericFilters.map(({ key, label }) => {
          const current = filters[key] || { min: '', max: '' }
          return (
            <div key={key} className="mb-3">
              <label className="text-textSecondary text-sm block mb-1">{label}</label>
              <div className="flex space-x-2">
                <input
                  type="number"
                  placeholder="Min"
                  value={current.min}
                  onChange={(e) => handleNumericChange(key, e.target.value, current.max)}
                  className="w-1/2 bg-surfaceLight border border-border rounded px-2 py-1 text-textPrimary text-sm"
                  step="any"
                />
                <input
                  type="number"
                  placeholder="Max"
                  value={current.max}
                  onChange={(e) => handleNumericChange(key, current.min, e.target.value)}
                  className="w-1/2 bg-surfaceLight border border-border rounded px-2 py-1 text-textPrimary text-sm"
                  step="any"
                />
              </div>
            </div>
          )
        })}
      </div>

      {/* Buttons */}
      <div className="flex space-x-4">
        <button onClick={applyFilters} className="btn-primary flex-1">Apply Filters</button>
        <button onClick={resetFilters} className="bg-surfaceLight hover:bg-border text-textPrimary px-4 py-2 rounded-lg transition-colors">Reset</button>
      </div>
    </div>
  )
}

export default FilterPanel