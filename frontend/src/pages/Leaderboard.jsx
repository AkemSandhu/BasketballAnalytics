import { useState, useEffect } from 'react'
import { AgGridReact } from 'ag-grid-react'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'
import { getAllPlayerSeasons } from '../api/client'

const Leaderboard = () => {
  const [rowData, setRowData] = useState([])
  const [loading, setLoading] = useState(true)

  const columnDefs = [
    {
      headerName: 'Info',
      children: [
        { field: 'player_name', headerName: 'Player', width: 180, pinned: 'left' },
        { field: 'season', width: 90, sortable: true, filter: true },
        { field: 'age', width: 70 },
        { field: 'mp', headerName: 'MIN', width: 80 },
      ]
    },
    {
      headerName: 'Roles',
      children: [
        { field: 'offensive_role', headerName: 'Off. Role', width: 140 },
        { field: 'offensive_fit', headerName: 'Off. Fit', width: 100, type: 'numericColumn' },
        { field: 'defensive_role', headerName: 'Def. Role', width: 140 },
        { field: 'defensive_fit', headerName: 'Def. Fit', width: 100, type: 'numericColumn' },
      ]
    },
    {
      headerName: 'Impact',
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
      headerName: 'Talent',
      children: [
        { field: 'talent_score', headerName: 'Talent Score', width: 120, type: 'numericColumn' },
        { field: 'obpm', headerName: 'OBPM', width: 90, type: 'numericColumn' },
        { field: 'dbpm', headerName: 'DBPM', width: 90, type: 'numericColumn' },
        { field: 'team_fit', headerName: 'Team Fit', width: 100, type: 'numericColumn' },
      ]
    },
    {
      headerName: 'Production',
      children: [
        { field: 'usg_pct', headerName: 'USG%', width: 90, type: 'numericColumn', valueFormatter: ({ value }) => value?.toFixed(1) },
        { field: 'ts_pct', headerName: 'TS%', width: 90, type: 'numericColumn', valueFormatter: ({ value }) => value?.toFixed(1) },
        { field: 'per', width: 80, type: 'numericColumn', valueFormatter: ({ value }) => value?.toFixed(1) },
      ]
    }
  ]

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const res = await getAllPlayerSeasons(5000, 0)
        setRowData(res.data.items)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  return (
    <div className="ag-theme-alpine-dark" style={{ height: '80vh', width: '100%' }}>
      <AgGridReact
        rowData={rowData}
        columnDefs={columnDefs}
        defaultColDef={{ sortable: true, resizable: true, filter: true }}
        animateRows={true}
        pagination={true}
        paginationPageSize={25}
        loading={loading}
      />
    </div>
  )
}

export default Leaderboard