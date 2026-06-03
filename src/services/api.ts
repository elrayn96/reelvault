import { MediaData } from '../types';

export interface DownloadResponse {
  success: boolean;
  filename: string;
  mimetype: string;
  download_url: string;
}

export async function analyzeUrl(url: string, clientId: string): Promise<MediaData> {
  const response = await fetch('/api/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url, client_id: clientId }),
  });

  if (!response.ok) {
    const errorDetails = await response.json();
    throw new Error(errorDetails.detail || 'Failed to analyze url. Check account privacy settings or rate limits.');
  }

  return response.json();
}

export async function downloadMedia(url: string, compression: string, clientId: string): Promise<DownloadResponse> {
  const response = await fetch('/api/download', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url, compression, client_id: clientId }),
  });

  if (!response.ok) {
    const errorDetails = await response.json();
    throw new Error(errorDetails.detail || 'Download compilation failed.');
  }

  return response.json();
}
