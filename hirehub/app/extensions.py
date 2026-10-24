"""MongoDB connection — reads MONGO_URI and MONGO_DATABASE from Flask app config,
which in turn reads them from the .env file via app/config.py."""
from __future__ import annotations
from pymongo import MongoClient
from pymongo.database import Database


class MongoDB:
    """
    Singleton-style MongoDB wrapper.

    Connection lifecycle:
        MongoDB.init_app(app)   ← called once inside create_app()
        MongoDB.get_db()        ← called anywhere a collection is needed
        MongoDB.close()         ← called on teardown (optional)
    """

    _client: MongoClient | None = None
    _db: Database | None = None

    @classmethod
    def init_app(cls, app) -> None:
        """
        Open a MongoClient using MONGO_URI and MONGO_DATABASE
        from Flask app.config (both values come from .env).
        """
        uri     = app.config["MONGO_URI"]       # e.g. mongodb://localhost:27017
        db_name = app.config["MONGO_DATABASE"]  # e.g. hirehub

        print(f"  [MongoDB] Connecting to  : {uri}")
        print(f"  [MongoDB] Database       : {db_name}")

        cls._client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        cls._db     = cls._client[db_name]

        # Verify the connection is alive
        try:
            cls._client.admin.command("ping")
            print(f"  [MongoDB] Connected ✓   (database: {db_name})")
        except Exception as exc:
            print(f"  [MongoDB] WARNING — could not reach MongoDB: {exc}")

        # Make the db accessible via app.extensions["mongodb"]
        app.extensions["mongodb"] = cls._db

    @classmethod
    def get_db(cls) -> Database:
        """Return the active database.  Raises if init_app() was not called."""
        if cls._db is None:
            raise RuntimeError(
                "MongoDB is not initialised. "
                "Make sure MongoDB.init_app(app) is called inside create_app()."
            )
        return cls._db

    @classmethod
    def close(cls) -> None:
        """Close the connection (useful in tests / teardown)."""
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db     = None
            print("  [MongoDB] Connection closed.")


def get_db() -> Database:
    """Module-level shortcut — used by all repositories."""
    return MongoDB.get_db()
