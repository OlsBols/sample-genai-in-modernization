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

/**
 * Fetch wrapper that retries once on 401 (handles ALB OIDC session cookie issues)
 * On 401, reloads the page to re-authenticate via the ALB OIDC flow
 */
export const fetchWithAuth = async (url, options = {}, retries = 1) => {
  const response = await fetch(url, options);
  if (response.status === 401 && retries > 0) {
    // Wait briefly then retry - cookie may not have been sent on first request
    await new Promise(resolve => setTimeout(resolve, 1000));
    const retryResponse = await fetch(url, options);
    if (retryResponse.status === 401) {
      // Session truly expired - reload to re-authenticate
      window.location.reload();
      return retryResponse;
    }
    return retryResponse;
  }
  return response;
};

export default getApiUrl;
