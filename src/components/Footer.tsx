
import { Github, Send } from 'lucide-react';

export function Footer() {
  const currentYear = 2024; // Static to satisfy strict purity linting

  return (
    <footer className="w-full border-t border-border-dark mt-24" id="contact">
      <div className="max-w-6xl mx-auto px-6 py-12 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex flex-col gap-2 text-sm text-text-secondary">
          <p className="font-mono">Jimmiy · Systems & Low-Latency Engineer</p>
          <p>© {currentYear} · Engineered for zero allocations</p>
        </div>

        <div className="flex items-center gap-4">
          <a
            href="https://t.me/jimmiy_dev"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md bg-surface border border-border-dark hover:border-text-secondary hover:text-text-primary transition-all text-text-secondary"
          >
            <Send size={16} />
            <span>@jimmiy_dev</span>
          </a>
          <a
            href="https://github.com/jimi18102010-commits"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md bg-surface border border-border-dark hover:border-text-secondary hover:text-text-primary transition-all text-text-secondary"
          >
            <Github size={16} />
            <span>GitHub</span>
          </a>
        </div>
      </div>
    </footer>
  );
}
