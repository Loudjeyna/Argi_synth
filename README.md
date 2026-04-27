# AgroAI - Smart Agriculture Platform

<div align="center">

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-Active-brightgreen.svg)

**AI-Powered Agricultural Data Platform with CTGAN**

</div>

---

## 🌱 Project Overview

AgroAI is a professional agricultural SaaS platform that leverages **CTGAN (Conditional Tabular Generative Adversarial Network)** to generate synthetic agricultural data for crop recommendation. The platform provides role-based access for **Farmers** and **Admins**, with a monetization system to support free and premium plans.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AgroAI Platform                         │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   Login/     │───▶│    Admin     │    │   Farmer     │ │
│  │  Register   │    │  Dashboard   │    │  Dashboard   │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────┐   │
│  │              SQLITE Database                       │   │
│  │   - Users Table (username, email, role, plan)      │   │
│  │   - Usage Logs (track generation)                  │   │
│  │   - Model Status (CTGAN trained state)            │   │
│  └────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────┐   │
│  │              CTGAN Model (SDV)                     │   │
│  │   - Train on Crop Recommendation Dataset           │   │
│  │   - Generate Synthetic Data                       │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### Authentication & User Management
- 🔐 **Login/Register** with SQLite database
- 🔒 **Password hashing** using SHA-256
- 👥 **Role-based access** (Admin / Farmer)
- 💰 **Subscription plans** (Free / Premium)

### For Admins
- 🔧 **Train CTGAN Model** with configurable epochs
- 📊 **Generate Synthetic Data** (customizable rows)
- 👥 **User Management** (view, upgrade plans)
- 📚 **Data Statistics** (real vs synthetic comparison)
- 📥 **CSV Download** of generated datasets
- 📈 **Correlation Heatmaps** using Plotly

### For Farmers
- 🌾 **Crop Recommendations** - 22 crops supported
- 🌡️ **Optimal Temperature Range**
- 💧 **Optimal Humidity**
- ⚗️ **Optimal pH Range**
- 🌧️ **Rainfall Requirements**
- 🚿 **Water Level** (High/Medium/Low)
- 🧪 **Fertilizer Level** (High/Medium/Low)
- 📥 **CSV Export** of recommendations

### Monetization
| Feature | Free Plan | Premium Plan |
|---------|----------|--------------|
| Daily Quota | 100 rows | Unlimited |
| Crop Recommendations | ✅ | ✅ |
| CSV Download | ✅ | ✅ |
| Advanced Statistics | ❌ | ✅ |
| Priority Support | ❌ | ✅ |

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** - Web framework
- **SQLite** - Database
- **SDV** - Synthetic Data Vault (CTGAN)
- **Pandas/NumPy** - Data processing
- **Plotly** - Data visualization

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- pip

### Steps

```bash
# Clone repository
git clone <repository-url>
cd SynthAI

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

---

## 📁 Project Structure

```
SynthAI/
├── app.py                 # Main Streamlit app
├── main.py                # Entry point
├── requirements.txt     # Dependencies
├── README.md            # Documentation
├── data/
│   ├── Crop_recommendation.csv  # Original dataset
│   └── agroai.db        # SQLite database
├── src/
│   ├── ctgan_model.py  # CTGAN model wrapper
│   ├── database.py     # Database management
│   ├── recommender.py  # Crop recommendations
│   ├── data_loader.py  # Data loading
│   └── generator.py   # Statistics utilities
├── models/             # Saved CTGAN models
└── outputs/           # Generated datasets
```

---

## 👨‍💻 Usage Flow

### Admin Login
1. **Username**: `admin`
2. **Password**: `admin123`

### Admin Features
1. Login with admin credentials
2. Navigate to Admin Dashboard
3. Train CTGAN model
4. Generate synthetic data
5. View statistics
6. Manage users

### Farmer Flow
1. Register new account
2. Login with credentials
3. Get crop recommendations
4. Download CSV
5. Generate synthetic data (limited by quota)

---

## 🤖 CTGAN Explanation

**What is CTGAN?**

CTGAN (Conditional Tabular GAN) is a deep learning model that learns the statistical distribution of tabular data and generates realistic synthetic samples.

**Why CTGAN?**
- ✅ Preserves correlations between features
- ✅ Handles mixed data types
- ✅ Maintains statistical properties
- ✅ Industry-standard for tabular data

---

## 📊 Screenshots

*[Add screenshots here]*

### Login Page
```

```

### Admin Dashboard
```

```

### Farmer Dashboard
```

```

---

## 📝 License

MIT License

---

## 🙏 Acknowledgments

- [SDV](https://sdv.dev) - Synthetic Data Vault
- [Streamlit](https://streamlit.io) - Web framework
- [Plotly](https://plotly.com) - Data visualization

---

## 📧 Contact

For questions or support, please open an issue.

---

<div align="center">

**🌱 AgroAI - Growing Smart Agriculture with AI 🌱**

</div>