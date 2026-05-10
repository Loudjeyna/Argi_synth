===============================================================================
                           SynthAI
           Smart Agricultural Intelligence Platform
===============================================================================

PROJECT DESCRIPTION
===============================================================================

SynthAI is a professional SaaS (Software as a Service) platform for smart 
agriculture that combines synthetic data generation using CTGAN (Conditional 
Tabular Generative Adversarial Network) with intelligent agricultural decision 
support. The platform serves three distinct user roles:

- Farmers: Access crop recommendations and growing condition insights
- Companies: Generate synthetic agricultural datasets for research and ML
- Administrators: Manage users, subscriptions, payments, and system monitoring

The platform addresses the critical challenge of limited agricultural data 
availability by generating realistic synthetic datasets that preserve the 
statistical properties of real agricultural data, while simultaneously 
providing farmers with actionable crop recommendations based on their 
specific soil and environmental conditions.


TECHNOLOGIES USED
===============================================================================

FRONTEND:
- HTML5: Semantic web structure and accessibility
- CSS3: Modern styling with CSS custom properties, Flexbox, Grid layouts,
        gradients, animations, and responsive design
- Vanilla JavaScript (ES6+): All client-side logic organized in modular
        service-based architecture (no frameworks, no libraries)

STORAGE:
- localStorage: Persistent data storage for users, predictions, datasets,
               payments, and subscription history
- sessionStorage: Session management for authenticated user state

DESIGN TOOLS:
- SVG icons: Custom scalable vector icons for navigation and UI elements
- CSS Variables: Consistent color theme (green agricultural palette)
- CSS Grid/Flexbox: Responsive layouts without external frameworks

BACKEND (optional/separate):
- Python 3.10+: CTGAN model training and data generation
- Pandas: Data manipulation and analysis
- SDV (Synthetic Data Vault): CTGAN implementation

DEPLOYMENT:
- Python HTTP server: python -m http.server 8080
- No build tools, bundlers, or package managers required


ARCHITECTURE
===============================================================================

The platform follows a Clean Architecture pattern with strict separation of
concerns across three layers:

LAYER 1: PRESENTATION LAYER (pages/)
  - 14 HTML pages organized by user role
  - Role-based routing and access control
  - Responsive UI with consistent theme
  - Each page handles its own rendering logic

LAYER 2: SERVICE LAYER (js/services/)
  - auth.js: Authentication, authorization, session management
  - payment.js: Subscription plans, simulated payments, plan enforcement
  - data.js: Fixed-size dataset generation, statistics, correlation, export
  - recommendation.js: Crop conditions database, prediction engine, export
  - history.js: Prediction tracking, search, filter, delete, export

LAYER 3: CONTROLLER LAYER (js/app.js)
  - Application routing and initialization
  - Sidebar navigation setup for each role
  - User panel display with plan information
  - Icon management for SVG navigation

FOLDER STRUCTURE:
  frontend/
    pages/           - 14 HTML pages (one per view)
    styles/          - global.css (complete theme system)
    js/
      services/      - 5 service modules (auth, payment, data, recommendation, history)
      app.js         - Main controller (sidebar, routing, icons)
    components/      - Reusable HTML components (future use)
    assets/          - Images, fonts, static resources

KEY ARCHITECTURAL DECISIONS:
- Service-based modular JavaScript using IIFE pattern (immediately-invoked
  function expressions) for namespace isolation
- Service layer encapsulates all business logic; pages only handle UI
- localStorage as data store with JSON serialization
- Role-based access enforced in each page's DOMContentLoaded handler
- Plan limits enforced at the service layer (not the UI)


FEATURES EXPLANATION
===============================================================================

FARMER FEATURES:

1. Crop to Conditions
   - Select any of 22 crops from a dropdown
   - Receives optimal growing conditions:
     * Temperature range (Celsius)
     * Humidity range (%)
     * Soil pH range
     * Rainfall range (mm)
     * N-P-K nutrient ranges
     * Water irrigation level (Low/Medium/High)
     * Fertilizer level (Low/Medium/High)
   - Visual indicators with color-coded level dots
   - CSV export of recommendations

2. Conditions to Crop
   - Input current soil conditions (N, P, K, temperature, humidity, pH, rainfall)
   - System computes compatibility scores for all 22 crops
   - Returns top 5 ranked matches with percentage scores
   - Visual match bars showing compatibility strength
   - Medal-style rank badges (gold, silver, bronze)
   - Best recommendation highlight card
   - CSV export of prediction results

3. Prediction History
   - Complete history of all predictions
   - Search by crop name
   - Filter by date range
   - Filter by prediction type
   - Delete individual entries
   - Clear all history
   - CSV export
   - Plan-based storage limits (Free: 10, Pro: 100, Premium: Unlimited)
   - KPI statistics (total, by type)

