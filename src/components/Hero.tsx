
import { motion } from 'framer-motion';

export function Hero() {
  return (
    <section className="py-24 md:py-32 border-b dashed-border-b border-border-dark relative">
      <div className="max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        >
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-medium tracking-tight text-text-primary leading-[1.1] mb-8">
            I'm Jimmiy — 15-year-old systems and low-latency engineer based in Tashkent, Uzbekistan.
          </h1>

          <p className="text-lg md:text-xl text-text-secondary leading-relaxed max-w-3xl font-sans font-light">
            I build network packet dissectors, eBPF filters, and high-throughput streaming systems with care for cache efficiency, memory safety, and predictable microsecond timing.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="mt-12 flex flex-wrap gap-4 font-mono text-sm"
        >
          <div className="flex items-center gap-2 px-3 py-1.5 border border-border-dark bg-surface/50 rounded-md">
            <span className="w-2 h-2 rounded-full bg-accent-cyan"></span>
            <span className="text-text-secondary">Upstream Scapy Contributor</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 border border-border-dark bg-surface/50 rounded-md">
            <span className="text-text-secondary">Focus:</span>
            <span className="text-text-primary">eBPF / Rust / C++ / Python</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
