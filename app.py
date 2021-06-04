from api import API

app = API()


@app.route("/home")
def home(request):
    return "Hello from the HOME page"


@app.route("/about")
class About:
    def get(self, request):
        return "Hello from the ABOUT page"


@app.route("/hello/{name}")
def greeting(request, name):
    return f"Hello, {name}"


@app.route("/hello/lily")
def greeting(request):
    return "KOKOS!"


if __name__ == '__main__':
    app()

