import { useFetch } from '../hooks/useApi'
import type { TodayResponse } from '../types/api'
import { MealCard } from '../components/MealCard'
import { Skeleton } from '../components/Skeleton'
import { Footprints, Moon, Dumbbell, Zap } from 'lucide-react'

// ── Calorie Arc ───────────────────────────────────────────────────────────────
function CalorieArc({ consumed, target }: { consumed: number; target: number }) {
  const pct = Math.min(consumed / target, 1)
  const remaining = Math.max(target - consumed, 0)
  const over = consumed > target

  // SVG arc math — full circle gauge
  const r = 52
  const circ = 2 * Math.PI * r
  const offset = circ * (1 - pct)
  const color = pct >= 1 ? '#EF4444' : pct >= 0.9 ? '#EAB308' : '#22C55E'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
      <div style={{ position: 'relative', width: 140, height: 140 }}>
        <svg width={140} height={140} style={{ transform: 'rotate(-90deg)' }}>
          <circle cx={70} cy={70} r={r} fill="none" stroke="#1e1e1e" strokeWidth={12} />
          <circle
            cx={70} cy={70} r={r} fill="none"
            stroke={color} strokeWidth={12}
            strokeLinecap="round"
            strokeDasharray={circ}
            strokeDashoffset={offset}
            style={{ transition: 'stroke-dashoffset 0.6s ease, stroke 0.3s ease' }}
          />
        </svg>
        <div style={{
          position: 'absolute', inset: 0,
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        }}>
          <span style={{ fontSize: 28, fontWeight: 900, color: '#F5F5F5', lineHeight: 1 }}>
            {consumed.toLocaleString()}
          </span>
          <span style={{ fontSize: 11, color: '#8A8A8A', marginTop: 2 }}>of {target.toLocaleString()}</span>
          <span style={{ fontSize: 10, color: '#8A8A8A' }}>kcal</span>
        </div>
      </div>
      <div style={{ display: 'flex', gap: 20, textAlign: 'center' }}>
        <div>
          <div style={{ fontSize: 15, fontWeight: 700, color: over ? '#EF4444' : '#22C55E' }}>
            {over ? `+${(consumed - target).toLocaleString()}` : remaining.toLocaleString()}
          </div>
          <div style={{ fontSize: 10, color: '#8A8A8A', fontWeight: 600, letterSpacing: '0.04em' }}>
            {over ? 'OVER' : 'LEFT'}
          </div>
        </div>
        <div style={{ width: 1, background: '#262626' }} />
        <div>
          <div style={{ fontSize: 15, fontWeight: 700, color: '#F5F5F5' }}>{target.toLocaleString()}</div>
          <div style={{ fontSize: 10, color: '#8A8A8A', fontWeight: 600, letterSpacing: '0.04em' }}>TARGET</div>
        </div>
      </div>
    </div>
  )
}

// ── Macro Row ─────────────────────────────────────────────────────────────────
function MacroRow({ label, consumed, target, color }: {
  label: string; consumed: number; target: number; color: string
}) {
  const pct = target > 0 ? Math.min((consumed / target) * 100, 100) : 0
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <span style={{ fontSize: 12, color: '#8A8A8A', fontWeight: 600, letterSpacing: '0.05em' }}>
          {label}
        </span>
        <span style={{ fontSize: 13, fontWeight: 700, color: '#F5F5F5' }}>
          {Math.round(consumed)}<span style={{ fontWeight: 400, color: '#8A8A8A' }}>/{target}g</span>
        </span>
      </div>
      <div style={{ height: 7, background: '#1e1e1e', borderRadius: 4, overflow: 'hidden' }}>
        <div style={{
          height: '100%', width: `${pct}%`, background: color,
          borderRadius: 4, transition: 'width 0.5s ease',
        }} />
      </div>
    </div>
  )
}

