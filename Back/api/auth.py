"""Authentification JWT (US-008).

Les comptes sont définis ici pour la démo. Les mots de passe sont stockés
hachés (PBKDF2-SHA256) ; aucune donnée personnelle n'est conservée (RGPD).
Pour ajouter un compte : USERS_EXTRA="login:motdepasse:Nom:Rôle;..." dans .env
"""
from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from logs_service import security_log
from settings import JWT_EXPIRE_HOURS, JWT_SECRET

ALGO = "HS256"
_bearer = HTTPBearer(auto_error=False)


def _hash(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return f"{salt.hex()}${digest.hex()}"


def _verify(password: str, stored: str) -> bool:
    salt_hex, digest_hex = stored.split("$")
    candidate = _hash(password, bytes.fromhex(salt_hex)).split("$")[1]
    return hmac.compare_digest(candidate, digest_hex)


def _build_users() -> dict[str, dict]:
    base = [
        (1, "admin", "admin123", "Marie Dubois", "Responsable Environnement", True),
        (2, "elu", "elu123", "Pierre Lambert", "Élu Municipal", False),
        (3, "demo", "demo", "Jean Martin", "Citoyen", False),
    ]
    extra = os.getenv("USERS_EXTRA", "")
    for i, entry in enumerate(filter(None, extra.split(";")), start=10):
        parts = entry.split(":")
        if len(parts) >= 4:
            base.append((i, parts[0], parts[1], parts[2], parts[3], len(parts) > 4 and parts[4] == "admin"))
    return {
        login: {"id": uid, "username": login, "password_hash": _hash(pwd),
                "name": name, "role": role, "is_admin": admin}
        for uid, login, pwd, name, role, admin in base
    }


USERS = _build_users()


def public_user(u: dict) -> dict:
    return {k: u[k] for k in ("id", "username", "name", "role", "is_admin")}


def authenticate(username: str, password: str, client_ip: str) -> dict:
    user = USERS.get(username)
    if not user or not _verify(password, user["password_hash"]):
        security_log.warning("Échec de connexion pour '%s' depuis %s", username[:50], client_ip)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiants invalides")
    security_log.info("Connexion réussie : %s depuis %s", username, client_ip)
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    token = jwt.encode({"sub": username, "exp": expire}, JWT_SECRET, algorithm=ALGO)
    return {"token": token, "user": public_user(user), "expiresAt": expire.isoformat()}


def current_user(creds: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> dict:
    if not creds:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentification requise")
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[ALGO])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session expirée")
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token invalide")
    user = USERS.get(payload.get("sub", ""))
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Utilisateur inconnu")
    return public_user(user)


def admin_user(user: dict = Depends(current_user)) -> dict:
    if not user["is_admin"]:
        security_log.warning("Accès admin refusé pour %s", user["username"])
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Accès réservé aux administrateurs")
    return user
