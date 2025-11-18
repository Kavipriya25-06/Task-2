# project/db_routers.py


class ReportingRouter:
    """
    Prevent migrations on the 'reporting' database
    (we treat it as read-only / externally managed).
    """

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == "reporting":
            # Never run migrations on reporting DB
            return False
        return None  # use default behavior for others