// ── Stat Box ──────────────────────────────────────────────────────────────────
function StatBox({ icon: Icon, value, label, color }: {
  icon: typeof Footprints; value: string; label: string; color: string
}) {
  return (
    <div style={{
      flex: 1, background: '#141414', border: '1px solid #262626',
      borderRadius: 14, padding: '14px 8px',
      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 5,
    }}>
      <Icon size={20} color={color} strokeWidth={1.8} />
      <span style={{ fontSize: 18, fontWeight: 800, color, lineHeight: 1 }}>{value}</span>
      <span style={{ fontSize: 9, fontWeight: 700, color: '#8A8A8A', letterSpacing: '0.06em' }}>{label}</span>
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export function Today() {
  const { data, loading, error } = useFetch<TodayResponse>('/api/v1/today')

  if (error) {
    return (
      <div style={{ padding: 16 }}>
        <div style={{
          background: '#141414', border: '1px solid #EF4444',
          borderRadius: 12, padding: 16, color: '#EF4444', fontSize: 14,
        }}>
          Could not load data — is the backend running?<br />
          <span style={{ color: '#8A8A8A', fontSize: 12 }}>{error}</span>
        </div>
      </div>
    )
  }

  if (loading || !data) {
    return (
      <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
        <Skeleton height={24} style={{ width: '40%' }} />
        <Skeleton height={220} />
        <Skeleton height={140} />
        <Skeleton height={100} />
        <Skeleton height={180} />
      </div>
    )
  }

  const { calories, macros, meals, steps, sleep_hrs, workout_done, day_number, day_type, protein_on_track } = data

  const dateLabel = new Date(data.date + 'T00:00:00').toLocaleDateString('en-IN', {
    weekday: 'long', day: 'numeric', month: 'short',
  })

  // Steps display
  const stepsVal = steps != null ? steps.toLocaleString() : '—'
  const stepsColor = steps == null ? '#8A8A8A' : steps >= 8000 ? '#22C55E' : '#EAB308'

  // Sleep display
  const sleepVal = sleep_hrs != null ? `${sleep_hrs}h` : '—'
  const sleepColor = sleep_hrs == null ? '#8A8A8A' : sleep_hrs >= 7 ? '#22C55E' : '#EF4444'

  // Workout display
  const workoutVal = workout_done == null ? '—' : workout_done ? 'Done' : 'Rest'
  const workoutColor = workout_done == null ? '#8A8A8A' : workout_done ? '#22C55E' : '#8A8A8A'

  return (
    <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 14 }}>

      {/* ── Header ── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div style={{ fontSize: 22, fontWeight: 800, color: '#F5F5F5' }}>
            Day {day_number}
            <span style={{ fontSize: 13, fontWeight: 500, color: '#8A8A8A', marginLeft: 6 }}>of 56</span>
          </div>
          <div style={{ fontSize: 13, color: '#8A8A8A', marginTop: 2 }}>{dateLabel}</div>
        </div>
        <span style={{
          fontSize: 11, fontWeight: 700, padding: '4px 10px', borderRadius: 8,
          background: day_type === 'training' ? 'rgba(34,197,94,0.12)' : 'rgba(138,138,138,0.1)',
          color: day_type === 'training' ? '#22C55E' : '#8A8A8A',
          border: `1px solid ${day_type === 'training' ? 'rgba(34,197,94,0.3)' : '#262626'}`,
          letterSpacing: '0.06em',
        }}>
          {day_type === 'training' ? 'TRAINING' : 'REST DAY'}
        </span>
      </div>

      {/* ── Calories (big card) ── */}
      <div style={{
        background: '#141414', border: '1px solid #262626', borderRadius: 16,
        padding: '20px 16px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4,
      }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: '#8A8A8A', letterSpacing: '0.08em', marginBottom: 8 }}>
          CALORIES TODAY
        </div>
        <CalorieArc consumed={calories.consumed_mid} target={calories.target} />
      </div>

      {/* ── Protein highlight ── */}
      <div style={{
        background: '#141414', border: `1px solid ${protein_on_track ? '#262626' : 'rgba(234,179,8,0.3)'}`,
        borderRadius: 14, padding: '14px 16px',
        display: 'flex', alignItems: 'center', gap: 12,
      }}>
        <Zap size={20} color={protein_on_track ? '#3B82F6' : '#EAB308'} strokeWidth={2} />
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
            <span style={{ fontSize: 13, fontWeight: 700, color: '#F5F5F5' }}>Protein</span>
            <span style={{ fontSize: 13, fontWeight: 700, color: '#3B82F6' }}>
              {Math.round(macros.protein_g)}g
              <span style={{ fontWeight: 400, color: '#8A8A8A' }}> / {macros.protein_target_g}g</span>
            </span>
          </div>
          <div style={{ height: 8, background: '#1e1e1e', borderRadius: 4, overflow: 'hidden' }}>
            <div style={{
              height: '100%',
              width: `${Math.min((macros.protein_g / macros.protein_target_g) * 100, 100)}%`,
              background: '#3B82F6', borderRadius: 4, transition: 'width 0.5s ease',
            }} />
          </div>
          {!protein_on_track && (
            <div style={{ fontSize: 11, color: '#EAB308', marginTop: 5 }}>
              Behind target — prioritise protein in your next meal
            </div>
          )}
        </div>
      </div>

      {/* ── Other macros ── */}
      <div style={{
        background: '#141414', border: '1px solid #262626', borderRadius: 14, padding: '14px 16px',
        display: 'flex', flexDirection: 'column', gap: 12,
      }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: '#8A8A8A', letterSpacing: '0.07em' }}>MACROS</div>
        <MacroRow label="CARBS" consumed={macros.carbs_g} target={200} color="#EAB308" />
        <MacroRow label="FATS" consumed={macros.fats_g} target={56} color="#A855F7" />
        <MacroRow label="FIBER" consumed={macros.fiber_g} target={25} color="#22C55E" />
      </div>

      {/* ── Activity stats ── */}
      <div style={{ display: 'flex', gap: 10 }}>
        <StatBox icon={Footprints} value={stepsVal} label="STEPS" color={stepsColor} />
        <StatBox icon={Moon} value={sleepVal} label="SLEEP" color={sleepColor} />
        <StatBox icon={Dumbbell} value={workoutVal} label="GYM" color={workoutColor} />
      </div>

      {/* ── Meals ── */}
      <div>
        <div style={{ fontSize: 11, fontWeight: 700, color: '#8A8A8A', letterSpacing: '0.07em', marginBottom: 10 }}>
          MEALS ({meals.length})
        </div>
        {meals.length === 0 ? (
          <div style={{
            background: '#141414', border: '1px solid #262626', borderRadius: 12,
            padding: 20, textAlign: 'center', color: '#8A8A8A', fontSize: 13,
          }}>
            No meals logged yet.<br />
            <span style={{ fontSize: 12 }}>Tell Nouri what you ate on Telegram.</span>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {meals.map((meal) => <MealCard key={meal.id} meal={meal} />)}
          </div>
        )}
      </div>

      {/* ── Agent notes ── */}
      {(data.summary?.coach_notes || data.summary?.nouri_notes) && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#8A8A8A', letterSpacing: '0.07em' }}>AGENT NOTES</div>
          {data.summary.coach_notes && (
            <div style={{ background: '#141414', border: '1px solid #262626', borderRadius: 12, padding: '12px 14px' }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: '#3B82F6', marginBottom: 4, letterSpacing: '0.05em' }}>
                IRON
              </div>
              <p style={{ fontSize: 13, color: '#8A8A8A', lineHeight: 1.5 }}>{data.summary.coach_notes}</p>
            </div>
          )}
          {data.summary.nouri_notes && (
            <div style={{ background: '#141414', border: '1px solid #262626', borderRadius: 12, padding: '12px 14px' }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: '#22C55E', marginBottom: 4, letterSpacing: '0.05em' }}>
                NOURI
              </div>
              <p style={{ fontSize: 13, color: '#8A8A8A', lineHeight: 1.5 }}>{data.summary.nouri_notes}</p>
            </div>
          )}
        </div>
      )}

      {/* bottom padding for nav bar */}
      <div style={{ height: 8 }} />
    </div>
  )
}
