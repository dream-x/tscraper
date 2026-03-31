# Authentication

TScraper uses a Telegram **user session** (not a bot token). You need to authenticate once to create a session file.

## First-time Setup

```bash
python auth.py
```

The script will:

1. Ask for your phone number in international format (e.g., `+79123456789`)
2. Send a verification code to your Telegram app
3. Ask you to enter the code
4. If 2FA is enabled, ask for your password
5. Create `my_user_session.session`

!!! important "Session file"
    The `my_user_session.session` file contains your authenticated session.

    - **Never commit** this file to version control
    - **Persist it** across Docker restarts using a volume mount
    - **Back it up** — losing it means re-authenticating

## Re-authentication

If you need to re-authenticate (session expired, account change):

```bash
rm my_user_session.session
python auth.py
```

## Docker Considerations

The session file must be mounted as a volume to persist across container restarts:

```yaml
# docker-compose.yml
volumes:
  - ./my_user_session.session:/app/my_user_session.session
```

!!! tip
    Authenticate **before** starting the Docker container for the first time.
    Run `python auth.py` on your host machine, then start the container with the session file mounted.