4. Daily Prediction Limits
   - Free: 5 predictions per day (resets daily)
   - Pro: 50 predictions per day
   - Premium: Unlimited predictions
   - Automatic enforcement with user notification

COMPANY FEATURES:

1. Synthetic Dataset Generation
   - Three dataset types: Crop, Soil, Weather
   - Fixed dataset sizes (enforced, not user-configurable):
     * Medium: 1,000 rows
     * Large: 10,000 rows (Pro and Premium)
     * Big Data: 100,000 rows (Premium only)
   - Type selection with visual cards
   - Level selection with plan badges
   - Disabled levels shown for unsubscribed users with upgrade prompt

2. Dataset Viewer (Kaggle-style)
   - Paginated table preview (20 rows per page)
   - Search/filter across all columns
   - Column statistics panel:
     * Mean, Standard Deviation
     * Min, Max, Median values
   - Correlation heatmap with color-coded cells
     * Green: positive correlation
     * Red: negative correlation
   - Missing values summary
   - CSV download with BOM for Excel compatibility
   - Total rows, column count, level badges

3. Dataset Management
   - List all generated datasets with metadata
   - View individual datasets in the viewer
   - Delete datasets
   - Status badges (Completed, level indicators)

ADMIN FEATURES:

1. User Management
   - View all registered users
   - Three-column tabs: Users, Payment History, Subscriptions
   - Change user plan via dropdown (Free/Pro/Premium)
   - Enable/disable user accounts
   - KPI dashboard: total users, predictions, datasets, plan distribution
   - Payment records with user, plan, amount, date
   - Active subscriptions with expiry dates

2. CTGAN Model Training
   - Visual GAN architecture diagram (Generator - Discriminator flow)
   - Training configuration (epochs, batch size, learning rate)
   - Live training simulation with:
     * Real-time epoch counter
     * Generator loss visualization (live bars)
     * Discriminator loss visualization (live bars)
     * Loss convergence tracking
   - Final model status with KPI cards
   - Sample data generation from trained model
   - Visual representation of the adversarial training process

3. Data Validation
   - Real vs Synthetic data comparison tables
   - Side-by-side statistical comparison (mean, std, min, max)
   - Distribution visualization by column
     * Real data distribution bars (green)
     * Synthetic data distribution bars (orange)
   - Automated validation checks:
     * pH range (0-14)
     * Non-negative rainfall
     * Nutrient values in range
     * Temperature range
     * Valid categorical labels
     * Distribution similarity
     * Correlation preservation
   - Quality score indicator with progress bar
   - Dataset quality KPIs (valid, warning, invalid counts)

4. System Dashboard
   - KPI cards: users, predictions, datasets, total rows
   - Quick action cards for model training, validation, user management


SETUP INSTRUCTIONS
===============================================================================

PREREQUISITES:
- A modern web browser (Chrome, Firefox, Edge, Safari)
- Python 3.10+ (optional, for HTTP server)

INSTALLATION:

1. Navigate to the project root:
   cd SynthAI

2. Start the HTTP server:
   python -m http.server 8080

3. Open the application:
   http://localhost:8080/frontend/pages/login.html

4. Login with default admin:
   Username: admin
   Password: admin123

5. Register new users:
   - Create a farmer account for crop predictions
   - Create a company account for dataset generation

NO ADDITIONAL DEPENDENCIES ARE REQUIRED.
The frontend runs entirely in the browser with no build steps.


USER ROLES EXPLANATION
===============================================================================

1. ADMINISTRATOR (admin)
   - Full system control
   - Manage all users (plans, status)
   - Monitor payments and subscriptions
   - Train CTGAN model with visual training simulation
   - Validate data quality with real vs synthetic comparison
   - View system-wide statistics
   - Default credentials: admin / admin123

2. FARMER
   - Agricultural decision support
   - Crop to Conditions: find optimal growing parameters
   - Conditions to Crop: predict best crops from conditions
   - View prediction history with search and filter
   - Export results as CSV
   - Subject to daily prediction limits based on plan

3. COMPANY
   - Synthetic dataset generation
   - Generate Crop, Soil, or Weather datasets
   - Fixed dataset sizes (1K, 10K, 100K rows)
   - View datasets with Kaggle-style viewer
   - Statistical analysis and correlation heatmaps
   - CSV export
   - Access to larger sizes depends on subscription plan


PAYMENT SYSTEM EXPLANATION
===============================================================================

PLANS:

1. FREE PLAN ($0)
   - 5 predictions/day (Farmer)
   - Medium dataset only (1,000 rows)
   - 10 history entries
   - Basic recommendations
   - Standard support

