from . import app


@app.route('/')
def index():
    return __name__