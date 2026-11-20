export const API_BASE = 
  import.meta.env.VITE_API_BASE || 
  (typeof window !== 'undefined' && window.location.port === '5173' ? 'http://localhost:8000' : '');