2. PRO PLAN ($9.99/month)
   - 50 predictions/day (Farmer)
   - Large datasets (10,000 rows)
   - 100 history entries
   - Advanced recommendations
   - All dataset types
   - Priority support

3. PREMIUM PLAN ($29.99/month)
   - Unlimited predictions
   - Big Data generation (100,000 rows)
   - Unlimited history entries
   - Advanced analytics dashboard
   - All dataset types + custom
   - 24/7 priority support

PAYMENT FLOW:
1. User visits Subscription page
2. Views plan comparison table with features
3. Selects a plan (Pro or Premium)
4. Simulated payment modal opens
5. User confirms payment (simulated card processing)
6. Payment is processed with 1.5 second delay
7. On success: user's plan is upgraded, subscription recorded
8. On failure: error message displayed, no charge

FEATURE ENFORCEMENT:
- Plan restrictions are enforced at the service layer
- Data generation levels are gated by plan
- Prediction limits reset daily based on last reset timestamp
- History storage limits applied when rendering
- Admin can manually change any user's plan

PAYMENT STORAGE:
- All payments stored in localStorage (synthai_payments)
- Each payment record includes: id, userId, planId, planName, price,
  subscribedAt, expiresAt (30 days), expired flag, status
- Subscription expiration checked on each session


CTGAN WORKFLOW EXPLANATION
===============================================================================

WHAT IS CTGAN?
CTGAN (Conditional Tabular Generative Adversarial Network) is a deep learning
architecture specifically designed for generating synthetic tabular data. It
extends the GAN (Generative Adversarial Network) framework to handle mixed
data types (numerical and categorical) commonly found in tabular datasets.

CTGAN ARCHITECTURE (as visualized in the platform):

1. GENERATOR
   - Creates synthetic samples that mimic real data patterns
   - Initially generates random data (poor quality)
   - Learns to produce increasingly realistic samples through training
   - Input: random noise vector
   - Output: synthetic tabular data row

2. DISCRIMINATOR
   - Evaluates whether samples are real or synthetic
   - Acts as a judge distinguishing original data from generated data
   - Provides feedback signal to improve the Generator
   - Input: data sample (real or synthetic)
   - Output: probability that sample is real

3. TRAINING PROCESS
   - Both components compete adversarially:
     * Generator creates samples to fool Discriminator
     * Discriminator improves at detecting fakes
     * Generator improves based on feedback
     * Cycle repeats until convergence
   - Training continues until:
     * Generator produces realistic data
     * Discriminator cannot reliably distinguish real vs synthetic
     * Loss values converge to stable values

4. SYNTHETIC DATA OUTPUT
   - Generated dataset preserves:
     * Statistical distributions (mean, std, min, max)
     * Correlations between features
     * Valid categorical labels and ranges
     * Relationships between variables (e.g., temperature-humidity)

WHY CTGAN FOR AGRICULTURE:
- Specialized for tabular data (not images or text)
- Preserves feature correlations critical for agricultural analysis
- Handles mixed data types (numeric: temperature, pH; categorical: crop labels)
- Produces realistic agricultural data that passes statistical validation
- Addresses data scarcity in agricultural research

PLATFORM SIMULATION:
Since the frontend runs purely in the browser without Python backend, the 
CTGAN training is simulated visually to demonstrate:
- Real-time loss tracking (Generator vs Discriminator)
- Epoch progression
- Loss convergence visualization
- Model readiness indicators
- Sample generation from trained model


DESIGN CHOICES
===============================================================================

1. COLOR PALETTE: Green Agricultural Theme
   - Primary: #1B5E20 (Dark green - trust, growth, stability)
   - Secondary: #2E7D32 (Medium green - nature, agriculture)
   - Accent: #66BB6A (Light green - freshness, vitality)
   - Background: #FAFBF8 (Soft cream - warmth, readability)
   - Earth: #8D6E63 (Brown accent - soil, earthiness)
   - Rationale: Green represents agriculture, growth, and environmental
     consciousness. The palette creates a calm, professional atmosphere.

2. CARD-BASED DESIGN
   - Content organized in rounded cards with subtle shadows
   - Clear visual hierarchy with consistent spacing
   - KPIs displayed in bordered cards with large numbers
   - Rationale: Cards improve scanability and create visual structure

3. FIXED SIDEBAR NAVIGATION
   - Role-specific menu items with SVG icons
   - Active page highlighting
   - User panel with plan badge
   - Rationale: Provides consistent navigation context across all pages

4. SVG ICONS (NO EMOJIS)
   - Custom SVG paths for all navigation icons
   - Scalable, crisp at any resolution
   - Consistent styling with currentColor fill
   - Rationale: Professional appearance, accessibility, theme consistency


