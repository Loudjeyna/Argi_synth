# SynthAI - Smart Agricultural Intelligence Platform

<div align="center">

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![HTML5](https://img.shields.io/badge/html5-E34F26.svg?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-1572B6.svg?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-F7DF1E.svg?logo=javascript&logoColor=black)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-Active-brightgreen.svg)

**AI-Powered Agricultural Data Platform**

</div>

---

## System Overview

SynthAI is a professional SaaS platform that combines synthetic data generation using CTGAN (Conditional Tabular Generative Adversarial Network) with intelligent agricultural decision support. The platform addresses the critical challenge of limited agricultural data availability by generating realistic synthetic datasets while providing farmers with actionable crop recommendations.

The system serves three distinct user roles:
- **Farmers**: Access crop recommendations and growing condition insights
- **Companies**: Generate synthetic agricultural datasets for research and ML training
- **Admins**: Manage users, subscriptions, and system configuration

---

## Architecture

### Folder Structure

```
SynthAI/
├── frontend/
│   ├── pages/
│   │   ├── login.html              # Authentication page
│   │   ├── farmer_home.html        # Farmer dashboard
│   │   ├── crop_conditions.html     # Crop to Conditions page
│   │   ├── conditions_crop.html     # Conditions to Crop page
│   │   ├── history.html            # Prediction history
│   │   ├── company_home.html       # Company dashboard
│   │   ├── generate_data.html      # Data generation page
│   │   ├── datasets.html           # Dataset listing
│   │   ├── admin_home.html         # Admin dashboard
│   │   ├── admin_users.html        # User management
│   │   ├── admin_validation.html   # Data validation
│   │   └── admin_model.html        # Model training
│   ├── styles/
│   │   └── global.css              # Global styles
│   └── js/
│       ├── app.js                  # Main application controller
│       └── services/
│           ├── auth.js             # Authentication service
│           ├── history.js          # Prediction history service
│           ├── recommendation.js   # Crop recommendation engine
│           └── data.js             # Data generation service
├── backend/
│   ├── controllers/                # Request handlers
│   ├── services/                   # Business logic
│   ├── models/                     # Data models
│   └── utils/                      # Utility functions
├── src/
│   ├── ctgan_model.py             # CTGAN model wrapper
│   ├── database.py                # SQLite database management
│   ├── recommender.py             # Python recommendation engine
│   ├── data_loader.py             # Data loading utilities
│   └── generator.py               # Statistics utilities
├── data/                          # Datasets and database
├── models/                        # Saved CTGAN models
└── outputs/                       # Generated synthetic data
```

### Design Principles

1. **Separation of Concerns**: UI (frontend/pages), logic (frontend/js/services), and backend are isolated
2. **Single Responsibility**: Each service handles one domain (auth, history, data, recommendations)
3. **Clean Architecture**: Frontend communicates with backend services through well-defined interfaces
4. **Scalability**: Modular structure allows easy addition of new features

---

## User Roles and Features

### Farmer Role

Farmers use the platform for agricultural decision support.

**Crop to Conditions**
- Select a crop from dropdown
- Receive optimal growing parameters:
  - Temperature range
  - Humidity range
  - pH range
  - Rainfall requirements
  - Nitrogen, Phosphorus, Potassium levels
  - Water level (Low/Medium/High)
  - Fertilizer level (Low/Medium/High)

**Conditions to Crop**
- Input soil and environmental conditions:
  - N, P, K values
  - Temperature
  - Humidity
  - pH
  - Rainfall
- System returns ranked crop matches with compatibility scores

**History Tracking**
- All predictions stored with timestamp
- Search by crop name
- Filter by date
- Export history as CSV

**Usage Limits**
- Free users: 5 predictions per day
- Premium users: Unlimited predictions

### Company Role

Companies generate synthetic agricultural datasets.

**Data Generation**
- Medium: 500 rows (Free)
- Large: 2,000 rows (Free with limits)
- Big Data: 10,000 rows (Premium)

**Features**
- Live data preview
- Statistical analysis (mean, std, min, max)
- CSV download
- Usage tracking

### Admin Role

Full system control and management.

**User Management**
- View all registered users
- Toggle account active/inactive
- Upgrade/downgrade subscriptions
- Monitor usage statistics

**Data Validation**
- View all generated datasets
- Quality checks:
  - pH range validation
  - Non-negative rainfall
  - Nutrient value ranges
- Status indicators: Valid/Warning/Invalid

**Model Training**
- Configure epochs and batch size
- Train CTGAN model
- View model status

---

## Monetization System

### Free Plan
- 5 predictions/day (Farmers)
- Medium data generation (500 rows)
- 10 history entries
- Basic recommendations

### Premium Plan
- Unlimited predictions
- Big Data generation (10,000 rows)
- Full history access (50+ entries)
- Advanced analytics
- Priority processing

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| HTML5 | Semantic structure |
| CSS3 | Modern styling with CSS variables, flexbox, grid |
| JavaScript (ES6+) | Client-side logic, service modules |
| Python | Backend CTGAN processing |
| CTGAN (SDV) | Synthetic data generation |
| SQLite | User and history storage |
| Pandas | Data manipulation |

---

## Getting Started

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari)
- Python 3.10+ (for backend)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd SynthAI

