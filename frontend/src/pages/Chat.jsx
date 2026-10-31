import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
import { ErrorMessage, Loading } from '../components/Feedback.jsx'
import { useLoad } from '../hooks.js'
import { fmt } from '../utils.js'
import { useRecorder } from '../useRecorder.js'

export default function Chat() {
  const sessions = useLoad(() => api.chatSessions({ limit: 50, offset: 0 }), [])
  const [selectedId, setSelectedId] = useState(null)
  const messages = useLoad(
    () => (selectedId ? api.chatMessages(selectedId) : Promise.resolve([])),
    [selectedId],
  )
  const [input, setInput] = useState('')
  const [pendingText, setPendingText] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef(null)

  const recorder = useRecorder((text) =>
    setInput((prev) => (prev ? prev.trimEnd() + ' ' : '') + text),
  )
  const voiceBusy = recorder.state !== 'idle'

  // open the most recent session when the list first loads
  useEffect(() => {
    if (selectedId === null && sessions.data && sessions.data.length > 0) {
      setSelectedId(sessions.data[0].id)
    }
  }, [sessions.data, selectedId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.data, pendingText])

  async function newChat() {
    setError('')
    try {
      const session = await api.createChat()
      setSelectedId(session.id)
      sessions.reload()
    } catch (e) {
      setError(e.message)
    }
  }

  async function send(e) {
    e.preventDefault()
    const text = input.trim()
    if (!text || !selectedId) return
    setSending(true)
    setPendingText(text)
    setInput('')
    setError('')
    try {
      await api.ask(selectedId, text)
    } catch (err) {
      setError(err.message)
      setInput(text) // nothing was saved, so let the user retry
    } finally {
      setPendingText('')
      setSending(false)
      messages.reload()
      sessions.reload()
    }
  }

  const list = messages.data || []

  return (
    <div className="chat">
      <aside className="chat-sessions">
        <button className="primary" onClick={newChat}>
          New chat
        </button>
        {sessions.loading && !sessions.data && <Loading />}
        {(sessions.data || []).map((s) => (
          <button
            key={s.id}
            className={`session ${s.id === selectedId ? 'active' : ''}`}
            onClick={() => setSelectedId(s.id)}
          >
            <span>{s.title || 'New chat'}</span>
            <small>{fmt(s.updated_at)}</small>
          </button>
        ))}
      </aside>

      <section className="chat-main">
        {!selectedId ? (
          <p className="muted">Start a new chat to ask the assistant a question.</p>
        ) : (
          <>
            <div className="chat-messages">
              {messages.loading && !messages.data && <Loading />}
              {messages.data && list.length === 0 && !pendingText && (
                <p className="muted">
                  Ask about company guides and policies, or about your own tickets.
                </p>
              )}
              {list.map((m) => (
                <div key={m.id} className={`msg msg-${m.role}`}>
                  <div className="prewrap">{m.content}</div>
                  {m.sources && m.sources.length > 0 && (
                    <div className="sources">
                      Sources:{' '}
                      {m.sources.map((s) => (
                        <Link key={s.article_id} to={`/articles/${s.article_id}`}>
                          {s.title}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              {pendingText && (
                <>
                  <div className="msg msg-user">
                    <div className="prewrap">{pendingText}</div>
                  </div>
                  <div className="msg msg-assistant muted">Thinking…</div>
                </>
              )}
              <div ref={bottomRef} />
            </div>
            <ErrorMessage message={error || messages.error || recorder.error} />
            <form className="chat-input" onSubmit={send}>
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type or speak your question…"
                maxLength={2000}
                disabled={sending || recorder.state === 'transcribing'}
              />
              <button
                type="button"
                className={`mic ${recorder.state === 'recording' ? 'recording' : ''}`}
                onClick={recorder.toggle}
                disabled={sending || recorder.state === 'transcribing'}
                title="Speak your question (click again to stop)"
              >
                {recorder.state === 'recording'
                  ? '■ Stop'
                  : recorder.state === 'transcribing'
                    ? 'Transcribing…'
                    : '🎤'}
              </button>
              <button className="primary" disabled={sending || voiceBusy || !input.trim()}>
                Send
              </button>
            </form>
          </>
        )}
      </section>
    </div>
  )
}
