
import { useTashkentTime } from '../hooks/useTashkentTime';
import { Volume2, VolumeX } from 'lucide-react';

interface HeaderProps {
  isMuted: boolean;
  toggleMute: () => void;
  playHaptic: () => void;
}

export function Header({ isMuted, toggleMute, playHaptic }: HeaderProps) {
  const time = useTashkentTime();

  return (
    <header className="w-full border-b border-border-dark bg-graphite/90 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-6 py-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        {/* Status */}
        <div className="flex items-center gap-3">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-green opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-accent-green"></span>
          </span>
          <span className="text-xs font-mono text-text-secondary uppercase tracking-wider">
            Available for high-impact systems projects
          </span>
        </div>

        {/* Right side controls */}
        <div className="flex items-center gap-6">
          <div className="text-xs font-mono text-text-secondary">
            Tashkent, UZ · UTC+05:00 · <span className="text-text-primary">{time || '00:00:00'}</span>
          </div>

          <nav className="flex items-center gap-4 text-sm font-sans font-medium">
            <a href="#work" className="text-text-secondary hover:text-text-primary transition-colors">Work</a>
            <a href="#systems" className="text-text-secondary hover:text-text-primary transition-colors">Systems</a>
            <a href="#contact" className="text-text-secondary hover:text-text-primary transition-colors">Contact</a>
          </nav>

          <button
            onClick={() => {
              toggleMute();
              if (isMuted) playHaptic(); // Play after unmuting
            }}
            className="p-1.5 rounded-md hover:bg-surface text-text-secondary hover:text-text-primary transition-colors border border-transparent hover:border-border-dark"
            aria-label={isMuted ? "Unmute sounds" : "Mute sounds"}
          >
            {isMuted ? <VolumeX size={16} /> : <Volume2 size={16} />}
          </button>
        </div>
      </div>
    </header>
  );
}
