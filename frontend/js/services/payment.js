/* SynthAI - Payment Service */
const PaymentService = (function() {
    const PAYMENTS_KEY = 'synthai_payments';
    const PLANS = {
        free: {
            id: 'free', name: 'Free', price: 0, period: '',
            badge: '', color: 'badge-free',
            features: [
                'plan.feature.free_1', 'plan.feature.free_2',
                'plan.feature.free_3', 'plan.feature.free_4',
                'plan.feature.free_5'
            ]
        },
        pro: {
            id: 'pro', name: 'Pro', price: 9.99, period: '/month',
            badge: '', color: 'badge-warning',
            features: [
                'plan.feature.pro_1', 'plan.feature.pro_2',
                'plan.feature.pro_3', 'plan.feature.pro_4',
                'plan.feature.pro_5'
            ]
        },
        premium: {
            id: 'premium', name: 'Premium', price: 29.99, period: '/month',
            badge: 'plan.most_popular', color: 'badge-premium',
            features: [
                'plan.feature.premium_1', 'plan.feature.premium_2',
                'plan.feature.premium_3', 'plan.feature.premium_4',
                'plan.feature.premium_5', 'plan.feature.premium_6'
            ]
        }
    };

    function getPayments() {
        return JSON.parse(localStorage.getItem(PAYMENTS_KEY) || '[]');
    }

    function savePayments(data) {
        localStorage.setItem(PAYMENTS_KEY, JSON.stringify(data));
    }

    function getUserSubscription(userId) {
        const payments = getPayments();
        const sub = payments.find(p => p.userId === userId && !p.expired);
        if (sub) {
            if (sub.expiresAt < Date.now()) {
                sub.expired = true;
                savePayments(payments);
                return null;
            }
            return sub;
        }
        return null;
    }

    function subscribe(userId, planId) {
        if (!PLANS[planId]) return { success: false, message: (typeof I18nService !== 'undefined' ? I18nService.t('payment.invalid_plan') : 'Invalid plan') };
        if (planId === 'free') {
            const users = AuthService.getUsers();
            const idx = users.findIndex(u => u.id === userId);
            if (idx !== -1) {
                users[idx].plan = 'free';
                users[idx].subscriptionExpires = null;
                AuthService.saveUsers(users);
                const currentUser = AuthService.getCurrentUser();
                if (currentUser && currentUser.id === userId) {
                    currentUser.plan = 'free';
                    currentUser.subscriptionExpires = null;
                    AuthService.updateCurrentUser(currentUser);
                }
            }
            return { success: true, plan: PLANS.free };
        }
        const plan = PLANS[planId];
        const payments = getPayments();
        const now = Date.now();
        const expiresAt = now + (30 * 24 * 60 * 60 * 1000);

        payments.push({
            id: now,
            userId: userId,
            planId: planId,
            planName: plan.name,
            price: plan.price,
            subscribedAt: now,
            expiresAt: expiresAt,
            expired: false,
            status: 'active'
        });

        savePayments(payments);

        const users = AuthService.getUsers();
        const idx = users.findIndex(u => u.id === userId);
        if (idx !== -1) {
            users[idx].plan = planId;
            users[idx].subscriptionExpires = expiresAt;
            AuthService.saveUsers(users);
            const currentUser = AuthService.getCurrentUser();
            if (currentUser && currentUser.id === userId) {
                currentUser.plan = planId;
                currentUser.subscriptionExpires = expiresAt;
                AuthService.updateCurrentUser(currentUser);
            }
        }

        return { success: true, plan: plan, expiresAt };
    }

    function getAvailablePlans() {
        return PLANS;
    }

    function simulatePayment(userId, planId) {
        return subscribe(userId, planId);
    }

    function getPaymentHistory(userId) {
        const payments = getPayments();
        return payments.filter(p => p.userId === userId).sort((a, b) => b.subscribedAt - a.subscribedAt);
    }

    function getUserPlan(userId) {
        const sub = getUserSubscription(userId);
        if (sub) return sub.planId;
        const users = AuthService.getUsers();
        const user = users.find(u => u.id === userId);
        return user ? user.plan : 'free';
    }

    function getPlanDetails(planId) {
        return PLANS[planId] || PLANS.free;
    }

    function canAccessFeature(userId, feature) {
        const plan = getUserPlan(userId);
        if (plan === 'premium') return true;
        const user = AuthService.getCurrentUser();
        if (user && user.role === 'admin') return true;
        if (plan === 'pro') {
            return feature !== 'bigdata';
        }
        return feature === 'medium';
    }

    function getDatasetLimit(userId) {
        const plan = getUserPlan(userId);
        const limits = { medium: 1000, large: 10000, bigdata: 100000 };
        const access = { free: ['medium'], pro: ['medium', 'large'], premium: ['medium', 'large', 'bigdata'] };
        return access[plan] || ['medium'];
    }

    function getAugmentationLimit(userId) {
        var plan = getUserPlan(userId);
        var limits = { free: [2], pro: [2, 5], premium: [2, 5, 10] };
        return limits[plan] || [2];
    }

    return {
        PLANS, getAvailablePlans, subscribe, getUserSubscription,
        simulatePayment, getPaymentHistory, getUserPlan,
        getPlanDetails, canAccessFeature, getDatasetLimit,
        getAugmentationLimit
    };
})();