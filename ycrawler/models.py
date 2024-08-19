from pydantic import BaseModel


class News(BaseModel):
    url: str
    file_path: str


class Comment(BaseModel):
    url: str
    news_id: str
