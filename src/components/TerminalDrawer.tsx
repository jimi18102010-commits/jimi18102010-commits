import { useState } from 'react';
import { TerminalSquare, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface TerminalDrawerProps {
  playHaptic: () => void;
}

export function TerminalDrawer({ playHaptic }: TerminalDrawerProps) {
  const [isOpen, setIsOpen] = useState(false);

  const toggleDrawer = () => {
    playHaptic();
    setIsOpen(!isOpen);
  };

  return (
    <>
      <button
        onClick={toggleDrawer}
        className="fixed bottom-6 right-6 z-50 p-3 bg-surface border border-border-dark rounded-full text-text-secondary hover:text-accent-cyan transition-colors shadow-lg"
        title="Open Inspection Terminal"
      >
        <TerminalSquare size={20} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed bottom-0 left-0 right-0 z-50 h-80 bg-graphite border-t border-border-dark flex flex-col shadow-[0_-10px_40px_rgba(0,0,0,0.5)]"
          >
            <div className="flex items-center justify-between px-4 py-2 border-b border-border-dark bg-surface">
              <span className="text-xs font-mono text-text-secondary">root@tashkent-edge:~</span>
              <button onClick={toggleDrawer} className="text-text-secondary hover:text-text-primary p-1">
                <X size={14} />
              </button>
            </div>

            <div className="flex-1 p-4 font-mono text-xs overflow-y-auto">
              <div className="text-text-secondary mb-2">$ neofetch --stdout</div>
              <div className="text-text-primary mb-4">
                OS: Arch Linux x86_64<br/>
                Kernel: 6.8.0-custom-opt<br/>
                Uptime: 42 days, 13 hours<br/>
                Memory: 3192MiB / 32000MiB<br/>
              </div>

              <div className="text-text-secondary mb-2">$ sudo bpftool prog show</div>
              <div className="text-accent-cyan mb-4">
                42: xdp  name vortex_drop  tag a8b9c7d6e5f4<br/>
                &nbsp;&nbsp;&nbsp;&nbsp;loaded_at 2024-10-24T12:00:00+0000  uid 0<br/>
                &nbsp;&nbsp;&nbsp;&nbsp;xlated 144B  jited 108B  memlock 4096B<br/>
              </div>

              <div className="text-text-secondary mb-2">$ dmesg | tail -n 2</div>
              <div className="text-accent-green mb-4">
                [ 3672.412341] vortex: attached XDP program to eth0 (ifindex 2)<br/>
                [ 3672.415890] vortex: zero-copy ring buffer initialized<br/>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-text-secondary">$</span>
                <span className="w-2 h-4 bg-text-primary animate-pulse inline-block"></span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
