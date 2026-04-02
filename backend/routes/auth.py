from fastapi import APIRouter, HTTPException, Depends
from backend.connection.db_connection import get_cursor
from backend.schema.user import UserCreate, UserLogin, UserOut
from backend.services.auth_service import hash_password, verify_password, create_token

router = APIRouter()

@router.post("/signup", response_model=UserOut, status_code=201)
def signup(payload: UserCreate):
    with get_cursor(commit=True) as cur:
        cur.execute("SELECT id FROM users WHERE email = %s", (payload.email,))
        if cur.fetchone():
            raise HTTPException(status_code=409, detail="Email already exists")
        cur.execute(
            """
            INSERT INTO users (name, email, password_hash, role, contact)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, name, email, role, created_at
            """,
            (payload.name, payload.email, hash_password(payload.password),
             payload.role, payload.contact),
        )
        return dict(cur.fetchone())

@router.post("/login")
def login(payload: UserLogin):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM users WHERE email = %s", (payload.email,))
        user = cur.fetchone()
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": str(user["id"]), "role": user["role"]})
    return {"access_token": token, "token_type": "bearer",
            "user": {"id": user["id"], "name": user["name"],
                     "email": user["email"], "role": user["role"]}}