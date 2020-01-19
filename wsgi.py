from cs261 import app as cs261_app

app = cs261_app.Blueprint.get_app()

if __name__ == "__main__":
    app.run()
