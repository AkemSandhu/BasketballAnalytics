import { useState, useEffect, useRef } from 'react'
import { AgGridReact } from 'ag-grid-react'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'
import { getAllPlayerSeasons } from '../api/client'
import FilterPanel from '../components/FilterPanel'
import PlayerProfileCard from '../components/PlayerProfileCard'

const Leaderboard = () => {
  const [allData, setAllData] = useState([])
  const [filteredData, setFilteredData] = useState([])
  const [loading, setLoading] = useState(true)
  const [isFilterOpen, setIsFilterOpen] = useState(false)
  const [selectedRows, setSelectedRows] = useState([])
  const [showProfile, setShowProfile] = useState(false)
  const [globalTab, setGlobalTab] = useState(0)
  const totalTabs = 6 // Main, Line Chart, Badges, Radar, Shot Chart

  const columnApiRef = useRef(null)
  const gridApiRef = useRef(null)

  const [groupStates, setGroupStates] = useState({
    PLAYER: { isOpen: true, childColIds: ['season', 'age', 'mp'], headerName: 'PLAYER' },
    ROLES: { isOpen: true, childColIds: ['offensive_fit', 'defensive_role', 'defensive_fit'], headerName: 'ROLES' },
    IMPACT: { isOpen: true, childColIds: ['o_lebron', 'd_lebron', 'war', 'vorp', 'ws_per_48'], headerName: 'IMPACT' },
    TALENT: { isOpen: true, childColIds: ['obpm', 'dbpm', 'team_fit'], headerName: 'TALENT' },
    PRODUCTION: { isOpen: true, childColIds: ['ts_pct', 'per'], headerName: 'PRODUCTION' },
  })

  const baseColumnDefs = [
    {
      field: 'selection',
      headerName: '',
      width: 50,
      pinned: 'left',
      checkboxSelection: true,
      headerCheckboxSelection: true,
      sortable: false,
      filter: false,
      resizable: false,
    },
    {
      headerName: 'PLAYER',
      groupId: 'PLAYER',
      children: [
        { field: 'player_name', headerName: 'Player', width: 180, pinned: 'left' },
        { field: 'season', width: 90, sortable: true, filter: true },
        { field: 'age', width: 70 },
        { field: 'mp', headerName: 'MIN', width: 80 },
      ]
    },
    {
      headerName: 'ROLES',
      groupId: 'ROLES',
      children: [
        { field: 'offensive_role', headerName: 'Off. Role', width: 140 },
        { field: 'offensive_fit', headerName: 'Off. Fit', width: 100, type: 'numericColumn' },
        { field: 'defensive_role', headerName: 'Def. Role', width: 140 },
        { field: 'defensive_fit', headerName: 'Def. Fit', width: 100, type: 'numericColumn' },
      ]
    },
    {
      headerName: 'IMPACT',
      groupId: 'IMPACT',
      children: [
        { field: 'impact_score', headerName: 'Impact Score', width: 120, type: 'numericColumn', sort: 'desc' },
        { field: 'o_lebron', headerName: 'O-LEBRON', width: 110, type: 'numericColumn' },
        { field: 'd_lebron', headerName: 'D-LEBRON', width: 110, type: 'numericColumn' },
        { field: 'war', width: 90, type: 'numericColumn' },
        { field: 'vorp', width: 90, type: 'numericColumn' },
        { field: 'ws_per_48', headerName: 'WS/48', width: 100, type: 'numericColumn' },
      ]
    },
    {
      headerName: 'TALENT',
      groupId: 'TALENT',
      children: [
        { field: 'talent_score', headerName: 'Talent Score', width: 120, type: 'numericColumn' },
        { field: 'obpm', headerName: 'OBPM', width: 90, type: 'numericColumn' },
        { field: 'dbpm', headerName: 'DBPM', width: 90, type: 'numericColumn' },
        { field: 'team_fit', headerName: 'Team Fit', width: 100, type: 'numericColumn' },
      ]
    },
    {
      headerName: 'PRODUCTION',
      groupId: 'PRODUCTION',
      children: [
        { field: 'usg_pct', headerName: 'USG%', width: 90, type: 'numericColumn', valueFormatter: ({ value }) => value?.toFixed(1) },
        { field: 'ts_pct', headerName: 'TS%', width: 90, type: 'numericColumn', valueFormatter: ({ value }) => value?.toFixed(1) },
        { field: 'per', width: 80, type: 'numericColumn', valueFormatter: ({ value }) => value?.toFixed(1) },
      ]
    }
  ]

  const [columnDefs, setColumnDefs] = useState(() => {
    return baseColumnDefs.map(group => {
      const state = groupStates[group.groupId]
      if (!state) return group
      const arrow = state.isOpen ? '▼' : '►'
      return {
        ...group,
        headerName: `${arrow} ${state.headerName}`
      }
    })
  })

  const defaultColDef = {
    sortable: true,
    resizable: true,
    filter: true,
  }

  const onGridReady = (params) => {
    columnApiRef.current = params.columnApi
    gridApiRef.current = params.api
    Object.values(groupStates).forEach(g => {
      g.childColIds.forEach(colId => {
        params.columnApi.setColumnsVisible([colId], true)
      })
    })
  }

  const onColumnHeaderClicked = (params) => {
    const columnApi = columnApiRef.current
    if (!columnApi) return

    const colDef = params.column.getColDef()
    const groupId = colDef.groupId
    if (!groupId || !groupStates[groupId]) return

    const group = groupStates[groupId]
    const newIsOpen = !group.isOpen

    setGroupStates(prev => ({
      ...prev,
      [groupId]: { ...group, isOpen: newIsOpen }
    }))

    group.childColIds.forEach(colId => {
      const col = columnApi.getColumn(colId)
      if (col) {
        columnApi.setColumnsVisible([colId], newIsOpen)
      }
    })

    setColumnDefs(prev => {
      return prev.map(g => {
        if (g.groupId === groupId) {
          const arrow = newIsOpen ? '▼' : '►'
          return {
            ...g,
            headerName: `${arrow} ${group.headerName}`
          }
        }
        return g
      })
    })
  }

  const onSelectionChanged = (params) => {
    const selectedNodes = params.api.getSelectedNodes()
    const selectedData = selectedNodes.map(node => node.data)
    setSelectedRows(selectedData)
  }

  const handleViewProfile = () => {
    setGlobalTab(0)
    setShowProfile(true)
  }

  const closeProfile = () => {
    setShowProfile(false)
  }

  const handlePrevTab = () => setGlobalTab(prev => Math.max(0, prev - 1))
  const handleNextTab = () => setGlobalTab(prev => Math.min(totalTabs - 1, prev + 1))

  const handleFilter = (filters) => {
    if (!filters || Object.keys(filters).length === 0) {
      setFilteredData(allData)
      return
    }

    let filtered = allData

    if (filters.offensive && filters.offensive.length > 0) {
      const exclusive = filters.offensive_exclusive
      if (exclusive) {
        filtered = filtered.filter(row => row.offensive_role === exclusive)
      } else {
        filtered = filtered.filter(row => filters.offensive.includes(row.offensive_role))
      }
    }

    if (filters.defensive && filters.defensive.length > 0) {
      const exclusive = filters.defensive_exclusive
      if (exclusive) {
        filtered = filtered.filter(row => row.defensive_role === exclusive)
      } else {
        filtered = filtered.filter(row => filters.defensive.includes(row.defensive_role))
      }
    }

    const numericKeys = ['season', 'age', 'impact_score', 'talent_score', 'team_fit', 'offensive_fit', 'defensive_fit', 'usg_pct', 'ts_pct', 'per', 'obpm', 'dbpm', 'vorp', 'war', 'ws_per_48', 'mp']
    numericKeys.forEach(key => {
      const range = filters[key]
      if (range) {
        const min = parseFloat(range.min)
        const max = parseFloat(range.max)
        if (!isNaN(min)) {
          filtered = filtered.filter(row => row[key] >= min)
        }
        if (!isNaN(max)) {
          filtered = filtered.filter(row => row[key] <= max)
        }
      }
    })

    setFilteredData(filtered)
  }

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const res = await getAllPlayerSeasons(5000, 0)
        setAllData(res.data.items)
        setFilteredData(res.data.items)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  return (
    <>
      <div className="relative">
        <div className="mb-4 flex justify-between items-center">
          <button
            onClick={() => setIsFilterOpen(true)}
            className="btn-primary flex items-center space-x-2"
          >
            <span>Filters</span>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
          </button>
          {selectedRows.length > 0 && (
            <button
              onClick={handleViewProfile}
              className="btn-primary flex items-center space-x-2 bg-secondary hover:bg-secondaryDark"
            >
              <span>View Profile ({selectedRows.length})</span>
            </button>
          )}
        </div>

        <div className="ag-theme-alpine-dark" style={{ height: '80vh', width: '100%' }}>
          <AgGridReact
            rowData={filteredData}
            columnDefs={columnDefs}
            defaultColDef={defaultColDef}
            animateRows={true}
            pagination={true}
            paginationPageSize={25}
            loading={loading}
            onGridReady={onGridReady}
            onColumnHeaderClicked={onColumnHeaderClicked}
            rowSelection="multiple"
            onSelectionChanged={onSelectionChanged}
            suppressRowClickSelection={false}
          />
        </div>
      </div>

      {showProfile && (
        <div className="fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center p-4 overflow-auto">
          <div className="bg-surface rounded-xl border border-border w-full max-w-7xl max-h-[90vh] overflow-y-auto p-6 relative">
            {/* Close button moved to the right */}
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">Player Profile Comparison</h2>
              <div className="flex items-center space-x-4">
                <button
                  onClick={handlePrevTab}
                  className="text-textSecondary hover:text-textPrimary p-2 rounded hover:bg-surface transition"
                >
                  &#8249;
                </button>
                <span className="text-textSecondary text-sm">
                  Tab {globalTab + 1} of {totalTabs}
                </span>
                <button
                  onClick={handleNextTab}
                  className="text-textSecondary hover:text-textPrimary p-2 rounded hover:bg-surface transition"
                >
                  &#8250;
                </button>
                <button
                  onClick={closeProfile}
                  className="text-textSecondary hover:text-textPrimary text-2xl ml-2"
                >
                  &times;
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {selectedRows.map((row, idx) => (
                <PlayerProfileCard
                  key={idx}
                  playerData={row}
                  allData={allData}
                  globalTab={globalTab}
                />
              ))}
            </div>
          </div>
        </div>
      )}

      <FilterPanel
        isOpen={isFilterOpen}
        onClose={() => setIsFilterOpen(false)}
        rowData={allData}
        onFilter={handleFilter}
      />
    </>
  )
}

export default Leaderboard