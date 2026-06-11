import { MediaData } from '../types';

export interface DownloadResponse {
  success: boolean;
  filename: string;
  mimetype: string;
  download_url: string;
}

export async function analyzeUrl(url: string, clientId: string): Promise<MediaData> {
  let response;
  try {
    response = await fetch('/api/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url, client_id: clientId }),
    });
  } catch (netErr) {
    throw new Error(`Gateway connection offline: ${(netErr as Error).message}`);
  }

  if (!response.ok) {
    let errMsg = 'Failed to analyze url. Check account privacy settings or rate limits.';
    try {
      const errorDetails = await response.json();
      errMsg = errorDetails.detail || errMsg;
    } catch (e) {
      try {
        const textDetails = await response.text();
        if (textDetails && textDetails.includes('<!DOCTYPE html>') && textDetails.length > 500) {
          errMsg = 'ReelVault backend gateway returned an error template page. Try another link.';
        } else if (textDetails && textDetails.length < 300) {
          errMsg = textDetails;
        }
      } catch (inner) {}
    }
    throw new Error(errMsg);
  }

  try {
    return await response.json();
  } catch (e) {
    throw new Error('Received an invalid configuration envelope from ReelVault gateway.');
  }
}

export async function downloadMedia(url: string, compression: string, clientId: string): Promise<DownloadResponse> {
  let response;
  try {
    response = await fetch('/api/download', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url, compression, client_id: clientId }),
    });
  } catch (netErr) {
    throw new Error(`Gateway connection offline: ${(netErr as Error).message}`);
  }

  if (!response.ok) {
    let errMsg = 'Download compilation offline.';
    try {
      const errorDetails = await response.json();
      errMsg = errorDetails.detail || errMsg;
    } catch (e) {
      try {
        const textDetails = await response.text();
        if (textDetails && textDetails.includes('<!DOCTYPE html>') && textDetails.length > 500) {
          errMsg = 'Download pipeline compilation failed with an error page from backend.';
        } else if (textDetails && textDetails.length < 300) {
          errMsg = textDetails;
        }
      } catch (inner) {}
    }
    throw new Error(errMsg);
  }

  try {
    return await response.json();
  } catch (e) {
    throw new Error('Received an invalid compilation asset from ReelVault gateway.');
  }
}
