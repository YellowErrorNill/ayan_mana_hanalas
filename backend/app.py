import os
import hashlib
import secrets

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import ImageType
from pydantic import BaseModel
from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqladmin import Admin, ModelView

#python -m uvicorn app:app --reload

class Base(DeclarativeBase):

  pass


class CarD(Base):

  __tablename__ = "cards"

  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(String(100))
  location: Mapped[str] = mapped_column(String(100), default="")
  description: Mapped[str] = mapped_column(String(500))
  image: Mapped[str] = mapped_column(ImageType(storage=FileSystemStorage(path="uploads"), length=255), default="")


class User(Base):

  __tablename__ = "users"

  id: Mapped[int] = mapped_column(primary_key=True)
  username: Mapped[str] = mapped_column(String(30), unique=True)
  password_hash: Mapped[str] = mapped_column(String(255))
  first_name: Mapped[str] = mapped_column(String(50), default="")
  last_name: Mapped[str] = mapped_column(String(50), default="")


class Token(Base):

  __tablename__ = "tokens"

  id: Mapped[int] = mapped_column(primary_key=True)
  token: Mapped[str] = mapped_column(String(64), unique=True)
  user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))


class SavedPlace(Base):

  __tablename__ = "saved_places"

  id: Mapped[int] = mapped_column(primary_key=True)
  user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
  card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"))
  visited: Mapped[bool] = mapped_column(default=False)


class Place(Base):

  __tablename__ = "places"

  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(String(100))
  category: Mapped[str] = mapped_column(String(30), default="center")
  lat: Mapped[float] = mapped_column()
  lon: Mapped[float] = mapped_column()
  description: Mapped[str] = mapped_column(String(500), default="")
  preset: Mapped[str] = mapped_column(String(50), default="islands#greenDotIcon")
  





engine = create_engine("sqlite:///database.db", echo=True)
Base.metadata.create_all(engine)


with Session(engine) as session:
  if session.scalar(select(Place).limit(1)) is None:
    session.add_all([
      Place(name="пгт Нижний Бестях", category="transport", lat=61.9585, lon=129.9100,
            description="Административный центр улуса, ЖД-вокзал и переправа.",
            preset="islands#blueRailwayIcon"),
      Place(name="село Майя", category="center", lat=61.7370, lon=130.2785,
            description="Крупнейшее село улуса, культурный и исторический центр.",
            preset="islands#greenDotIcon"),
      Place(name="село Тюнгюлю", category="center", lat=62.1965, lon=130.7280,
            description="Крупный населённый пункт на трассе «Колыма».",
            preset="islands#greenDotIcon"),
      Place(name="село Павловск", category="culture", lat=61.8835, lon=129.8390,
            description="Нерюктяйинский наслег, берег реки Лены.",
            preset="islands#orangeLeisureIcon"),
      Place(name="Памятник Василию Манчаары", category="culture", lat=61.958066, lon=129.908433,
            description="Нерюктяйинский наслег, берег реки Лены.",
            preset="islands#orangeLeisureIcon"),
      Place(name="Церковь Благовещения Пресвятой Богородицы", category="culture", lat=61.957356, lon=129.906896,
            description="Нерюктяйинский наслег, берег реки Лены.",
            preset="islands#orangeLeisureIcon"),
      Place(name="Техтюрский музей истории и краеведения", category="culture", lat=61.964720, lon=129.913650,
            description="Нерюктяйинский наслег, берег реки Лены.",
            preset="islands#orangeLeisureIcon"),
    ])
    session.commit()
  

  
  
  
app = FastAPI(title="FastAPI + Vue Template")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def read_root():
    return {"message": "Привет, мир!"}


class AuthData(BaseModel):
    username: str
    password: str
    first_name: str = ""
    last_name: str = ""


def hash_password(password: str, salt: str = "") -> str:
    if not salt:
        salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return f"{salt}${h}"


def verify_password(password: str, password_hash: str) -> bool:
    salt, _ = password_hash.split("$")
    return secrets.compare_digest(hash_password(password, salt), password_hash)


def get_user_by_token(authorization: str, session: Session) -> User:
    token_value = authorization.removeprefix("Bearer ").strip()
    token = session.scalar(select(Token).where(Token.token == token_value))
    if token is None:
        raise HTTPException(status_code=401, detail="Не авторизован")
    return session.get(User, token.user_id)


@app.post("/register")
async def register(data: AuthData):
    with Session(engine) as session:
        if session.scalar(select(User).where(User.username == data.username)):
            raise HTTPException(status_code=400, detail="Пользователь уже существует")
        user = User(
            username=data.username,
            password_hash=hash_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
        )
        session.add(user)
        session.commit()
        return {"message": "Регистрация успешна"}


