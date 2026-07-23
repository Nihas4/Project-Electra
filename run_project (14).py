import http.server
import socketserver
import webbrowser
import threading
import os
import sys

PORT = 8000
FILE_NAME = "electra-demo.html"


class ProjectHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "":
            self.path = "/" + FILE_NAME
        return super().do_GET()

    def log_message(self, format, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()


class ProjectServer:
    def __init__(self, port):
        self.port = port
        self.httpd = None

    def find_available_port(self, attempts=15):
        port = self.port
        for _ in range(attempts):
            try:
                httpd = socketserver.TCPServer(("", port), ProjectHandler)
                self.httpd = httpd
                self.port = port
                return True
            except OSError:
                port += 1
        return False

    def open_browser(self):
        url = "http://localhost:{}/".format(self.port)
        webbrowser.open(url)
        return url

    def start(self):
        if self.httpd is None:
            return False
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            self.httpd.shutdown()
        return True


def get_script_folder():
    return os.path.dirname(os.path.abspath(__file__))


def check_version(folder):
    path = os.path.join(folder, FILE_NAME)
    if not os.path.exists(path):
        print("MISSING: " + FILE_NAME + " is not in " + folder)
        return False
    text = open(path, encoding="utf-8", errors="ignore").read()
    size_kb = round(os.path.getsize(path) / 1024, 1)
    print("Found " + FILE_NAME + " (" + str(size_kb) + " KB)")
    if "Welcome back" in text:
        print("This IS the current version. Good.")
        return True
    if "Have a happy journey" in text:
        print("WARNING: this is an OLD version of the file.")
        print("Delete this electra-demo.html and replace it with the latest download.")
        return False
    print("Unrecognized file contents - not sure which version this is.")
    return False


def main():
    folder = get_script_folder()
    os.chdir(folder)

    ok = check_version(folder)
    if not ok:
        sys.exit()

    server = ProjectServer(PORT)
    found = server.find_available_port()
    if not found:
        print("No available port found.")
        sys.exit(1)

    url = "http://localhost:{}/".format(server.port)
    print("Serving at " + url)
    threading.Timer(0.5, server.open_browser).start()
    server.start()


if __name__ == "__main__":
    main()
