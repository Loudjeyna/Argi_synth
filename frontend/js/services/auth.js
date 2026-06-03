/* SynthAI - Auth Service */
const AuthService = (function() {
    const USERS_KEY = 'synthai_users';
    const SESSION_KEY = 'synthai_session';

    function initUsers() {
        if (!localStorage.getItem(USERS_KEY)) {
            const defaultUsers = [{
                id: 1, username: 'admin', email: 'admin@synthai.com',
                password: 'admin123', role: 'admin', plan: 'premium',
                attempts: 0, lastReset: new Date().toISOString(),
                isActive: true, createdAt: new Date().toISOString()
            }];
            localStorage.setItem(USERS_KEY, JSON.stringify(defaultUsers));
        }
    }

    function getUsers() {
        return JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
    }

    function saveUsers(users) {
        localStorage.setItem(USERS_KEY, JSON.stringify(users));
    }

    function register(username, email, password, role = 'farmer') {
        initUsers();
        const users = getUsers();
        if (users.find(u => u.username === username || u.email === email)) {
            return { success: false, message: (typeof I18nService !== 'undefined' ? I18nService.t('login.exists') : 'Username or email already exists') };
        }
        const newUser = {
            id: users.length + 1, username, email, password, role,
            plan: 'free', attempts: 0, lastReset: new Date().toISOString(),
            isActive: true, createdAt: new Date().toISOString()
        };
        users.push(newUser);
        saveUsers(users);
        return { success: true, user: newUser };
    }

    function login(username, password) {
        initUsers();
        const users = getUsers();
        const user = users.find(u => u.username === username && u.password === password);
        if (!user) return { success: false, message: (typeof I18nService !== 'undefined' ? I18nService.t('login.invalid') : 'Invalid credentials') };
        if (!user.isActive) return { success: false, message: (typeof I18nService !== 'undefined' ? I18nService.t('login.disabled') : 'Account is disabled') };
        sessionStorage.setItem(SESSION_KEY, JSON.stringify(user));
        return { success: true, user };
    }

    function logout() {
        sessionStorage.removeItem(SESSION_KEY);
    }

    function getCurrentUser() {
        const session = sessionStorage.getItem(SESSION_KEY);
        return session ? JSON.parse(session) : null;
    }

    function isPremium() {
        const user = getCurrentUser();
        return user && user.plan === 'premium';
    }

    function canAttempt() {
        const user = getCurrentUser();
        if (!user) return false;
        if (user.role === 'admin' || user.plan === 'premium') return true;
        const now = new Date();
        const lastReset = new Date(user.lastReset);
        if (now.getDate() !== lastReset.getDate()) {
            user.attempts = 0;
            user.lastReset = now.toISOString();
            updateCurrentUser(user);
        }
        return user.attempts < 5;
    }

    function recordAttempt() {
        const user = getCurrentUser();
        if (user) {
            user.attempts = (user.attempts || 0) + 1;
            updateCurrentUser(user);
        }
    }

    function getRemainingAttempts() {
        const user = getCurrentUser();
        if (!user) return 0;
        if (user.role === 'admin' || user.plan === 'premium') return Infinity;
        if (user.plan === 'pro') return Math.max(0, 50 - (user.attempts || 0));
        const now = new Date();
        const lastReset = new Date(user.lastReset);
        if (now.getDate() !== lastReset.getDate()) return 5;
        return Math.max(0, 5 - (user.attempts || 0));
    }

    function updateCurrentUser(updatedUser) {
        const users = getUsers();
        const idx = users.findIndex(u => u.id === updatedUser.id);
        if (idx !== -1) {
            users[idx] = updatedUser;
            saveUsers(users);
            sessionStorage.setItem(SESSION_KEY, JSON.stringify(updatedUser));
        }
    }

    function syncSessionFromStorage() {
        const current = getCurrentUser();
        if (!current) return null;
        const users = getUsers();
        const fresh = users.find(u => u.id === current.id);
        if (fresh) {
            sessionStorage.setItem(SESSION_KEY, JSON.stringify(fresh));
            return fresh;
        }
        return current;
    }

    function upgradeUser(userId, plan) {
        const users = getUsers();
        const idx = users.findIndex(u => u.id === userId);
        if (idx !== -1) {
            users[idx].plan = plan;
            saveUsers(users);
            return true;
        }
        return false;
    }

    function toggleUserStatus(userId) {
        const users = getUsers();
        const idx = users.findIndex(u => u.id === userId);
        if (idx !== -1) {
            users[idx].isActive = !users[idx].isActive;
            saveUsers(users);
            return users[idx].isActive;
        }
        return null;
    }

    return {
        initUsers, register, login, logout, getCurrentUser,
        isPremium, canAttempt, recordAttempt, getRemainingAttempts,
        updateCurrentUser, upgradeUser, toggleUserStatus, getUsers, saveUsers,
        syncSessionFromStorage
    };
})();