======================================================================
  SynthAI — تصميم قاعدة البيانات الموحدة (SQLite Schema)
  يجمع: SQLite الحالي + جميع جداول localStorage
======================================================================

==========================
1. جدول: users
   الغرض: حسابات المستخدمين — يجمع users من SQLite و localStorage
==========================
CREATE TABLE IF NOT EXISTS users (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    username            TEXT    UNIQUE NOT NULL,
    email               TEXT    UNIQUE NOT NULL,
    password_hash       TEXT    NOT NULL,              -- SHA-256
    role                TEXT    NOT NULL DEFAULT 'farmer',  -- admin | farmer | company
    plan                TEXT    NOT NULL DEFAULT 'free',     -- free | pro | premium
    is_active           INTEGER NOT NULL DEFAULT 1,         -- 1=نشط, 0=معطل
    attempts            INTEGER NOT NULL DEFAULT 0,         -- عدد محاولات اليوم
    last_reset_date     TEXT,                               -- آخر تاريخ إعادة تعيين (YYYY-MM-DD)
    subscription_expires_at TEXT,                           -- تاريخ انتهاء الاشتراك (ISO)
    created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- المستخدم الافتراضي للمشروع
-- admin / admin123 (password_hash: SHA-256('admin123'))
-- سيتم إدراجه في seed data


==========================
2. جدول: user_settings
   الغرض: إعدادات المستخدم — يحل محل synthai_lang + synthai_api_available
==========================
CREATE TABLE IF NOT EXISTS user_settings (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,
    setting_key         TEXT    NOT NULL,      -- 'language' | 'api_available' | إلخ
    setting_value       TEXT    NOT NULL,
    UNIQUE(user_id, setting_key),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


==========================
3. جدول: models
   الغرض: النماذج المدربة — يحل محل synthai_models
==========================
CREATE TABLE IF NOT EXISTS models (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,               -- من أنشأ النموذج
    name                TEXT    NOT NULL,
    status              TEXT    NOT NULL DEFAULT 'in_progress',  -- in_progress | trained | failed
    is_production       INTEGER NOT NULL DEFAULT 0,     -- 1=نموذج إنتاجي (يحل محل synthai_production_model)
    config_epochs       INTEGER NOT NULL DEFAULT 10,
    config_batch_size   INTEGER NOT NULL DEFAULT 32,
    config_learning_rate REAL   NOT NULL DEFAULT 0.0002,
    dataset_file_name   TEXT,
    dataset_original_rows INTEGER DEFAULT 0,
    dataset_original_cols INTEGER DEFAULT 0,
    dataset_headers     TEXT,                           -- JSON array: ['N','P','K',...]
    cleaning_report     TEXT,                           -- JSON: تقرير تنظيف البيانات
    trained_model_path  TEXT,                           -- مسار ملف النموذج المدرب (إن وجد)
    evaluation          TEXT,                           -- JSON: تقييم النموذج النهائي
    created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


==========================
4. جدول: model_versions
   الغرض: إصدارات النموذج — يحل محل versions[] داخل synthai_models
==========================
CREATE TABLE IF NOT EXISTS model_versions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id            INTEGER NOT NULL,
    version_number      INTEGER NOT NULL,           -- 1, 2, 3, ...
    version_type        TEXT    NOT NULL DEFAULT 'initial',  -- initial | retrain
    status              TEXT    NOT NULL DEFAULT 'in_progress',  -- in_progress | trained | failed
    config_epochs       INTEGER NOT NULL DEFAULT 10,
    config_batch_size   INTEGER NOT NULL DEFAULT 32,
    config_learning_rate REAL   NOT NULL DEFAULT 0.0002,
    dataset_file_name   TEXT,
    dataset_original_rows INTEGER DEFAULT 0,
    dataset_original_cols INTEGER DEFAULT 0,
    dataset_headers     TEXT,                       -- JSON array
    cleaning_report     TEXT,                       -- JSON
    evaluation          TEXT,                       -- JSON: التقييم الخاص بهذا الإصدار
    created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(model_id, version_number),
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);


==========================
5. جدول: model_datasets
   الغرض: بيانات التدريب النظيفة لكل نموذج — يحل محل synthai_model_data_{id}
==========================
CREATE TABLE IF NOT EXISTS model_datasets (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id            INTEGER NOT NULL,
    version_id          INTEGER,                    -- nullable: قد يكون للنسخة الأحدث
    headers             TEXT    NOT NULL,            -- JSON array
    row_count           INTEGER NOT NULL DEFAULT 0,
    data_json           TEXT    NOT NULL,            -- JSON array of objects (كل الصفوف)
    created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE,
    FOREIGN KEY (version_id) REFERENCES model_versions(id) ON DELETE SET NULL
);


==========================
6. جدول: generations
   الغرض: سجل توليد البيانات الاصطناعية — يحل محل synthai_generations
==========================
CREATE TABLE IF NOT EXISTS generations (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,               -- المستخدم الذي قام بالتوليد
    model_id            INTEGER,                        -- nullable: من أي نموذج (إن وجد)
    model_version       INTEGER,                        -- إصدار النموذج المستخدم
    dataset_type        TEXT    NOT NULL,                -- crop | soil | weather
    dataset_level       TEXT    NOT NULL,                -- Medium | Large | Big Data
    rows_generated      INTEGER NOT NULL DEFAULT 1000,
    status              TEXT    NOT NULL DEFAULT 'completed',
    headers             TEXT    NOT NULL,                -- JSON array
    preview_data        TEXT,                           -- JSON array (أول 50 صف)
    full_data_stored    INTEGER NOT NULL DEFAULT 0,      -- 1=خُزنت كاملة في generation_data
    validation_report   TEXT,                           -- JSON نتيجة التحقق
    correlation_similarity REAL,                        -- نسبة تشابه الارتباط
    file_url            TEXT,                           -- رابط الملف المحلي
    cloudinary_url      TEXT,                           -- رابط Cloudinary (إن وجد)
    created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE SET NULL
);


==========================
7. جدول: generation_data
   الغرض: تخزين كامل البيانات المولدة (اختياري) — لتجنب إعادة التوليد
==========================
CREATE TABLE IF NOT EXISTS generation_data (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    generation_id       INTEGER NOT NULL UNIQUE,
    row_count           INTEGER NOT NULL DEFAULT 0,
    data_json           TEXT    NOT NULL,               -- JSON array (كل الصفوف)
    file_path           TEXT,                           -- مسار ملف CSV (إن وُجد على القرص)
    created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (generation_id) REFERENCES generations(id) ON DELETE CASCADE
);


==========================
8. جدول: augmentations
   الغرض: سجل زيادة البيانات — يحل محل synthai_augmentations
==========================
CREATE TABLE IF NOT EXISTS augmentations (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,
    file_name           TEXT    NOT NULL,               -- اسم الملف الأصلي
    original_rows       INTEGER NOT NULL DEFAULT 0,
    augmented_rows      INTEGER NOT NULL DEFAULT 0,     -- إجمالي الصفوف بعد الزيادة
    multiplier          INTEGER NOT NULL DEFAULT 2,      -- 2 | 5 | 10
    dataset_type        TEXT,                            -- crop | soil | weather | generic
    headers             TEXT    NOT NULL,                -- JSON array
    quality_score       INTEGER DEFAULT 0,               -- 0-100
    quality_label       TEXT    DEFAULT 'N/A',            -- Excellent | Good | Fair | Poor
    correlation_similarity REAL,
    original_stats      TEXT,                           -- JSON
    augmented_stats     TEXT,                           -- JSON
    preview_data        TEXT,                           -- JSON (أول 50 صف)
    created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


==========================
9. جدول: predictions
   الغرض: سجل التوقعات (دمج SQLite predictions + synthai_history)
==========================
CREATE TABLE IF NOT EXISTS predictions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,
    prediction_type     TEXT    NOT NULL,                -- crop_conditions | conditions_crop | data_generation
    input_data          TEXT    NOT NULL,                -- JSON: {'N':50, 'P':40, ...}
    output_result       TEXT    NOT NULL,                -- JSON: [{crop:'rice', match:95}, ...]
    crop_search         TEXT,                           -- اسم المحصول (للبحث السريع)
    prediction_date     TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


==========================
10. جدول: payments
    الغرض: سجل المدفوعات والاشتراكات — يحل محل synthai_payments
==========================
CREATE TABLE IF NOT EXISTS payments (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,
    plan_id             TEXT    NOT NULL,                -- free | pro | premium
    plan_name           TEXT    NOT NULL,
    price               REAL    NOT NULL DEFAULT 0,
    status              TEXT    NOT NULL DEFAULT 'active', -- active | expired | cancelled
    subscribed_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    expires_at          TEXT    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


==========================
11. جدول: usage_logs
    الغرض: تتبع استخدام النظام (يُحتفظ بالجدول الحالي)
==========================
CREATE TABLE IF NOT EXISTS usage_logs (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,
    action_type         TEXT    NOT NULL DEFAULT 'generation', -- generation | prediction | augmentation | training
    rows_affected       INTEGER DEFAULT 0,
    created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


==========================
12. جدول: crops
    الغرض: قائمة المحاصيل الأساسية (22 محصولاً) — يحل محل
    src/recommender.py (قائمة crops) + recommendation.js (قائمة crops)
==========================
CREATE TABLE IF NOT EXISTS crops (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name_en             TEXT    UNIQUE NOT NULL,        -- rice, maize, cotton, ...
    name_ar             TEXT,                           -- أرز، ذرة، قطن، ...
    name_fr             TEXT,                           -- riz, maïs, coton, ...
    category            TEXT,                           -- grain | fruit | legume | vegetable | oil
    is_algerian         INTEGER NOT NULL DEFAULT 0,     -- 1=محصول جزائري (للواجهة الفرنسية)
    created_at          TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- الـ 22 محصولاً من Crop_recommendation.csv
INSERT INTO crops (name_en, name_ar, name_fr, category, is_algerian) VALUES
('rice',        'أرز',         'riz',          'grain',  0),
('maize',       'ذرة',         'maïs',         'grain',  1),
('cotton',      'قطن',         'coton',        'fibre',  0),
('jute',        'جوت',         'jute',         'fibre',  0),
('coffee',      'بن',          'café',         'other',  0),
('banana',      'موز',         'banane',       'fruit',  0),
('mango',       'مانجو',       'mangue',       'fruit',  0),
('grapes',      'عنب',         'raisin',       'fruit',  0),
('apple',       'تفاح',        'pomme',        'fruit',  0),
('coconut',     'جوز هند',     'noix de coco', 'fruit',  0),
('chickpea',    'حمص',         'pois chiche',  'legume', 1),
('lentil',      'عدس',         'lentille',     'legume', 1),
('blackgram',   'جرام أسود',   'haricot noir', 'legume', 0),
('kidneybeans', 'فاصوليا حمراء','haricot rouge','legume', 0),
('pigeonpeas',  'بازلاء حمام',  'pois pigeon',  'legume', 0),
('muskmelon',   'شمام',        'melon',        'fruit',  1),
('watermelon',  'بطيخ',        'pastèque',     'fruit',  1),
('orange',      'برتقال',      'orange',       'fruit',  1),
('papaya',       'باباي',       'papaye',       'fruit',  0),
('pomegranate', 'رمان',        'grenade',      'fruit',  1),
('mungbean',    'ماش',         'haricot mungo', 'legume', 0),
('mothbeans',    'فول العثة',   'haricot papillon', 'legume', 0);


==========================
13. جدول: crop_requirements
    الغرض: المتطلبات المثلى لنمو كل محصول — يحل محل
    data.js:CROPS (النطاقات المثلى) + src/recommender.py (get_crop_stats)
==========================
CREATE TABLE IF NOT EXISTS crop_requirements (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    crop_id             INTEGER NOT NULL UNIQUE,

    -- العناصر الغذائية
    n_min               REAL,       n_max               REAL,
    p_min               REAL,       p_max               REAL,
    k_min               REAL,       k_max               REAL,

    -- الظروف المناخية
    temperature_min     REAL,       temperature_max     REAL,
    humidity_min        REAL,       humidity_max        REAL,
    ph_min              REAL,       ph_max              REAL,
    rainfall_min        REAL,       rainfall_max        REAL,

    -- مستويات الري والتسميد (نصية)
    water_level         TEXT,       -- Low | Medium | High
    fertilizer_level    TEXT,       -- Low | Medium | High

    created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE
);

-- إدراج متطلبات الـ 22 محصولاً (من data.js + recommender.py)
INSERT INTO crop_requirements (crop_id, n_min,n_max, p_min,p_max, k_min,k_max,
    temperature_min,temperature_max, humidity_min,humidity_max, ph_min,ph_max,
    rainfall_min,rainfall_max, water_level,fertilizer_level) VALUES

-- rice
(1,  45,105, 35,65,  35,55,  20,35, 70,95, 5,7,   100,350, 'High','Medium'),
-- maize
(2,  55,110, 40,85,  25,65,  18,35, 55,85, 5,7,   50,200,  'Medium','High'),
-- cotton
(3,  50,125, 40,90,  25,55,  20,40, 50,80, 5,8,   50,180,  'Medium','High'),
-- jute
(4,  75,120, 30,85,  30,80,  20,38, 70,90, 6,7,   150,300, 'High','Medium'),
-- coffee
(5,  50,110, 40,80,  25,55,  18,30, 65,85, 5,7,   100,300, 'Medium','Medium'),
-- banana
(6,  70,120, 45,90,  30,70,  25,38, 70,90, 5,7,   100,250, 'High','High'),
-- mango
(7,  35,90,  25,70,  20,55,  20,38, 50,85, 5,7,   50,200,  'Low','Medium'),
-- grapes
(8,  40,100, 35,80,  25,55,  15,35, 45,75, 5,7,   50,150,  'Low','Medium'),
-- apple
(9,  30,80,  25,60,  20,45,  5,20,  50,80, 5,7,   100,200, 'Medium','Low'),
-- coconut
(10, 40,90,  30,70,  25,55,  25,35, 70,95, 5,8,   150,350, 'High','Medium'),
-- chickpea
(11, 30,80,  35,75,  20,50,  15,30, 40,70, 6,8,   50,150,  'Low','Low'),
-- lentil
(12, 25,70,  30,65,  20,45,  10,30, 40,70, 5,7,   50,150,  'Low','Low'),
-- blackgram
(13, 20,60,  25,60,  15,40,  20,35, 50,75, 6,8,   50,150,  'Low','Low'),
-- kidneybeans
(14, 35,80,  30,70,  20,50,  15,30, 45,70, 5,7,   50,150,  'Low','Medium'),
-- pigeonpeas
(15, 30,70,  25,60,  20,45,  20,35, 50,75, 5,8,   50,150,  'Low','Low'),
-- muskmelon
(16, 40,90,  30,70,  25,55,  20,35, 60,85, 5,7,   100,250, 'Medium','Medium'),
-- watermelon
(17, 45,100, 35,75,  30,65,  20,35, 60,85, 5,7,   100,250, 'Medium','Medium'),
-- orange
(18, 35,80,  25,65,  20,50,  15,35, 50,80, 5,7,   100,200, 'Medium','Medium'),
-- papaya
(19, 40,90,  30,70,  25,55,  20,35, 60,85, 5,7,   100,250, 'Medium','Medium'),
-- pomegranate
(20, 35,80,  25,60,  20,50,  15,35, 40,70, 5,7,   50,200,  'Low','Low'),
-- mungbean
(21, 25,65,  25,60,  15,40,  20,35, 50,75, 6,8,   50,150,  'Low','Low'),
-- mothbeans
(22, 20,55,  20,55,  15,35,  20,35, 45,70, 6,8,   50,150,  'Low','Low');


==========================
14. جدول: crop_recommendations
    الغرض: تخزين نتائج التوصيات السابقة لكل مستخدم (سجل توصيات)
==========================
CREATE TABLE IF NOT EXISTS crop_recommendations (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,
    input_data          TEXT    NOT NULL,            -- JSON: {'N':50, 'P':40, 'K':30, 'temperature':25, ...}
    results             TEXT    NOT NULL,            -- JSON: [{crop_id:1, match_pct:95.2}, {crop_id:2, match_pct:88.5}, ...]
    top_crop_id         INTEGER,                    -- المحصول الأوصى به
    created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (top_crop_id) REFERENCES crops(id) ON DELETE SET NULL
);


==========================
15. جدول: soil_textures
    الغرض: أنواع التربة وخواصها — يحل محل data.js:SOIL_TEXTURES
==========================
CREATE TABLE IF NOT EXISTS soil_textures (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name_en             TEXT    UNIQUE NOT NULL,     -- sandy, loam, clay, silt, peat
    name_ar             TEXT,
    name_fr             TEXT,
    om_min              REAL,   om_max              REAL,
    moisture_min        REAL,   moisture_max        REAL,
    bulk_density        REAL,
    drainage            TEXT,                       -- high | medium | low
    nutrient_retention  TEXT,                       -- high | medium | low
    created_at          TEXT    NOT NULL DEFAULT (datetime('now'))
);

INSERT INTO soil_textures (name_en, name_ar, name_fr, om_min,om_max, moisture_min,moisture_max, bulk_density, drainage, nutrient_retention) VALUES
('sandy', 'رملية', 'sableuse',     0.3,1.5,  5,20,   1.6, 'high',   'low'),
('loam',  'طفالية', 'limoneuse',  1.5,4.0,  20,40,  1.3, 'medium', 'medium'),
('clay',  'طينية', 'argileuse',   2.0,5.5,  35,60,  1.1, 'low',    'high'),
('silt',  'غرينية', 'silt',       1.0,3.5,  25,45,  1.2, 'medium', 'medium'),
('peat',  'خثية', 'tourbeuse',    4.0,8.0,  40,75,  0.8, 'low',    'high');


==========================
16. جدول: weather_zones
    الغرض: المناطق المناخية — يحل محل data.js:WEATHER_PATTERNS
==========================
CREATE TABLE IF NOT EXISTS weather_zones (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    zone_key            TEXT    UNIQUE NOT NULL,     -- tropical_rainy, tropical_dry, ...
    name_ar             TEXT,
    name_fr             TEXT,
    temp_min            REAL,   temp_max            REAL,
    hum_min             REAL,   hum_max             REAL,
    precip_min          REAL,   precip_max          REAL,
    wind_min            REAL,   wind_max            REAL,
    pressure_min        REAL,   pressure_max        REAL,
    cloud_min           REAL,   cloud_max           REAL,
    created_at          TEXT    NOT NULL DEFAULT (datetime('now'))
);

INSERT INTO weather_zones (zone_key, name_ar, name_fr, temp_min,temp_max, hum_min,hum_max, precip_min,precip_max, wind_min,wind_max, pressure_min,pressure_max, cloud_min,cloud_max) VALUES
('tropical_rainy',  'مداري ممطر', 'tropical humide',  22,35, 65,95,  100,350, 2,15,  1005,1015, 60,100),
('tropical_dry',    'مداري جاف',  'tropical sec',     25,40, 30,55,  5,50,   5,25,  1008,1018, 0,30),
('temperate_humid', 'معتدل رطب',  'tempéré humide',   10,28, 55,85,  50,200, 5,20,  1010,1025, 40,85),
('temperate_dry',   'معتدل جاف',  'tempéré sec',      5,25,  30,50,  10,80,  10,30, 1012,1028, 0,40),
('mediterranean',   'متوسطي',     'méditerranéen',    15,32, 40,70,  20,120, 5,20,  1010,1022, 10,60),
('arid',            'جاف قاحل',   'aride',            30,48, 10,30,  0,30,   10,40, 1008,1018, 0,15),
('highland',        'مرتفع',      'montagnard',       2,20,  40,80,  30,150, 5,25,  850,950,  30,80);


======================================================================
ملخص جميع الجداول (16 جدولاً)
======================================================================

Basic Tables (بيانات أساسية):
  1. users           — المستخدمون
  2. user_settings   — إعدادات المستخدم
  3. sessions        — جلسات تسجيل الدخول
  4. crops           — المحاصيل (22 محصولاً)
  5. crop_requirements  — المتطلبات المثلى لكل محصول
  6. soil_textures   — أنواع التربة (5 أنواع)
  7. weather_zones   — المناطق المناخية (7 مناطق)

Training Tables (التدريب):
  8. models          — النماذج المدربة
  9. model_versions  — إصدارات النموذج
 10. model_datasets  — بيانات التدريب النظيفة
 11. model_status    — حالة النموذج على مستوى النظام

Data Tables (البيانات المولدة):
 12. generations     — سجل توليد البيانات الاصطناعية
 13. generation_data — البيانات المولدة كاملة
 14. augmentations   — سجل زيادة البيانات

Activity Tables (النشاط):
 15. predictions     — سجل التوقعات
 16. crop_recommendations — سجل توصيات المحاصيل
 17. payments        — المدفوعات والاشتراكات
 18. usage_logs      — تتبع الاستخدام


======================================================================
علاقات المفاتيح الخارجية الكاملة
======================================================================

users (1) ──< user_settings (N)          ON DELETE CASCADE
users (1) ──< sessions (N)               ON DELETE CASCADE
users (1) ──< models (N)                 ON DELETE CASCADE
models (1) ──< model_versions (N)        ON DELETE CASCADE
models (1) ──< model_datasets (N)        ON DELETE CASCADE
model_versions (1) ──< model_datasets (N) ON DELETE SET NULL
users (1) ──< generations (N)            ON DELETE CASCADE
models (1) ──< generations (N)           ON DELETE SET NULL
generations (1) ──< generation_data (1)  ON DELETE CASCADE
users (1) ──< augmentations (N)          ON DELETE CASCADE
users (1) ──< predictions (N)            ON DELETE CASCADE
users (1) ──< crop_recommendations (N)   ON DELETE CASCADE
crops (1) ──< crop_recommendations (N)   ON DELETE SET NULL
crops (1) ──< crop_requirements (1)      ON DELETE CASCADE
users (1) ──< payments (N)               ON DELETE CASCADE
users (1) ──< usage_logs (N)             ON DELETE CASCADE
==========================
CREATE TABLE IF NOT EXISTS model_status (
    id                  INTEGER PRIMARY KEY DEFAULT 1,
    is_trained          INTEGER NOT NULL DEFAULT 0,
    model_type          TEXT    NOT NULL DEFAULT 'CTGAN',
    last_trained        TEXT,
    CHECK (id = 1)      -- صف واحد فقط
);


==========================
13. جدول: sessions
    الغرض: جلسات المستخدم النشطة — يحل محل synthai_session
==========================
CREATE TABLE IF NOT EXISTS sessions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,
    token               TEXT    UNIQUE NOT NULL,         -- رمز الجلسة
    expires_at          TEXT    NOT NULL,
    created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


======================================================================
ملخص العلاقات (ER Diagram)
======================================================================

users ──< user_settings          (1 → N)
users ──< models                 (1 → N)
models ──< model_versions        (1 → N)
models ──< model_datasets        (1 → N)
users ──< generations            (1 → N)
models ──< generations           (1 → N)
generations ──< generation_data  (1 → 1)
users ──< augmentations          (1 → N)
users ──< predictions            (1 → N)
users ──< payments               (1 → N)
users ──< usage_logs             (1 → N)
users ──< sessions               (1 → N)


======================================================================
مقارنة: التخزين الحالي ← التصميم الجديد
======================================================================

التخزين الحالي                        →  الجدول الجديد
─────────────────────────────────────────────────────────────
SQLite: users                         →  users (+ is_active, attempts, last_reset, subscription_expires)
SQLite: usage_logs                    →  usage_logs (+ action_type)
SQLite: model_status                  →  model_status (يُحتفظ به)
SQLite: predictions                   →  predictions (+ crop_search)
SQLite: synthetic_datasets            →  generations

localStorage: synthai_users           →  users (مدمج)
localStorage: synthai_session         →  sessions (جديد)
localStorage: synthai_models          →  models + model_versions + model_datasets
localStorage: synthai_model_data_{id} →  model_datasets
localStorage: synthai_generations     →  generations + generation_data
localStorage: synthai_augmentations   →  augmentations
localStorage: synthai_history         →  predictions (مدمج مع predictions الحالي)
localStorage: synthai_payments        →  payments
localStorage: synthai_production_model→  models.is_production (حقل في models)
localStorage: synthai_lang            →  user_settings
localStorage: synthai_api_available   →  user_settings


======================================================================
Seed Data (المستخدم الافتراضي)
======================================================================

-- سيتم إدراجها بعد إنشاء الجداول
INSERT INTO users (username, email, password_hash, role, plan, is_active)
VALUES ('admin', 'admin@synthai.com',
        '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',  -- SHA-256('admin123')
        'admin', 'premium', 1);

======================================================================
