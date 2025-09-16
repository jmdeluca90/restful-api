import os
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from app.database import get_db
from app import models, auth

router = APIRouter(prefix="/oauth", tags=["oauth"])

config_data = {
    "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", ""),
    "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET", ""),
    "GITHUB_CLIENT_ID": os.getenv("GITHUB_CLIENT_ID", ""),
    "GITHUB_CLIENT_SECRET": os.getenv("GITHUB_CLIENT_SECRET", ""),
    "SECRET_KEY": os.getenv("SECRET_KEY", "secret"),
}
config = Config(environ=config_data)

oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=config("GOOGLE_CLIENT_ID"),
    client_secret=config("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)
oauth.register(
    name='github',
    client_id=config("GITHUB_CLIENT_ID"),
    client_secret=config("GITHUB_CLIENT_SECRET"),
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

@router.get("/login/{provider}")
async def oauth_login(provider: str, request: Request):
    redirect_uri = request.url_for('oauth_callback', provider=provider)
    return await oauth.create_client(provider).authorize_redirect(request, str(redirect_uri))

@router.get("/callback/{provider}")
async def oauth_callback(provider: str, request: Request, db: Session = Depends(get_db)):
    token = await oauth.create_client(provider).authorize_access_token(request)
    if provider == "google":
        userinfo = await oauth.google.parse_id_token(request, token)
        email = userinfo["email"]
        oauth_id = userinfo["sub"]
    elif provider == "github":
        resp = await oauth.github.get('user', token=token)
        profile = resp.json()
        email = profile.get("email")
        oauth_id = str(profile.get("id"))
        if not email:
            # Get email from API if not public
            emails_resp = await oauth.github.get('user/emails', token=token)
            emails = emails_resp.json()
            email = next((e["email"] for e in emails if e["primary"]), None)
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    user = db.query(models.User).filter(models.User.oauth_provider == provider, models.User.oauth_id == oauth_id).first()
    if not user:
        # Register new user
        username = email.split("@")[0]
        user = models.User(username=username, email=email, oauth_provider=provider, oauth_id=oauth_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    access_token = auth.create_access_token(data={"sub": user.username})
    # Redirect to docs with token in query (demo only, use cookies in real apps)
    return RedirectResponse(url=f"/docs?token={access_token}")