# Install Python dependencies (for backend)
pip install -r requirements.txt
```

### Running the Platform

```bash
# Option 1: Open directly in browser
Open frontend/pages/login.html in your browser

# Option 2: Serve with Python
cd frontend
python -m http.server 8000
# Visit http://localhost:8000/pages/login.html
```

### Default Credentials
- **Admin**: username: `admin`, password: `admin123`
- **Register**: Create new farmer or company accounts from the login page

---

## UI/UX Design

### Color Palette
- **Primary**: #2E7D32 (Dark Green)
- **Secondary**: #66BB6A (Light Green)
- **Background**: #FAFBF8 (Soft Cream)
- **Text**: #1C1C1C (Near Black)
- **Accent**: #8D6E63 (Earth Brown)

### Design Principles
- Clean, minimal SaaS aesthetic
- Responsive layout (desktop + mobile)
- Card-based dashboard components
- Real SVG icons (no emojis)
- Clear visual hierarchy
- Smooth transitions and hover states

---

## Data Flow Example

1. **User Authentication**
   - User enters credentials on login.html
   - AuthService validates against localStorage database
   - Redirects to role-specific dashboard

2. **Crop Recommendation**
   - Farmer selects crop in crop_conditions.html
   - RecommendationService retrieves optimal conditions
   - HistoryService records the prediction
   - Results displayed in formatted cards

3. **Data Generation**
   - Company selects parameters in generate_data.html
   - DataService generates preview with statistics
   - Results saved to localStorage
   - CSV download available

---

## Backend Integration

The frontend is designed to work with the Python backend:

```python
# Backend service integration example
from src.ctgan_model import CTGANModel
from src.database import Database
from src.recommender import CropRecommender

# Train model
model = CTGANModel(epochs=300, verbose=True)
model.train(real_data)
model.save("models/ctgan_model.pkl")

# Generate synthetic data
synthetic_df = model.generate(num_rows=1000)
synthetic_df.to_csv("outputs/synthetic_data.csv")
```

The backend handles:
- CTGAN model training
- Synthetic data generation
- Real data statistics
- Database operations

---

## Screenshots

*[Add screenshots here]*

- Login page
- Farmer dashboard
- Crop recommendations
- Company data generation
- Admin user management

---

## Academic Project Information

This project is designed for demonstration in an academic setting (Master 2 level). It demonstrates:
- Full-stack web development
- AI/ML integration (CTGAN)
- Clean architecture principles
- SaaS platform design
- Role-based access control
- Subscription monetization

---

## License

MIT License - See LICENSE file for details.

---

<div align="center">

**SynthAI - Smart Agricultural Intelligence Platform**

Growing the future with AI