SECURITY CHOICES
===============================================================================

1. SESSION-BASED AUTHENTICATION
   - Session stored in sessionStorage (cleared on tab close)
   - Role verification on every page load
   - Redirect to login for unauthenticated users
   - Rationale: Session storage is safer than localStorage for sensitive
     session data and is automatically cleared when the browser closes.

2. ROLE-BASED ACCESS CONTROL
   - Each page validates user role in DOMContentLoaded
   - Unauthorized users see access denied message
   - Navigation menu only shows role-appropriate links
   - Rationale: Defense in depth - multiple layers verify authorization.

3. ACCOUNT MANAGEMENT
   - Admin can disable any user account
   - Disabled accounts cannot log in
   - Plan-based feature gating at service level
   - Rationale: Platform control for administrators over resource access.

4. INPUT VALIDATION
   - Form validation on all input fields
   - Numeric range checking (min/max values)
   - Required field validation
   - Rationale: Prevents invalid data entry and edge cases.

5. DATA ISOLATION
   - Each service module is encapsulated in an IIFE
   - No global variable pollution
   - Services only expose public API methods
   - Rationale: Prevents unauthorized access to internal data structures.

NOTE: As a demonstration prototype, passwords are stored in plaintext in
localStorage. A production version would implement:
- Server-side authentication
- Password hashing (bcrypt/argon2)
- HTTPS-only communication
- JWT or OAuth-based token authentication
- SQL injection prevention
- XSS and CSRF protection


SCALABILITY CHOICES
===============================================================================

1. MODULAR SERVICE ARCHITECTURE
   - Each service handles exactly one domain concern
   - Services can be extended without modifying other modules
   - New features can be added as new service files
   - Rationale: Clean separation allows independent scaling of features.

2. DATA ABSTRACTION
   - All data access goes through service methods
   - Storage backend (localStorage) can be replaced with API calls
   - Same interface regardless of storage implementation
   - Rationale: Enables migration to server-side database without
     changing page logic.

3. COMPONENT-BASED PAGES
   - Consistent header, sidebar, and footer across all pages
   - Shared CSS variables and utility classes
   - Reusable service modules across multiple pages
   - Rationale: Reduces duplication and enables consistent updates.

4. ROLE-BASED FEATURE EXPANSION
   - New roles can be added to the routing system
   - Navigation is data-driven (array of links per role)
   - Page access control is role-parameterized
   - Rationale: New user types can be added without restructuring.

5. STATIC FILE SERVING
   - No build step required
   - Any HTTP server can serve the frontend
   - Easy to deploy to CDN or cloud storage
   - Rationale: Simplifies deployment and reduces infrastructure needs.

LIMITATIONS (for demo):
- localStorage has ~5-10MB limit (full 100K datasets not storable)
- No server-side processing for actual CTGAN
- Single-browser, single-user without real multi-tenancy
- These would be addressed with backend API integration


MAINTAINABILITY TECHNIQUES
===============================================================================

1. SINGLE RESPONSIBILITY PRINCIPLE (SRP)
   - auth.js: Only handles authentication concerns
   - payment.js: Only handles subscription and payment logic
   - data.js: Only handles data generation and statistics
   - recommendation.js: Only handles crop recommendations
   - history.js: Only handles prediction history
   - Each file has exactly one reason to change.

2. SEPARATION OF CONCERNS
   - Pages (HTML): Structure and presentation
   - Services (JS): Business logic and data management
   - Controllers (app.js): Application orchestration
   - Styles (CSS): Visual presentation
   - No inline business logic in HTML files.

3. CONSISTENT CODING CONVENTIONS
   - Descriptive variable and function names
   - Consistent indentation and formatting
   - Modular IIFE pattern for all services
   - Return object at end of each service module
   - Clear function signatures with single responsibilities.

4. CENTRALIZED THEME MANAGEMENT
   - All colors defined as CSS custom properties in :root
   - Consistent component styles defined once
   - Utility classes for common patterns
   - Global changes via variable updates.

5. ERROR HANDLING
   - Status messages for all user actions (success, warning, error)
   - Graceful empty states for all data displays
   - Fallback UI for missing data or failed operations
   - Form validation with user feedback.

6. CODE DOCUMENTATION
   - File headers describing module purpose
   - Clear function names that describe behavior
   - Descriptive comments for complex logic
   - Consistent return value patterns.

7. TESTABILITY
   - Services are pure functions (given input, return output)
   - No DOM dependencies in service layer
   - Data store can be mocked by replacing localStorage
   - Business logic separated from UI rendering.

===============================================================================
                         END OF DOCUMENTATION
===============================================================================
