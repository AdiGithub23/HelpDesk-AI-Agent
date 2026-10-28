import { pretty } from '../utils.js'

export default function Badge({ value }) {
  return <span className={`badge badge-${value}`}>{pretty(value)}</span>
}