import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
} from 'recharts'

const tooltipStyle = {
  background: '#1a1a1a',
  border: '1px solid #262626',
  borderRadius: 8,
  color: '#F5F5F5',
  fontSize: 12,
}

const axisStyle = {
  fill: '#8A8A8A',
  fontSize: 11,
}

interface LineConfig {
  key: string
  color: string
  name: string
}

interface BarConfig {
  key: string
  color: string
  name: string
}

interface RefLine {
  key: string
  color: string
  label: string
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
interface TrendChartProps {
  data: any[]
  xKey: string
  lines?: LineConfig[]
  bars?: BarConfig[]
  referenceLine?: RefLine
  height?: number
}

export function TrendChart({ data, xKey, lines, bars, referenceLine, height = 180 }: TrendChartProps) {
  const formatted = data.map((d) => ({
    ...d,
    _label: String(d[xKey]).slice(5), // MM-DD from YYYY-MM-DD
  }))

  const refValue =
    referenceLine && formatted.length > 0
      ? (formatted[0][referenceLine.key] as number | undefined)
      : undefined

  if (bars && bars.length > 0) {
    return (
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={formatted} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e1e1e" vertical={false} />
          <XAxis dataKey="_label" tick={axisStyle} tickLine={false} axisLine={false} interval="preserveStartEnd" />
          <YAxis tick={axisStyle} tickLine={false} axisLine={false} />
          <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: '#8A8A8A' }} />
          {refValue != null && (
            <ReferenceLine
              y={refValue}
              stroke={referenceLine?.color ?? '#EF4444'}
              strokeDasharray="4 4"
              label={{ value: referenceLine?.label, fill: referenceLine?.color, fontSize: 10, position: 'insideTopRight' }}
            />
          )}
          {bars.map((b) => (
            <Bar key={b.key} dataKey={b.key} name={b.name} fill={b.color} radius={[3, 3, 0, 0]} maxBarSize={20} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={formatted} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e1e1e" vertical={false} />
        <XAxis dataKey="_label" tick={axisStyle} tickLine={false} axisLine={false} interval="preserveStartEnd" />
        <YAxis tick={axisStyle} tickLine={false} axisLine={false} domain={['auto', 'auto']} />
        <Tooltip contentStyle={tooltipStyle} labelStyle={{ color: '#8A8A8A' }} />
        {lines?.map((l) => (
          <Line
            key={l.key}
            type="monotone"
            dataKey={l.key}
            name={l.name}
            stroke={l.color}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
            connectNulls
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