@app.post("/login")
async def login(data: AuthData):
    with Session(engine) as session:
        user = session.scalar(select(User).where(User.username == data.username))
        if user is None or not verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")
        token = Token(token=secrets.token_hex(32), user_id=user.id)
        session.add(token)
        session.commit()
        return {"token": token.token, "username": user.username}


@app.post("/logout")
async def logout(authorization: str = Header(default="")):
    with Session(engine) as session:
        token_value = authorization.removeprefix("Bearer ").strip()
        token = session.scalar(select(Token).where(Token.token == token_value))
        if token is None:
            raise HTTPException(status_code=401, detail="Не авторизован")
        session.delete(token)
        session.commit()
        return {"message": "Вы вышли"}


@app.get("/me")
async def me(authorization: str = Header(default="")):
    with Session(engine) as session:
        user = get_user_by_token(authorization, session)
        return {"username": user.username}


@app.get("/cards")
async def get_cards():
    with Session(engine) as session:
        cards = session.scalars(select(CarD)).all()
        return [card_to_dict(c) for c in cards]


@app.get("/places")
async def get_places():
    with Session(engine) as session:
        places = session.scalars(select(Place)).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "coords": [p.lat, p.lon],
                "description": p.description,
                "preset": p.preset,
            }
            for p in places
        ]


def card_to_dict(c: CarD) -> dict:
    image = c.image.replace("\\", "/").split("/")[-1] if c.image else ""
    return {
        "id": c.id,
        "name": c.name,
        "location": c.location,
        "description": c.description,
        "image": f"/uploads/{image}" if image else "",
    }


class SavedData(BaseModel):
    card_id: int


@app.post("/saved")
async def save_place(data: SavedData, authorization: str = Header(default="")):
    with Session(engine) as session:
        user = get_user_by_token(authorization, session)
        if session.get(CarD, data.card_id) is None:
            raise HTTPException(status_code=404, detail="Место не найдено")
        existing = session.scalar(
            select(SavedPlace).where(
                SavedPlace.user_id == user.id, SavedPlace.card_id == data.card_id
            )
        )
        if existing is None:
            session.add(SavedPlace(user_id=user.id, card_id=data.card_id))
            session.commit()
        return {"message": "Сохранено"}


@app.get("/profile")
async def profile(authorization: str = Header(default="")):
    with Session(engine) as session:
        user = get_user_by_token(authorization, session)
        saved = session.scalars(
            select(SavedPlace).where(SavedPlace.user_id == user.id)
        ).all()
        want, visited = [], []
        for s in saved:
            card = session.get(CarD, s.card_id)
            if card is None:
                continue
            (visited if s.visited else want).append(card_to_dict(card))
        return {"username": user.username, "want": want, "visited": visited}


@app.post("/saved/{card_id}/visit")
async def mark_visited(card_id: int, authorization: str = Header(default="")):
    with Session(engine) as session:
        user = get_user_by_token(authorization, session)
        saved = session.scalar(
            select(SavedPlace).where(
                SavedPlace.user_id == user.id, SavedPlace.card_id == card_id
            )
        )
        if saved is None:
            raise HTTPException(status_code=404, detail="Место не сохранено")
        saved.visited = True
        session.commit()
        return {"message": "Отмечено как посещённое"}


@app.post("/saved/{card_id}/unvisit")
async def mark_not_visited(card_id: int, authorization: str = Header(default="")):
    with Session(engine) as session:
        user = get_user_by_token(authorization, session)
        saved = session.scalar(
            select(SavedPlace).where(
                SavedPlace.user_id == user.id, SavedPlace.card_id == card_id
            )
        )
        if saved is None:
            raise HTTPException(status_code=404, detail="Место не сохранено")
        saved.visited = False
        session.commit()
        return {"message": "Возвращено в «Хочу побывать»"}


os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


class CarDAdmin(ModelView, model=CarD):
    column_list = [CarD.id, CarD.name, CarD.location, CarD.description, CarD.image]


CarDAdmin.identity = "cards"

admin = Admin(app, engine)
admin.add_view(CarDAdmin)


class SavedPlaceAdmin(ModelView, model=SavedPlace):
    column_list = [SavedPlace.id, SavedPlace.user_id, SavedPlace.card_id, SavedPlace.visited]


SavedPlaceAdmin.identity = "saved"
admin.add_view(SavedPlaceAdmin)


class PlaceAdmin(ModelView, model=Place):
    column_list = [Place.id, Place.name, Place.category, Place.lat, Place.lon, Place.description, Place.preset]


PlaceAdmin.identity = "places"
admin.add_view(PlaceAdmin)





