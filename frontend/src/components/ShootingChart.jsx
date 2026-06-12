import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const ShootingChart = ({ data }) => {
  const zones = [
    { name: 'At Rim', accuracy: data.at_rim_accuracy, fga: data.at_rim_fga },
    { name: 'Short Mid', accuracy: data.short_mid_range_accuracy, fga: data.short_mid_range_fga },
    { name: 'Long Mid', accuracy: data.long_mid_range_accuracy, fga: data.long_mid_range_fga },
    { name: 'Corner 3', accuracy: data.corner3_accuracy, fga: data.corner3_fga },
    { name: 'Arc 3', accuracy: data.arc3_accuracy, fga: data.arc3_fga },
  ]
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={zones} layout="vertical" margin={{ left: 60 }}>
        <XAxis type="number" domain={[0,100]} stroke="#a0a0b0" />
        <YAxis type="category" dataKey="name" stroke="#a0a0b0" />
        <Tooltip formatter={(value) => `${value?.toFixed(1)}%`} />
        <Bar dataKey="accuracy" fill="#10b981" radius={[0,4,4,0]}>
          {zones.map((_, idx) => <Cell key={idx} fill={idx === 4 ? '#2b6ef0' : '#10b981'} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
export default ShootingChart