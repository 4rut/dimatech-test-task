import os

config = {
    "DATABASE_URL": "postgresql+asyncpg://myuser:mypassword@db:5432/mydb",
    "SECRET_KEY": os.getenv("SECRET_KEY", "gfdmhghif38yrf9ew0jkf32"),
}
