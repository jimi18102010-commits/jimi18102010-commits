
import { motion } from 'framer-motion';
import { ArrowUpRight, GitPullRequest, Activity, Cpu, ScanFace } from 'lucide-react';

const projects = [
  {
    title: "secdev/scapy",
    type: "Upstream / Core",
    icon: <GitPullRequest size={18} className="text-text-secondary" />,
    description: "Merged PR #5214 into authoritative Python packet manipulation library. Implemented EDNS0 padding & TLS SNI dissector logic for low-level packet tracing.",
    link: "https://github.com/secdev/scapy/pull/5214",
    metric: "Merged #5214",
    tech: ["Python", "Networking", "RFC Compliance"]
  },
  {
    title: "VORTEX",
    type: "Kernel / eBPF",
    icon: <Activity size={18} className="text-text-secondary" />,
    description: "Kernel-space packet drop engine. Operates at < 0.8 µs latency per packet via zero-copy ring buffer with memory-mapped user-space telemetry.",
    link: "https://github.com/jimi18102010-commits/vortex",
    metric: "< 0.8µs Latency",
    tech: ["eBPF", "XDP", "C", "Rust"]
  },
  {
    title: "DriveBlast",
    type: "High-Throughput IO",
    icon: <Cpu size={18} className="text-text-secondary" />,
    description: "3.8× faster multi-threaded chunked Google Drive streaming engine. Features custom dynamic window flow control and async chunk pipeline.",
    link: "https://github.com/jimi18102010-commits/Driveblast",
    metric: "3.8× Throughput",
    tech: ["Rust", "Python", "Async IO"]
  },
  {
    title: "FaceBlast",
    type: "Edge Inference",
    icon: <ScanFace size={18} className="text-text-secondary" />,
    description: "Real-time biometric pipeline utilizing ONNX Runtime and optimized C++ bindings for absolute minimal overhead on edge devices.",
    link: "https://github.com/jimi18102010-commits/faceblast",
    metric: "< 15ms Inference",
    tech: ["C++", "ONNX", "SIMD"]
  }
];

export function WorkGrid() {
  return (
    <section id="work" className="py-24 border-b dashed-border-b border-border-dark relative">
      <h2 className="text-sm font-mono text-text-secondary uppercase tracking-widest mb-12">Selected Engineering Work</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-border-dark dashed-grid">
        {projects.map((project, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: idx * 0.1, duration: 0.5 }}
            className="group relative bg-graphite/95 hover:bg-surface/80 p-8 transition-colors flex flex-col h-full"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                {project.icon}
                <span className="text-xs font-mono text-text-secondary">{project.type}</span>
              </div>
              <a
                href={project.link}
                target="_blank"
                rel="noopener noreferrer"
                className="text-text-secondary hover:text-accent-cyan transition-colors"
                aria-label={`View ${project.title}`}
              >
                <ArrowUpRight size={18} />
              </a>
            </div>

            <h3 className="text-xl font-medium text-text-primary mb-3">{project.title}</h3>

            <p className="text-text-secondary text-sm leading-relaxed mb-8 flex-grow">
              {project.description}
            </p>

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mt-auto pt-6 border-t border-border-dark/50">
              <span className="text-xs font-mono text-accent-green bg-accent-green/10 px-2 py-1 rounded inline-block w-fit">
                {project.metric}
              </span>

              <div className="flex flex-wrap gap-2">
                {project.tech.map((t, i) => (
                  <span key={i} className="text-[10px] font-mono text-text-secondary px-1.5 py-0.5 border border-border-dark rounded">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
