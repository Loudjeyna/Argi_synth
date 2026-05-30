/* SynthAI - Main Application Controller */
const App = (function() {
    var PREFIX = '/pages/';

    function p(path) { return PREFIX + path; }

    var PAGES = {
        login: p('login.html'),
        farmer: {
            home: p('farmer_home.html'),
            crop_conditions: p('crop_conditions.html'),
            conditions_crop: p('conditions_crop.html'),
            predict: p('farmer_predict.html'),
            history: p('history.html')
        },
        company: {
            home: p('company_home.html'),
            generate: p('generate_data.html'),
            datasets: p('datasets.html'),
            comparison: p('model_comparison.html')
        },
        admin: {
            home: p('admin_home.html'),
            users: p('admin_users.html'),
            models: p('admin_models.html'),
            training: p('admin_training.html'),
            model_details: p('admin_model_details.html'),
            comparison: p('model_comparison.html')
        }
    };

    function init() {
        var user = AuthService.getCurrentUser();
        if (window.location.pathname.includes('login.html') && user) {
            redirectByRole(user.role);
        } else if (!window.location.pathname.includes('login.html') && !user) {
            window.location.href = p('login.html');
        }
    }

    function redirectByRole(role) {
        const routes = { admin: PAGES.admin.home, company: PAGES.company.home, farmer: PAGES.farmer.home };
        window.location.href = routes[role] || PAGES.login;
    }

    function setupSidebar() {
        const user = AuthService.getCurrentUser();
        if (!user) return;
        const nav = document.getElementById('sidebar-nav');
        if (!nav) return;
        
        const links = [];
        if (user.role === 'admin') {
            links.push({ href: PAGES.admin.home, icon: 'home', label: 'Dashboard' });
            links.push({ href: PAGES.admin.training, icon: 'gear', label: 'New Training' });
            links.push({ href: PAGES.admin.models, icon: 'database', label: 'Models' });
            links.push({ href: PAGES.company.generate, icon: 'database', label: 'Generate Data' });
            links.push({ href: PAGES.admin.users, icon: 'users', label: 'Users' });
            links.push({ href: PAGES.company.datasets, icon: 'file', label: 'Datasets' });
            links.push({ href: PAGES.admin.comparison, icon: 'chart', label: 'Model Comparison' });
        } else if (user.role === 'company') {
            links.push({ href: PAGES.company.home, icon: 'home', label: 'Dashboard' });
            links.push({ href: PAGES.company.generate, icon: 'database', label: 'Generate Data' });
            links.push({ href: PAGES.company.datasets, icon: 'file', label: 'Datasets' });
            links.push({ href: PAGES.company.comparison, icon: 'chart', label: 'Model Comparison' });
            links.push({ href: p('subscription.html'), icon: 'star', label: 'Subscription' });
        } else {
            links.push({ href: PAGES.farmer.home, icon: 'home', label: 'Dashboard' });
            links.push({ href: PAGES.farmer.predict, icon: 'brain', label: 'Crop Prediction' });
            links.push({ href: PAGES.farmer.crop_conditions, icon: 'seedling', label: 'Crop \u2192 Conditions' });
            links.push({ href: PAGES.farmer.conditions_crop, icon: 'search', label: 'Conditions \u2192 Crop' });
            links.push({ href: PAGES.farmer.history, icon: 'history', label: 'History' });
            links.push({ href: p('subscription.html'), icon: 'star', label: 'Subscription' });
        }

        const currentPage = window.location.pathname.split('/').pop();
        nav.innerHTML = links.map(l => {
            const isActive = currentPage === l.href ? 'active' : '';
            return '<a href="' + l.href + '" class="' + isActive + '">' +
                '<svg viewBox="0 0 24 24"><path d="' + getIconPath(l.icon) + '"/></svg>' +
                '<span>' + l.label + '</span></a>';
        }).join('');
    }

    function getIconPath(name) {
        const paths = {
            home: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
            seedling: 'M12 19l9 2-9-18-9 18 9-2zm0 0v-8',
            search: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z',
            history: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
            database: 'M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4',
            file: 'M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z',
            users: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z',
            brain: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z',
            chart: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
            star: 'M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z',
            logout: 'M17 16l4-4m0 0l-4-4m6 4H3',
            gear: 'M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4',
            brain: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z'
        };
        return paths[name] || paths.home;
    }

    function setupUserPanel() {
        const user = AuthService.getCurrentUser();
        if (!user) return;
        const panel = document.getElementById('user-panel');
        if (!panel) return;
        const planBadge = user.plan === 'premium' ? '<span class="badge badge-premium">PREMIUM</span>' : '<span class="badge badge-free">FREE</span>';
        panel.innerHTML = '<div class="sidebar-user"><div class="name">' + user.username + '</div><div class="email">' + user.email + '</div>' + planBadge + '</div>';
    }

    function setupLogout() {
        var btn = document.getElementById('logout-btn');
        if (btn) btn.addEventListener('click', function() { AuthService.logout(); window.location.href = p('login.html'); });
    }

    // Global logout safety: event delegation catches clicks even if setupLogout() was never called
    document.addEventListener('click', function(e) {
        var target = e.target;
        while (target) {
            if (target.id === 'logout-btn' || (target.tagName === 'BUTTON' && target.textContent.trim() === 'Logout')) {
                try { AuthService.logout(); } catch (ex) { sessionStorage.clear(); }
                window.location.href = p('login.html');
                e.preventDefault();
                return;
            }
            target = target.parentElement;
        }
    });

    return { init, setupSidebar, setupUserPanel, setupLogout, PAGES };
})();