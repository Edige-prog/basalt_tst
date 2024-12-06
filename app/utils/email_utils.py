from app.config import MAIL_PASSWORD, MAIL_USERNAME
from fastapi import HTTPException
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from starlette.responses import JSONResponse


# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME = MAIL_USERNAME,
    MAIL_PASSWORD = MAIL_PASSWORD,
    MAIL_FROM = MAIL_USERNAME,
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_FROM_NAME="Basalt",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def send_email(recipient: EmailStr, subject: str, body: str) -> JSONResponse:
    html = f"""<p>{body}</p> """

    # Create the message object
    message = MessageSchema(
        subject=subject,
        recipients=[recipient],
        body=html,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    
    try:
        # Send email
        await fm.send_message(message)
        return JSONResponse(status_code=200, content={"message": "Email has been sent successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

