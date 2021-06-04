import inspect
import os
import socket

from parse import parse


class API:
    def __init__(self, server_host: str = '127.0.0.1', server_port: int = 8000):
        self.routes = {}

        # Create socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((server_host, server_port))
        self.server_socket.listen(1)
        print('Listening on port %s ...' % server_port)

    def __call__(self):
        while True:
            client_connection, client_address = self.server_socket.accept()

            request = client_connection.recv(1024).decode()
            print(request)

            response = self.handle_request(request)
            client_connection.sendall(response.encode())
            client_connection.close()

    def handle_request(self, request):
        headers = request.split('\n')
        path = headers[0].split()[1]

        handler, kwargs = self.find_handler(request_path=path)

        if handler is not None:
            if inspect.isclass(handler):
                method = headers[0].split()[0]
                handler = getattr(handler(), method.lower(), None)

                if handler is None:
                    raise AttributeError("Method now allowed", method)

            content = handler(request, **kwargs)
            response = 'HTTP/1.0 200 OK\n\n' + content

        else:
            response = self.default_response()

        return response

    def find_handler(self, request_path):
        for path, handler in self.routes.items():
            parse_result = parse(path, request_path)  # TODO: remove usage of external libraries

            if parse_result is not None:
                return handler, parse_result.named

        return None, None

    def route(self, path):
        assert path not in self.routes, "Path already in use."

        def wrapper(handler):
            self.routes[path] = handler
            return handler

        return wrapper

    def default_response(self):
        content = 'HTTP/1.0 404 Not Found\n\n'

        if os.path.exists('templates/404.html'):
            fin = open('templates/404.html')
            file_content = fin.read()
            fin.close()
            return content + file_content

        return content
