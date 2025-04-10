from unittest.mock import ANY

from pytest_mock import MockerFixture
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from src.app.db.db_session import DatabaseSession


class TestDatabaseSession:
    def test_init(self, mocker: MockerFixture):
        # Arrange
        mock_create_engine = mocker.patch("src.app.db.db_session.create_engine")
        mock_sessionmaker = mocker.patch("src.app.db.db_session.sessionmaker")
        mock_scoped_session = mocker.patch("src.app.db.db_session.scoped_session")
        connection_string = "sqlite:///test.db"

        # Act
        db_session = DatabaseSession("sqlite:///test.db")

        # Assert
        assert db_session.connection_string == connection_string
        mock_create_engine.assert_called_once_with(
            connection_string,
            connect_args={"options": "-c default_transaction_read_only=on"},
        )
        mock_sessionmaker.assert_called_once_with(bind=ANY)
        mock_scoped_session.assert_called_once()

    def test_create_engine(self, mocker: MockerFixture):
        # Arrange
        connection_string = "sqlite:///test.db"
        db_session = DatabaseSession(connection_string)
        mock_create_engine = mocker.patch("src.app.db.db_session.create_engine")

        # Act
        db_session._create_engine()

        # Assert
        mock_create_engine.assert_called_once_with(
            connection_string,
            connect_args={"options": "-c default_transaction_read_only=on"},
        )

    def test_create_session_factory(self, mocker: MockerFixture):
        # Arrange
        mock_engine = mocker.MagicMock(spec=Engine)
        mock_sessionmaker = mocker.patch(
            "src.app.db.db_session.sessionmaker", return_value="mock_sessionmaker"
        )
        mock_scoped_session = mocker.patch(
            "src.app.db.db_session.scoped_session", return_value="mock_scoped_session"
        )

        # Act
        session_factory = DatabaseSession._create_session_factory(mock_engine)

        # Assert
        mock_sessionmaker.assert_called_once_with(bind=mock_engine)
        mock_scoped_session.assert_called_once_with("mock_sessionmaker")
        assert session_factory == "mock_scoped_session"

    def test_get_session(self, mocker: MockerFixture):
        # Arrange
        mock_session = mocker.MagicMock(spec=Session)
        db_session = DatabaseSession("sqlite:///test.db")
        db_session.Session = mocker.MagicMock(return_value=mock_session)  # type: ignore[assignment]

        # Act
        session = db_session.get_session()

        # Assert
        db_session.Session.assert_called_once()  # type: ignore
        assert session == mock_session

    def test_close(self, mocker: MockerFixture):
        # Arrange
        connection_string = "sqlite:///test.db"
        db_session = DatabaseSession(connection_string)
        mock_remove = mocker.patch("src.app.db.db_session.scoped_session.remove")
        mock_dispose = mocker.patch("src.app.db.db_session.Engine.dispose")

        # Act
        db_session.close()

        # Assert
        mock_remove.assert_called_once()
        mock_dispose.assert_called_once()

    def test_del(self, mocker: MockerFixture):
        # Arrange
        connection_string = "sqlite:///test.db"
        db_session = DatabaseSession(connection_string)
        mock_close = mocker.patch("src.app.db.db_session.DatabaseSession.close")

        # Act
        del db_session

        # Assert
        mock_close.assert_called_once()
