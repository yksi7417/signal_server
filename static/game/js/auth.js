// Authentication module — Sign in with Apple + Guest mode
import { store } from './gameStore.js';

const SESSION_KEY = 'sessionToken';

/**
 * Fetch wrapper that adds Authorization header when a session exists.
 */
export async function apiFetch(url, opts = {}) {
    const headers = { ...opts.headers };
    const token = localStorage.getItem(SESSION_KEY);
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return fetch(url, { ...opts, headers });
}

/**
 * Check if we have a valid session. Returns user object or null.
 */
export async function checkAuth() {
    const token = localStorage.getItem(SESSION_KEY);
    if (!token) return null;

    try {
        const resp = await apiFetch('/api/auth/me');
        if (resp.ok) {
            const data = await resp.json();
            if (data.success) {
                store.currentUser = data.user;
                return data.user;
            }
        }
    } catch (e) {
        console.warn('Auth check failed:', e);
    }
    // Token invalid — clear it
    localStorage.removeItem(SESSION_KEY);
    store.currentUser = null;
    return null;
}

/**
 * Initiate Sign in with Apple flow using the Apple JS SDK.
 */
export async function loginWithApple() {
    try {
        // Apple JS SDK must be loaded in index.html
        const data = await window.AppleID.auth.signIn();
        const idToken = data.authorization.id_token;
        const fullName = data.user
            ? `${data.user.name.firstName || ''} ${data.user.name.lastName || ''}`.trim()
            : null;

        const resp = await fetch('/api/auth/apple', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                identity_token: idToken,
                display_name: fullName,
            }),
        });

        const result = await resp.json();
        if (result.success) {
            localStorage.setItem(SESSION_KEY, result.session_token);
            store.currentUser = result.user;
            hideLoginOverlay();
            return result.user;
        } else {
            console.error('SIWA login failed:', result.error);
            return null;
        }
    } catch (e) {
        console.error('Apple sign-in error:', e);
        return null;
    }
}

/**
 * Continue as guest — no auth, no stats persistence.
 */
export function playAsGuest() {
    store.currentUser = null;
    hideLoginOverlay();
}

/**
 * Logout — invalidate session.
 */
export async function logout() {
    const token = localStorage.getItem(SESSION_KEY);
    if (token) {
        try {
            await fetch('/api/auth/logout', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
            });
        } catch (e) { /* ignore */ }
    }
    localStorage.removeItem(SESSION_KEY);
    store.currentUser = null;
    showLoginOverlay();
}

/**
 * Get auth headers for use in fetch calls.
 */
export function getAuthHeaders() {
    const token = localStorage.getItem(SESSION_KEY);
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

// --- Login overlay UI ---

function showLoginOverlay() {
    const overlay = document.getElementById('loginOverlay');
    if (overlay) overlay.style.display = 'flex';
}

function hideLoginOverlay() {
    const overlay = document.getElementById('loginOverlay');
    if (overlay) overlay.style.display = 'none';
}

/**
 * Initialize auth on page load.
 * Shows login overlay if no valid session, otherwise proceeds silently.
 */
export async function initAuth() {
    const user = await checkAuth();
    if (!user) {
        showLoginOverlay();
    }
    return user;
}
