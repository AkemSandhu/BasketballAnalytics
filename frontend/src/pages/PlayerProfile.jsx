import { useParams } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { getPlayerSeasons, getPlayerSeason, getRadarData, getTimeline, getSimilar } from '../api/client'
import RadarChart from '../components/RadarChart'
import ShootingChart from '../components/ShootingChart'
import SimilarPlayers from '../components/SimilarPlayers'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const PlayerProfile = () => {
  const { playerId } = useParams()
  const [seasons, setSeasons] = useState([])
  const [selectedSeason, setSelectedSeason] = useState(null)
  const [seasonData, setSeasonData] = useState(null)
  const [radarData, setRadarData] = useState(null)
  const [timeline, setTimeline] = useState([])
  const [similar, setSimilar] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchSeasons = async () => {
      try {
        const res = await getPlayerSeasons(playerId)
        const seasonList = res.data.map(ps => ({ id: ps.season_id, year: ps.year }))
        setSeasons(seasonList)
        if (seasonList.length > 0) {
          const latest = seasonList[seasonList.length-1].id
          setSelectedSeason(latest)
          await fetchSeasonData(latest)
          await fetchRadar(latest)
          await fetchSimilar(latest)
        }
        const timelineRes = await getTimeline(playerId)
        setTimeline(timelineRes.data)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetchSeasons()
  }, [playerId])

  const fetchSeasonData = async (seasonId) => {
    const res = await getPlayerSeason(playerId, seasonId)
    setSeasonData(res.data)
  }
  const fetchRadar = async (seasonId) => {
    const res = await getRadarData(playerId, seasonId)
    setRadarData(res.data)
  }
  const fetchSimilar = async (seasonId) => {
    const res = await getSimilar(playerId, seasonId)
    setSimilar(res.data)
  }

  const handleSeasonChange = (seasonId) => {
    setSelectedSeason(seasonId)
    fetchSeasonData(seasonId)
    fetchRadar(seasonId)
    fetchSimilar(seasonId)
  }

  if (loading) return <div className="text-center py-20">Loading player profile...</div>
  if (!seasonData) return <div className="text-center py-20">Player not found</div>

  return (
    <div className="space-y-8">
      <div className="card">
        <div className="flex justify-between items-start flex-wrap gap-4">
          <div>
            <h1 className="text-3xl font-bold">{seasonData.player_name}</h1>
            <p className="text-textSecondary">{seasonData.team} • {seasonData.pos} • Age {seasonData.age}</p>
          </div>
          <select value={selectedSeason} onChange={(e) => handleSeasonChange(Number(e.target.value))} className="bg-surfaceLight border border-border rounded px-3 py-2">
            {seasons.map(s => <option key={s.id} value={s.id}>{s.year}</option>)}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold mb-3">Impact Metrics</h2>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div><div className="text-3xl text-primary">{seasonData.impact_score?.toFixed(2)}</div><div className="text-textSecondary text-sm">Impact</div></div>
            <div><div className="text-3xl text-secondary">{seasonData.talent_score?.toFixed(2)}</div><div className="text-textSecondary text-sm">Talent</div></div>
            <div><div className="text-3xl text-accent">{seasonData.team_fit?.toFixed(2)}</div><div className="text-textSecondary text-sm">Team Fit</div></div>
          </div>
          <hr className="my-4 border-border" />
          <h2 className="text-xl font-semibold mb-3">Advanced Stats</h2>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>PER: {seasonData.per?.toFixed(1)}</div>
            <div>BPM: {seasonData.bpm?.toFixed(1)}</div>
            <div>LEBRON: {seasonData.lebron?.toFixed(2)}</div>
            <div>USG%: {seasonData.usg_pct?.toFixed(1)}%</div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-3">Skill Badges</h2>
          {radarData ? <RadarChart data={radarData} /> : <p className="text-textSecondary">No badge data</p>}
        </div>
      </div>

      <div className="card">
        <h2 className="text-xl font-semibold mb-3">Shooting Efficiency</h2>
        <ShootingChart data={seasonData} />
      </div>

      <div className="card">
        <h2 className="text-xl font-semibold mb-3">Career Trajectory</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={timeline}>
            <XAxis dataKey="season" stroke="#a0a0b0" />
            <YAxis stroke="#a0a0b0" />
            <Tooltip contentStyle={{ backgroundColor: '#14141c', borderColor: '#2a2a35' }} />
            <Line type="monotone" dataKey="impact_score" stroke="#2b6ef0" name="Impact" />
            <Line type="monotone" dataKey="talent_score" stroke="#10b981" name="Talent" />
            <Line type="monotone" dataKey="team_fit" stroke="#3b82f6" name="Team Fit" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h2 className="text-xl font-semibold mb-3">Similar Seasons</h2>
        <SimilarPlayers players={similar} />
      </div>
    </div>
  )
}

export default PlayerProfile