from dataclasses import dataclass

@dataclass
class Genre:
    id: int
    name: str

@dataclass
class Movie:
    id: int
    title: str
    year: int
    genre_id: int
    rating: float
    description: str
    poster_path: str