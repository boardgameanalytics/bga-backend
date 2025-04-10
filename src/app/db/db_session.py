"""
db_session.py - Module for creating a read-only SQLAlchemy session
for the boardgame analytics database.
"""


import contextlib
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.ext.declarative import declarative_base

# Create base class for declarative models
Base = declarative_base()


class DatabaseSession:
    """
    Class for managing database connections and sessions.
    Provides read-only access to the boardgame analytics database.
    """

    def __init__(self, connection_string: str) -> None:
        """
        Initialize the database session manager.

        :param connection_string: Database connection string.
        """
        self.connection_string: str = connection_string
        self.engine: Engine = self._create_engine()
        self.Session: scoped_session[Session] = self._create_session_factory(self.engine)

    def _create_engine(self) -> Engine:
        """
        Create SQLAlchemy engine with read-only configuration.

        :return Engine: Configured SQLAlchemy engine
        """
        return create_engine(
            self.connection_string,
            connect_args={"options": "-c default_transaction_read_only=on"}
        )

    @staticmethod
    def _create_session_factory(engine: Engine) -> scoped_session[Session]:
        """
        Create a session factory and wrap it in a scoped_session.

        :return scoped_session[Session]: Thread-local session factory
        """
        session_factory = sessionmaker(bind=engine)
        return scoped_session(session_factory)

    def get_session(self) -> Session:
        """
        Get a new session object.

        :return Session: SQLAlchemy session object
        """
        return self.Session()

    def close(self) -> None:
        """
        Clean up resources used by this database session manager.
        """
        self.Session.remove()
        self.engine.dispose()

    def __del__(self) -> None:
        """
        Destructor to automatically clean up resources when the object is garbage collected.
        Note: It's still better to call close() explicitly when you're done with the connection.
        """
        with contextlib.suppress(Exception):
            self.close()
