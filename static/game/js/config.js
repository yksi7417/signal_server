// Configuration for Capacitor vs server mode
// In Capacitor local mode, API calls must go to the remote server
// In server mode (or browser), API calls go to the same origin

const isCapacitor = typeof window.Capacitor !== 'undefined' || window.location.protocol === 'capacitor:';

// API base URL: empty string for same-origin (server mode), full URL for Capacitor
export const API_BASE = isCapacitor ? 'https://signal-server-eo-7uq.fly.dev' : '';

/**
 * Build a full API URL from a path like '/api/draw_tile'
 */
export function apiUrl(path) {
    return API_BASE + path;
}
