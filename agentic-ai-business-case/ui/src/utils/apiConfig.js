/**
 * API Configuration Utility
 * Handles API URL configuration for development and production environments
 */

// In production (served by Flask), use relative URLs
// In development (Vite dev server), use localhost:5000
export const getApiUrl = (path = '') => {
  const baseUrl = import.meta.env.PROD ? '/api' : 'http://localhost:5000/api';
  return path ? `${baseUrl}${path.startsWith('/') ? path : `/${path}`}` : baseUrl;
};

export default getApiUrl;
