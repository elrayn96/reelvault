export interface MediaItem {
  index: number;
  is_video: boolean;
  url: string;
  thumbnail: string;
}

export interface MediaData {
  id: string;
  type: 'video' | 'image' | 'carousel';
  original_type: 'post' | 'reel' | 'story' | 'carousel' | 'tv';
  caption: string;
  owner: string;
  timestamp: number;
  items: MediaItem[];
  fallback_active: boolean;
  fallback_message?: string;
}

export interface WebSocketMessage {
  type: 'progress' | 'info';
  status?: string;
  progress?: number;
  stage?: 'validating' | 'connecting' | 'downloading' | 'processing' | 'compressing' | 'packaging' | 'completed' | 'error' | 'finalized';
  data?: MediaData;
}
