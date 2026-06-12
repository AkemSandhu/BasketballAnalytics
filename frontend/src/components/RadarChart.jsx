import { Radar, RadarChart as RechartsRadar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts'

const RadarChart = ({ data }) => {
  const chartData = Object.entries(data).map(([skill, tier]) => ({
    skill,
    value: tier === 'Diamond' ? 100 : tier === 'Gold' ? 80 : tier === 'Silver' ? 60 : tier === 'Bronze' ? 40 : 20,
    fullMark: 100,
  }))
  return (
    <ResponsiveContainer width="100%" height={300}>
      <RechartsRadar data={chartData}>
        <PolarGrid stroke="#2a2a35" />
        <PolarAngleAxis dataKey="skill" stroke="#a0a0b0" tick={{ fontSize: 10 }} />
        <PolarRadiusAxis domain={[0, 100]} stroke="#2a2a35" />
        <Tooltip />
        <Radar name="Badge Tier" dataKey="value" stroke="#2b6ef0" fill="#2b6ef0" fillOpacity={0.6} />
      </RechartsRadar>
    </ResponsiveContainer>
  )
}
export default RadarChart