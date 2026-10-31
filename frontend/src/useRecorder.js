import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from './api.js'

const MAX_SECONDS = 60

export function useRecorder(onText) {
  const [state, setState] = useState('idle') // idle | recording | transcribing
  const [error, setError] = useState('')
  const recorderRef = useRef(null)
  const streamRef = useRef(null)
  const chunksRef = useRef([])
  const timerRef = useRef(null)
  const cancelledRef = useRef(false)
  const onTextRef = useRef(onText)
  onTextRef.current = onText

  const releaseMic = useCallback(() => {
    clearTimeout(timerRef.current)
    streamRef.current?.getTracks().forEach((t) => t.stop()) // turns the mic indicator off
    streamRef.current = null
  }, [])

  const stop = useCallback(() => {
    if (recorderRef.current && recorderRef.current.state === 'recording') {
      recorderRef.current.stop()
    }
  }, [])

  const start = useCallback(async () => {
    setError('')
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
      setError('Voice input is not supported in this browser.')
      return
    }
    let stream
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    } catch (e) {
      setError(
        e.name === 'NotAllowedError'
          ? 'Microphone access was denied.'
          : e.name === 'NotFoundError'
            ? 'No microphone was found.'
            : 'Could not access the microphone.',
      )
      return
    }

    streamRef.current = stream
    chunksRef.current = []
    const recorder = new MediaRecorder(stream)
    recorderRef.current = recorder
    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data)
    }
    recorder.onstop = async () => {
      releaseMic()
      if (cancelledRef.current) return
      const blob = new Blob(chunksRef.current, { type: recorder.mimeType })
      if (blob.size === 0) {
        setState('idle')
        setError('No audio was recorded.')
        return
      }
      setState('transcribing')
      try {
        const { text } = await api.transcribe(blob)
        if (text) onTextRef.current(text)
        else setError('No speech was detected.')
      } catch (e) {
        setError(e.message)
      } finally {
        setState('idle')
      }
    }

    recorder.start()
    setState('recording')
    timerRef.current = setTimeout(stop, MAX_SECONDS * 1000) // automatic stop
  }, [releaseMic, stop])

  const toggle = useCallback(() => {
    if (state === 'recording') stop()
    else if (state === 'idle') start()
  }, [state, start, stop])

  // leaving the page: stop recording and release the mic, without sending anything
  useEffect(() => {
    cancelledRef.current = false
    return () => {
      cancelledRef.current = true
      if (recorderRef.current && recorderRef.current.state === 'recording') {
        recorderRef.current.stop()
      }
      releaseMic()
    }
  }, [releaseMic])

  return { state, error, toggle }
}