from fastapi import FastAPI, UploadFile, Form, HTTPException, \
                    Depends, Header, File
from requests import Request
from counter.utility.auth import *
from counter.utility.logger import logger

from fastapi_limiter import FastAPILimiter
import time
from counter import config

# Create a FastAPI app
app = FastAPI()

count_action = config.get_count_action()

# @app.middleware("http")
# async def add_rate_limiting_header(request: Request, call_next):
#     await limiter.consume(request)
#     response = await call_next(request)
#     response.headers["X-RateLimit-Limit"] = str(limiter.rate_limit)
#     response.headers["X-RateLimit-Remaining"] = str(limiter.remaining)
#     return response


@app.middleware("http")
async def set_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Frame-Options"] = "DENY"
    return response

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if user is None or not pwd_context.verify(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

rate_limit_dict = {}

# Define a rate limiting decorator
def rate_limit(limit: int, per: int):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            client_ip = args[0].client.host  # Get the client's IP address

            # Check if the client's IP is in the rate_limit_dict
            if client_ip in rate_limit_dict:
                current_time = time.time()
                request_list = rate_limit_dict[client_ip]

                # Remove requests that are older than the rate limit window
                request_list = [req for req in request_list if current_time - req < per]

                # Check if the client has exceeded the rate limit
                if len(request_list) >= limit:
                    raise HTTPException(status_code=429, detail="Rate limit exceeded")

                request_list.append(current_time)
                rate_limit_dict[client_ip] = request_list
            else:
                rate_limit_dict[client_ip] = [time.time()]

            return await func(*args, **kwargs)

        return wrapper

    return decorator

# Protected route with authentication
@app.get("/protected-route/")
@rate_limit(limit=5, per=60)
async def protected_route(user: User = Depends(get_current_user)):
    return {"message": "This is a protected route", "user": user}

@app.post("/predict/")
@rate_limit(limit=5, per=60)
async def predict_objects(
    image: UploadFile = File(...),
    threshold: float = Form(...),
):
    try:
        # Your object detection code here
        count_response = count_action.execute(image.file, threshold)
        # Log a message
        logger.info(f"Object detection completed successfully for image: {image.filename}")

        # Return predictions
        return {"message": f"Object detection completed.{count_response}"}

    except Exception as e:
        # Log an error message
        logger.error(f"Error in object detection: {str(e)}")

        # Return an error response
        raise HTTPException(status_code=500, detail="Internal server error")
