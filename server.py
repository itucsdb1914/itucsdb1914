from Iwent import app
import os

app.config["DATABASE_URI"] = "postgres://jhnpckexbslqcy:ce78071326738d66de8bc98fc93c0c54b43dd4f9eeda2c7345d6730f9b6153bf@ec2-176-34-183-20.eu-west-1.compute.amazonaws.com:5432/dbbdt1ie3k7s0f"

if __name__ == "__main__":
    app.run()
