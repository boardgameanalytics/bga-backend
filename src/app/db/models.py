from sqlalchemy import Column, Float, ForeignKey, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text

Base = declarative_base()


class GameDetails(Base):  # type: ignore
    __tablename__ = "game_details"

    game_id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    year_published = Column(Integer)
    avg_rating = Column(Float)
    bayes_rating = Column(Float)
    total_ratings = Column(Integer)
    std_dev_ratings = Column(Float)
    min_players = Column(Integer)
    max_players = Column(Integer)
    min_playtime = Column(Integer)
    max_playtime = Column(Integer)
    min_age = Column(Integer)
    average_weight = Column(Float)
    total_weights = Column(Integer)
    owned_copies = Column(Integer)
    wishlist = Column(Integer)
    popularity = Column(
        Float,
        server_default=text(
            "(LN(ABS((bayes_rating - 5.5) * total_ratings) + 1) * SIGN((bayes_rating - 5.5)))"
        ),
    )

    # Relationships
    mechanics = relationship("GameMechanicLink", back_populates="game")
    categories = relationship("GameCategoryLink", back_populates="game")
    designers = relationship("GameDesignerLink", back_populates="game")
    artists = relationship("GameArtistLink", back_populates="game")
    publishers = relationship("GamePublisherLink", back_populates="game")


class MechanicDetails(Base):  # type: ignore
    __tablename__ = "mechanic_details"

    mechanic_id = Column(Integer, primary_key=True)
    mechanic_name = Column(Text, nullable=False)

    # Relationships
    games = relationship("GameMechanicLink", back_populates="mechanic")


class CategoryDetails(Base):  # type: ignore
    __tablename__ = "category_details"

    category_id = Column(Integer, primary_key=True)
    category_name = Column(Text, nullable=False)

    # Relationships
    games = relationship("GameCategoryLink", back_populates="category")


class ArtistDetails(Base):  # type: ignore
    __tablename__ = "artist_details"

    artist_id = Column(Integer, primary_key=True)
    artist_name = Column(Text, nullable=False)

    # Relationships
    games = relationship("GameArtistLink", back_populates="artist")


class PublisherDetails(Base):  # type: ignore
    __tablename__ = "publisher_details"

    publisher_id = Column(Integer, primary_key=True)
    publisher_name = Column(Text, nullable=False)

    # Relationships
    games = relationship("GamePublisherLink", back_populates="publisher")


class DesignerDetails(Base):  # type: ignore
    __tablename__ = "designer_details"

    designer_id = Column(Integer, primary_key=True)
    designer_name = Column(Text, nullable=False)

    # Relationships
    games = relationship("GameDesignerLink", back_populates="designer")


class GameMechanicLink(Base):  # type: ignore
    __tablename__ = "game_mechanic_link"

    game_id = Column(Integer, ForeignKey("game_details.game_id"), primary_key=True)
    mechanic_id = Column(
        Integer, ForeignKey("mechanic_details.mechanic_id"), primary_key=True
    )

    # Relationships
    game = relationship("GameDetails", back_populates="mechanics")
    mechanic = relationship("MechanicDetails", back_populates="games")


class GameCategoryLink(Base):  # type: ignore
    __tablename__ = "game_category_link"

    game_id = Column(Integer, ForeignKey("game_details.game_id"), primary_key=True)
    category_id = Column(
        Integer, ForeignKey("category_details.category_id"), primary_key=True
    )

    # Relationships
    game = relationship("GameDetails", back_populates="categories")
    category = relationship("CategoryDetails", back_populates="games")


class GameDesignerLink(Base):  # type: ignore
    __tablename__ = "game_designer_link"

    game_id = Column(Integer, ForeignKey("game_details.game_id"), primary_key=True)
    designer_id = Column(
        Integer, ForeignKey("designer_details.designer_id"), primary_key=True
    )

    # Relationships
    game = relationship("GameDetails", back_populates="designers")
    designer = relationship("DesignerDetails", back_populates="games")


class GameArtistLink(Base):  # type: ignore
    __tablename__ = "game_artist_link"

    game_id = Column(Integer, ForeignKey("game_details.game_id"), primary_key=True)
    artist_id = Column(
        Integer, ForeignKey("artist_details.artist_id"), primary_key=True
    )

    # Relationships
    game = relationship("GameDetails", back_populates="artists")
    artist = relationship("ArtistDetails", back_populates="games")


class GamePublisherLink(Base):  # type: ignore
    __tablename__ = "game_publisher_link"

    game_id = Column(Integer, ForeignKey("game_details.game_id"), primary_key=True)
    publisher_id = Column(
        Integer, ForeignKey("publisher_details.publisher_id"), primary_key=True
    )

    # Relationships
    game = relationship("GameDetails", back_populates="publishers")
    publisher = relationship("PublisherDetails", back_populates="games")
