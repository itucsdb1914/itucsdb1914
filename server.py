from Iwent import app
import os

app.config["DATABSE_URI"] = os.getenv("DATABASE_URL")

if __name__ == "__main__":
    app.run()
