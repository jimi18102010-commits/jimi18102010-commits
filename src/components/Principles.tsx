
import { Terminal } from 'lucide-react';

export function Principles() {
  return (
    <section id="systems" className="py-24 relative">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12 lg:gap-8">

        {/* Notebook / Tech Stack Column */}
        <div className="lg:col-span-1">
          <h2 className="text-sm font-mono text-text-secondary uppercase tracking-widest mb-8 flex items-center gap-2">
            <Terminal size={16} />
            Technical Core
          </h2>

          <div className="space-y-8">
            <div>
              <h3 className="text-text-primary text-sm font-medium mb-3">Systems</h3>
              <ul className="text-text-secondary text-sm space-y-2 font-mono">
                <li>Linux Kernel Internals</li>
                <li>eBPF & XDP Filters</li>
                <li>POSIX Sockets</li>
                <li>Memory-Mapped IO</li>
                <li>SIMD Intrinsics</li>
              </ul>
            </div>

            <div>
              <h3 className="text-text-primary text-sm font-medium mb-3">Languages</h3>
              <ul className="text-text-secondary text-sm space-y-2 font-mono flex flex-wrap gap-x-6 gap-y-2">
                <li>Rust</li>
                <li>C / C++</li>
                <li>Python</li>
                <li>TypeScript</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Principles Column */}
        <div className="lg:col-span-2 lg:border-l dashed-border-x border-border-dark lg:pl-12">
          <h2 className="text-sm font-mono text-text-secondary uppercase tracking-widest mb-8">
            Engineering Principles
          </h2>

          <div className="space-y-10">
            <div>
              <h3 className="text-lg text-text-primary font-medium mb-2">Zero Allocations in Hot Loops</h3>
              <p className="text-text-secondary text-sm leading-relaxed max-w-2xl">
                Heap allocations introduce unpredictable latency spikes. In critical network paths, pre-allocated memory pools and ring buffers guarantee determinism. The garbage collector should never run while processing a packet.
              </p>
            </div>

            <div>
              <h3 className="text-lg text-text-primary font-medium mb-2">Data-Oriented Design</h3>
              <p className="text-text-secondary text-sm leading-relaxed max-w-2xl">
                Object-oriented hierarchies often result in scattered memory access patterns. Arranging data continuously arrays (Struct of Arrays) respects the CPU cache lines, fundamentally altering throughput characteristics.
              </p>
            </div>

            <div>
              <h3 className="text-lg text-text-primary font-medium mb-2">Predictable Cache Locality</h3>
              <p className="text-text-secondary text-sm leading-relaxed max-w-2xl">
                Modern CPUs are effectively idle when waiting on main memory. Minimizing L1/L2 cache misses by tightly packing structs and avoiding unnecessary pointers is more effective than theoretical algorithmic improvements.
              </p>
            </div>
          </div>
        </div>

      </div>
    </section>
  );
}
