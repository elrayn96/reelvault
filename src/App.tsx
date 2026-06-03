import { useState, useCallback } from 'react';
import { Header } from './components/Header';
import { Hero } from './components/Hero';
import { ProcessIndicator } from './components/ProcessIndicator';
import { PreviewCard } from './components/PreviewCard';
import { SuccessView } from './components/SuccessView';
import { Footer } from './components/Footer';
import { useWebSocket } from './hooks/useWebSocket';
import { analyzeUrl, downloadMedia, DownloadResponse } from './services/api';
import { MediaData, WebSocketMessage } from './types';

export default function App() {
  // Generate a persistent, random clientId for WebSockets session matching
  const [clientId] = useState(() => 'rv_' + Math.random().toString(36).substring(2, 10));

  // State managers
  const [stage, setStage] = useState<'idle' | 'analyzing' | 'preview' | 'downloading' | 'completed' | 'error'>('idle');
  const [scrapedData, setScrapedData] = useState<MediaData | null>(null);
  const [downloadResult, setDownloadResult] = useState<DownloadResponse | null>(null);
  const [compression, setCompression] = useState<'original' | 'compressed'>('original');
  const [inputUrl, setInputUrl] = useState('');

  // Real-time tracking progress logs
  const [statusMessage, setStatusMessage] = useState('Initiating ReelVault transit routes...');
  const [progressPercent, setProgressPercent] = useState(0);
  const [socketStage, setSocketStage] = useState('idle');
  const [errorDetails, setErrorDetails] = useState<string | null>(null);

  // Live WebSocket sync dispatcher
  const handleWebSocketMessage = useCallback((msg: WebSocketMessage) => {
    if (msg.type === 'progress') {
      if (msg.status) {
        setStatusMessage(msg.status);
      }
      if (msg.progress !== undefined) {
        setProgressPercent(msg.progress);
      }
      if (msg.stage) {
        setSocketStage(msg.stage);
      }
      
      // If we got completed final metadata inside analysis progress
      if (msg.stage === 'finalized' && msg.data) {
        setScrapedData(msg.data);
        setStage('preview');
      }
      
      // Handle download errors piped from WebSocket threads
      if (msg.stage === 'error') {
        setErrorDetails(msg.status || 'Transit operations disconnected.');
        setStage('error');
      }
    }
  }, []);

  const { isConnected: wsConnected } = useWebSocket(clientId, handleWebSocketMessage);

  // Analyze Link Action Trigger
  const handleAnalyze = async (url: string) => {
    setInputUrl(url);
    setStage('analyzing');
    setErrorDetails(null);
    setStatusMessage('Synchronizing secure analytics channels...');
    setProgressPercent(5);

    try {
      // Analyze URL endpoint
      const result = await analyzeUrl(url, clientId);
      setScrapedData(result);
      setStage('preview');
    } catch (err) {
      console.error(err);
      setErrorDetails((err as Error).message || 'Extraction failed. Please verify link properties or retry.');
      setStage('error');
    }
  };

  // Download Action Trigger
  const handleDownload = async (chosenCompression: 'original' | 'compressed') => {
    if (!scrapedData) return;
    
    setCompression(chosenCompression);
    setStage('downloading');
    setStatusMessage('Initiating download sequence...');
    setProgressPercent(15);

    try {
      // Download and package archive
      const result = await downloadMedia(inputUrl, chosenCompression, clientId);
      setDownloadResult(result);
      setStage('completed');
    } catch (err) {
      console.error(err);
      setErrorDetails((err as Error).message || 'Compilation failed. Verify media cache availability.');
      setStage('error');
    }
  };

  // Reset/Retry states
  const handleReset = () => {
    setStage('idle');
    setScrapedData(null);
    setDownloadResult(null);
    setErrorDetails(null);
    setProgressPercent(0);
    setInputUrl('');
    setStatusMessage('Initiating ReelVault transit routes...');
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#faf8ff] vault-gradient text-gray-800 font-sans selection:bg-indigo-150 selection:text-indigo-900">
      
      {/* Navbar Header banner */}
      <Header wsConnected={wsConnected} onReset={handleReset} />

      {/* Main interactive page routing */}
      <main className="flex-grow flex flex-col items-center justify-center">
        {stage === 'idle' && (
          <Hero 
            onAnalyze={handleAnalyze} 
            isLoading={false} 
            error={errorDetails} 
          />
        )}

        {stage === 'analyzing' && (
          <ProcessIndicator 
            status={statusMessage} 
            progress={progressPercent}
            stage={socketStage}
            onRetry={handleReset}
          />
        )}

        {stage === 'preview' && scrapedData && (
          <PreviewCard 
            data={scrapedData}
            onDownload={handleDownload}
            isDownloading={false}
            onBack={handleReset}
          />
        )}

        {stage === 'downloading' && (
          <ProcessIndicator 
            status={statusMessage} 
            progress={progressPercent}
            stage={socketStage}
            onRetry={handleReset}
          />
        )}

        {stage === 'completed' && downloadResult && scrapedData && (
          <SuccessView 
            downloadResult={downloadResult}
            compression={compression}
            thumbnail={scrapedData.items[activeCarouselIndex(scrapedData)].thumbnail}
            onReset={handleReset}
          />
        )}

        {stage === 'error' && (
          <ProcessIndicator 
            status={errorDetails || 'Unregistered pipeline crash.'} 
            progress={0}
            stage="error"
            onRetry={handleReset}
          />
        )}
      </main>

      {/* Corporate support guides and features description footer */}
      <Footer />
    </div>
  );
}

// Small layout helper to determine safe initial layout placeholder
function activeCarouselIndex(data: MediaData): number {
  return 0;
}
