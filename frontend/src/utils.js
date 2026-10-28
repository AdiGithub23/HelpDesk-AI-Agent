export const STATUSES = ['open', 'in_progress', 'resolved', 'closed']
export const PRIORITIES = ['low', 'medium', 'high']

// Mirrors the backend transition table: from -> to -> roles allowed.
const TRANSITIONS = {
  open: { in_progress: ['agent'], closed: ['agent'] },
  in_progress: { resolved: ['agent'], closed: ['agent'] },
  resolved: { closed: ['employee', 'agent'], in_progress: ['employee', 'agent'] },
  closed: {},
}

export function allowedStatuses(current, role) {
  return Object.entries(TRANSITIONS[current] || {})
    .filter(([, roles]) => roles.includes(role))
    .map(([to]) => to)
}

export function statusActionLabel(from, to) {
  if (to === 'closed') return 'Close'
  if (from === 'resolved' && to === 'in_progress') return 'Reopen'
  if (to === 'in_progress') return 'Start work'
  if (to === 'resolved') return 'Mark resolved'
  return to
}

export const pretty = (value) => (value ? value.replace(/_/g, ' ') : '')
export const fmt = (iso) => (iso ? new Date(iso).toLocaleString() : '')


