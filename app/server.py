import socket
import threading
import argparse
import os
import sys
import gzip
from typing import Union, Optional, Tuple

# Constants for server configuration
DEFAULT_PORT = 4221
BUFFER_SIZE = 4096

class HTTPRequest:
    def __init__(self, raw_request: str):
        self.method = ""
        self.path = ""
        self.headers = {}
        self.body = b""  # Store body as bytes
        self._parse(raw_request)

    def _parse(self, raw_request: str) -> None:
        try:
            # Split the request into headers and body sections
            if '\r\n\r\n' in raw_request:
                headers_section, body = raw_request.split('\r\n\r\n', 1)
            else:
                headers_section, body = raw_request, ''

            header_lines = headers_section.split('\r\n')

            # Get the HTTP method, path, and version from the first line
            self.method, self.path, _ = header_lines[0].split()

            # Parse all headers into a dictionary
            for line in header_lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    self.headers[key.lower().strip()] = value.strip()

            # Convert body to bytes
            self.body = body.encode('utf-8')
        except Exception as e:
            print(f"Error parsing request: {e}")

    def accepts_gzip(self) -> bool:
        # Check if client accepts gzip compression among multiple encoding options
        accept_encoding = self.headers.get('accept-encoding', '')
        # Split encodings by comma and clean up each value
        encodings = [enc.strip().lower() for enc in accept_encoding.split(',')]
        # Return True if gzip is in the accepted encodings
        return 'gzip' in encodings

class FileHandler:
    def __init__(self, base_dir: str):
        # Store the base directory for file operations
        self.base_dir = os.path.abspath(base_dir)

    def is_safe_path(self, filepath: str) -> bool:
        # Verify the file path is within allowed directory
        abs_path = os.path.abspath(filepath)
        return abs_path.startswith(self.base_dir)

    def read_file(self, filename: str) -> Tuple[Optional[bytes], bool]:
        # Read file contents if path is safe
        filepath = os.path.join(self.base_dir, filename)
        if not self.is_safe_path(filepath):
            return None, False

        try:
            with open(filepath, 'rb') as f:
                return f.read(), True
        except:
            return None, False

    def write_file(self, filename: str, content: bytes) -> bool:
        # Write content to file if path is safe
        filepath = os.path.join(self.base_dir, filename)
        if not self.is_safe_path(filepath):
            return False

        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'wb') as f:
                f.write(content)
            return True
        except:
            return False

class HTTPServer:
    def __init__(self, directory: str):
        # Initialize server with a file handler
        self.file_handler = FileHandler(directory)

    def compress_content(self, content: bytes) -> bytes:
        # Compress the content using gzip
        # This is where the actual compression happens
        return gzip.compress(content)

    def make_response(self, status: str, body: Union[str, bytes, None] = "",
                     content_type: str = "text/plain",
                     use_gzip: bool = False) -> bytes:
        # Handle None case
        if body is None:
            body = b""
        # Convert string to bytes if necessary
        elif isinstance(body, str):
            body = body.encode()

        # Compress the body if gzip is requested
        if use_gzip:
            body = self.compress_content(body)

        # Prepare headers
        headers = [
            f"HTTP/1.1 {status}",
            f"Content-Type: {content_type}",
        ]

        # Add Content-Encoding header if using gzip
        if use_gzip:
            headers.append("Content-Encoding: gzip")

        headers.extend([
            f"Content-Length: {len(body)}",
            "",
            ""
        ])

        return '\r\n'.join(headers).encode() + body

    def handle_file_request(self, request: HTTPRequest) -> bytes:
        # Extract filename from path
        filename = request.path[7:]  # Remove '/files/'
        supports_gzip = request.accepts_gzip()

        if not filename:
            return self.make_response("400 Bad Request")

        if request.method == "POST":
            try:
                # Get content length from headers
                content_length = int(request.headers.get('content-length', '0'))
                if content_length == 0:
                    return self.make_response("400 Bad Request")

                # Get content from request body
                content = request.body[:content_length]

                # Write file and return appropriate response
                if self.file_handler.write_file(filename, content):
                    return self.make_response("201 Created")
                return self.make_response("500 Internal Server Error")
            except ValueError:
                return self.make_response("400 Bad Request")

        elif request.method == "GET":
            # Read file and return contents if successful
            content, success = self.file_handler.read_file(filename)
            if success and content is not None:
                return self.make_response(
                    "200 OK",
                    content,
                    "application/octet-stream",
                    use_gzip=supports_gzip
                )
            return self.make_response("404 Not Found")

        return self.make_response("405 Method Not Allowed")

    def handle_request(self, raw_request: str) -> bytes:
        try:
            # Parse the request
            request = HTTPRequest(raw_request)
            supports_gzip = request.accepts_gzip()

            # Handle different request paths
            if request.path.startswith("/files/"):
                return self.handle_file_request(request)

            if request.path.startswith("/echo/"):
                return self.make_response(
                    "200 OK",
                    request.path[6:],
                    use_gzip=supports_gzip
                )

            # Define route handlers
            routes = {
                "/": lambda: self.make_response(
                    "200 OK",
                    "Welcome to the root path!",
                    use_gzip=supports_gzip
                ),
                "/user-agent": lambda: self.make_response(
                    "200 OK",
                    request.headers.get('user-agent', 'Missing User-Agent'),
                    use_gzip=supports_gzip
                )
            }

            # Return response for matching route or 404
            return routes.get(request.path, lambda: self.make_response("404 Not Found"))()

        except Exception as e:
            print(f"Error handling request: {e}")
            return self.make_response("400 Bad Request")

def handle_client(client_socket: socket.socket, server: HTTPServer) -> None:
    # Handle individual client connections
    try:
        request_data = client_socket.recv(BUFFER_SIZE).decode()
        response = server.handle_request(request_data)
        client_socket.sendall(response)
    finally:
        client_socket.close()

def run_server(directory: str, host: str = "localhost", port: int = DEFAULT_PORT) -> None:
    # Create and run the HTTP server
    server = HTTPServer(directory)

    with socket.create_server((host, port), reuse_port=True) as sock:
        print(f"Server running on {host}:{port}")

        # Accept and handle client connections
        while True:
            client_sock, addr = sock.accept()
            thread = threading.Thread(
                target=handle_client,
                args=(client_sock, server),
                daemon=True
            )
            thread.start()

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', default="/tmp")
    args = parser.parse_args()

    # Verify directory exists
    if not os.path.isdir(args.directory):
        sys.exit("Directory does not exist")

    # Start the server
    run_server(args.directory)

if __name__ == "__main__":
    main()
