"""Business Logic Layer — role-based access control rules."""

ROLE_HIERARCHY = {
    "admin": {"priority": 100, "label": "Admin"},
    "company": {"priority": 50, "label": "Company"},
    "farmer": {"priority": 10, "label": "Farmer"},
}

# Pages accessible per role
ROLE_PAGES = {
    "admin": [
        "admin_home", "admin_users", "admin_training", "admin_models",
        "admin_model_details", "admin_augmentation", "model_comparison",
        "generate_data", "datasets", "dataset_viewer", "data_evaluation",
        "history", "subscription",
    ],
    "company": [
        "company_home", "company_augment", "generate_data", "datasets",
        "dataset_viewer", "data_evaluation", "model_comparison", "history",
        "subscription",
    ],
    "farmer": [
        "farmer_home", "farmer_predict", "farmer_comparison",
        "farmer_requirements", "crop_conditions", "conditions_crop",
        "history", "subscription",
    ],
}


class AccessControl:
    """Stateless access-permission rules."""

    @staticmethod
    def can_access_page(role: str, page_key: str) -> bool:
        pages = ROLE_PAGES.get(role, [])
        return page_key in pages

    @staticmethod
    def can_manage_users(current_role: str) -> bool:
        return current_role == "admin"

    @staticmethod
    def can_train_models(role: str) -> bool:
        return role == "admin"

    @staticmethod
    def can_generate_data(role: str) -> bool:
        return role in ("admin", "company")

    @staticmethod
    def can_augment_data(role: str) -> bool:
        return role in ("admin", "company")

    @staticmethod
    def can_predict(role: str) -> bool:
        return role == "farmer"

    @staticmethod
    def can_view_history(role: str) -> bool:
        return role in ("admin", "company", "farmer")

    @staticmethod
    def priority(role: str) -> int:
        return ROLE_HIERARCHY.get(role, {}).get("priority", 0)
