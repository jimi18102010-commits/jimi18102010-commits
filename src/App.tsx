
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { Hero } from './components/Hero';
import { BufferVisualizer } from './components/BufferVisualizer';
import { WorkGrid } from './components/WorkGrid';
import { Principles } from './components/Principles';
import { TerminalDrawer } from './components/TerminalDrawer';
import { useAudioHaptic } from './hooks/useAudioHaptic';

function App() {
  const { playHaptic, isMuted, toggleMute } = useAudioHaptic();

  return (
    <div className="min-h-screen bg-graphite text-text-primary dashed-grid relative flex flex-col">
      <div className="absolute inset-0 bg-graphite/90 pointer-events-none z-0" />

      <div className="relative z-10 flex flex-col flex-grow">
        <Header isMuted={isMuted} toggleMute={toggleMute} playHaptic={playHaptic} />

        <main className="flex-grow max-w-6xl mx-auto w-full px-6">
          <Hero />

          <section className="py-12 border-b dashed-border-b border-border-dark">
            <h2 className="text-sm font-mono text-text-secondary uppercase tracking-widest mb-6">Live Telemetry</h2>
            <BufferVisualizer playHaptic={playHaptic} />
          </section>

          <WorkGrid />
          <Principles />
        </main>

        <Footer />
      </div>

      <TerminalDrawer playHaptic={playHaptic} />
    </div>
  );
}

export default App;
