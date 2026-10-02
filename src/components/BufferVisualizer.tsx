

import { useEffect, useRef, useState } from 'react';
import { Play, Square } from 'lucide-react';

interface BufferVisualizerProps {
  playHaptic: () => void;
}

export function BufferVisualizer({ playHaptic }: BufferVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isRunning, setIsRunning] = useState(true);
  const [latency, setLatency] = useState('0.78');
  const [jitter, setJitter] = useState('0.03');

  const animationRef = useRef<number>(0);
  const packetsRef = useRef<Array<{x: number, speed: number, alpha: number}>>([]);
  const isHoveredRef = useRef<boolean>(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Handle resize
    const resize = () => {
      const parent = canvas.parentElement;
      if (parent) {
        // High DPI canvas
        const dpr = window.devicePixelRatio || 1;
        canvas.width = parent.clientWidth * dpr;
        canvas.height = 200 * dpr;
        ctx.scale(dpr, dpr);
        canvas.style.width = `${parent.clientWidth}px`;
        canvas.style.height = '200px';
      }
    };

    resize();
    window.addEventListener('resize', resize);

    // Init packets
    for (let i = 0; i < 20; i++) {
      packetsRef.current.push({
        x: Math.random() * (canvas.width / (window.devicePixelRatio || 1)),
        speed: 2 + Math.random() * 4,
        alpha: 0.2 + Math.random() * 0.8
      });
    }

    let lastTime = performance.now();

    const draw = (time: number) => {
      if (!isRunning) {
        animationRef.current = requestAnimationFrame(draw);
        return;
      }

      // Update telemetry sporadically
      if (time - lastTime > 200) {
        setLatency((0.75 + Math.random() * 0.08).toFixed(2));
        setJitter((0.02 + Math.random() * 0.02).toFixed(2));
        lastTime = time;
      }

      const rect = canvas.getBoundingClientRect();
      const w = rect.width;
      const h = rect.height;

      // Clear with trail effect
      ctx.fillStyle = 'rgba(18, 21, 28, 0.2)'; // Graphite bg with low alpha
      ctx.fillRect(0, 0, w, h);

      // Draw buffer rings
      ctx.strokeStyle = '#262f3f'; // border-dark
      ctx.lineWidth = 1;

      const centerY = h / 2;

      ctx.beginPath();
      ctx.moveTo(0, centerY - 20);
      ctx.lineTo(w, centerY - 20);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(0, centerY + 20);
      ctx.lineTo(w, centerY + 20);
      ctx.stroke();

      // Draw packets
      packetsRef.current.forEach(p => {
        p.x += p.speed * (isHoveredRef.current ? 0.3 : 1); // slow down on hover
        if (p.x > w) {
          p.x = -10;
          p.speed = 2 + Math.random() * 5;
        }

        ctx.fillStyle = `rgba(56, 189, 248, ${p.alpha})`; // Accent cyan
        ctx.fillRect(p.x, centerY - 15, 4, 30);
      });

      // Draw filter hook node
      const hookX = w * 0.7;
      ctx.fillStyle = '#10b981'; // Accent green
      ctx.beginPath();
      ctx.arc(hookX, centerY, 6, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = 'rgba(16, 185, 129, 0.4)';
      ctx.beginPath();
      ctx.arc(hookX, centerY, 14 + Math.sin(time / 200) * 4, 0, Math.PI * 2);
      ctx.stroke();

      animationRef.current = requestAnimationFrame(draw);
    };

    animationRef.current = requestAnimationFrame(draw);

    return () => {
      window.removeEventListener('resize', resize);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [isRunning]);

  const toggleRun = () => {
    playHaptic();
    setIsRunning(!isRunning);
  };

  return (
    <div className="my-12 border border-border-dark rounded-lg overflow-hidden bg-surface relative">
      <div className="flex items-center justify-between px-4 py-2 border-b border-border-dark bg-graphite/50">
        <div className="flex items-center gap-4 text-xs font-mono">
          <span className="text-text-secondary">vortex_filter_obj</span>
          <div className="flex gap-3">
            <span className="text-accent-cyan">LATENCY: {latency}µs</span>
            <span className="text-text-secondary">JITTER: ±{jitter}µs</span>
            <span className="text-accent-green">FILTER: PASS</span>
          </div>
        </div>
        <button
          onClick={toggleRun}
          className="p-1 text-text-secondary hover:text-text-primary transition-colors"
          title={isRunning ? "Pause Engine" : "Resume Engine"}
        >
          {isRunning ? <Square size={14} /> : <Play size={14} />}
        </button>
      </div>
      <div className="w-full relative h-[200px] bg-graphite">
        <canvas
          ref={canvasRef}
          className="absolute inset-0 block cursor-crosshair"
          onMouseEnter={() => {
            isHoveredRef.current = true;
            playHaptic();
          }}
          onMouseLeave={() => { isHoveredRef.current = false; }}
        />
        {!isRunning && (
          <div className="absolute inset-0 flex items-center justify-center bg-graphite/50 backdrop-blur-sm">
            <span className="font-mono text-text-secondary text-sm">ENGINE_PAUSED</span>
          </div>
        )}
      </div>
    </div>
  );
}
