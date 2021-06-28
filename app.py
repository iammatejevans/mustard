from api import API
from middleware import Middleware
from utils import render

app = API()


class Pokus:
    meloun = ['meloun1', 'meloun2', 'meloun3']
    true = False
    ananas = 'pineapple'


papaja = 'papayaaaaaaa'

a = Pokus()
meals = {'bramborak': '22kc', 'houska': '5kc'}


@app.route("/home")
def home(request):
    # raise AttributeError('bla')
    return render('home.html', {'pokus': a, 'papaja': papaja, 'my_range': ['1', '2', '3'], 'meals': meals})


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


def custom_exception_handler(request, exception_cls):
    return "Oops! Something went wrong. Please, contact our customer support."


class CustomMiddleware(Middleware):
    def process_request(self, req):
        print('Processing request', req)

    def process_response(self, req, res):
        print('Processing response')


app.add_middleware(CustomMiddleware)


if __name__ == '__main__':
    app()

