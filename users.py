from pydantic import BaseModel

class UserInDB(BaseModel):
    username: str
    password: str
    role: str

MOCK_USERS = {
    "radarshi": UserInDB(
        username="radarshi",
        password="admin001",
        role="admin"
    ),
    "alice": UserInDB(
        username="alice",
        password="alice004",
        role="hr"
    ),
    "shyam": UserInDB(
        username="shyam",
        password="shyam003",
        role="finance"
    ),
    "kartik": UserInDB(
        username="kartik",
        password="kartik002",
        role="tech"
    )
}