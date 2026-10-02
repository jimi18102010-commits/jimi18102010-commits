import { useCallback, useRef, useState, useEffect } from 'react';

// A simple ~1200Hz 8ms sine wave pop
export function useAudioHaptic() {
  const audioCtxRef = useRef<AudioContext | null>(null);
  const [isMuted, setIsMuted] = useState(false);

  useEffect(() => {
    // Only initialize on user interaction later if needed, but we can set up the context
    if (!audioCtxRef.current) {
      try {
        const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
        if (AudioContextClass) {
          audioCtxRef.current = new AudioContextClass();
        }
      } catch (e) {
        console.error("AudioContext not supported", e);
      }
    }

    return () => {
      if (audioCtxRef.current && audioCtxRef.current.state !== 'closed') {
        audioCtxRef.current.close();
      }
    };
  }, []);

  const playHaptic = useCallback(() => {
    if (isMuted || !audioCtxRef.current) return;

    try {
      if (audioCtxRef.current.state === 'suspended') {
        audioCtxRef.current.resume();
      }

      const ctx = audioCtxRef.current;
      const osc = ctx.createOscillator();
      const gainNode = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(1200, ctx.currentTime);
      // slight drop in frequency for a more 'clicky' feel
      osc.frequency.exponentialRampToValueAtTime(100, ctx.currentTime + 0.01);

      // quick attack and release
      gainNode.gain.setValueAtTime(0, ctx.currentTime);
      gainNode.gain.linearRampToValueAtTime(0.1, ctx.currentTime + 0.001);
      gainNode.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.008);

      osc.connect(gainNode);
      gainNode.connect(ctx.destination);

      osc.start(ctx.currentTime);
      osc.stop(ctx.currentTime + 0.01);
    } catch (e) {
      console.warn("Failed to play haptic sound", e);
    }
  }, [isMuted]);

  const toggleMute = useCallback(() => {
    setIsMuted(prev => !prev);
  }, []);

  return { playHaptic, isMuted, toggleMute };
}
