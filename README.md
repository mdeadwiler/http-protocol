# Custom HTTP Server Implementation

A robust HTTP/1.1 server implementation in Python that supports multiple client connections, file operations, and response compression. This server demonstrates modern HTTP functionality while maintaining clean, type-safe code through comprehensive type hinting.

## Features

## Why This Project?

As an entry-level software engineer deeply passionate about understanding system fundamentals, I chose to build this HTTP server implementation to gain hands-on experience with core networking concepts. This project challenged me to dive deep into TCP/IP protocols, concurrent programming with threading, and proper error handling - skills that are essential for any backend developer. By building a server from scratch rather than using existing frameworks, I gained invaluable insights into how web servers actually work under the hood. The project helped me understand crucial software engineering concepts like protocol design, system architecture, and test-driven development. What started as a learning exercise became a practical demonstration of my ability to handle complex programming challenges and my commitment to understanding the fundamental building blocks of modern web infrastructure. This experience has not only improved my technical skills but also reinforced my passion for software engineering and system design.

### Core HTTP Functionality
- **HTTP/1.1 Protocol Support**: Full implementation of HTTP/1.1 request handling
- **Multi-threading**: Handles multiple concurrent client connections efficiently
- **Method Support**: Implements GET and POST methods with proper status codes
- **Error Handling**: Comprehensive error handling with appropriate HTTP status codes (404, 405, 500)

### Advanced Features
- **File Operations**
  - Binary file upload and download support
  - Secure file path handling
  - Automatic Content-Type detection for files
  - Directory-based file storage

- **Response Compression**
  - Gzip compression support
  - Content-Encoding header handling
  - Automatic compression negotiation

- **Special Endpoints**
  - `/` - Root endpoint returning 200 OK
  - `/echo/*` - Echo service returning client-provided content
  - `/user-agent` - Returns client's User-Agent information
  - `/files/*` - File upload and download functionality

### Technical Implementation
- **Type Safety**
  - Comprehensive type hints throughout the codebase
  - Proper handling of binary and text data
  - Clear interface definitions

- **Robust Error Handling**
  - Graceful handling of malformed requests
  - Proper resource cleanup
  - Detailed error logging

## Getting Started

### Prerequisites
- Python 3.11 or later
- `pipenv` (recommended for dependency management)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Set up the environment:
```bash
pipenv install
```

3. Run the server:
```bash
python main.py <directory-path>
```
Replace `<directory-path>` with the path where files should be stored.

## Usage Examples

### Basic GET Request
```bash
curl http://localhost:4221/
```

### Echo Service
```bash
curl http://localhost:4221/echo/hello-world
```

### User Agent Information
```bash
curl http://localhost:4221/user-agent
```

### File Operations
Upload a file:
```bash
curl -X POST -d 'content' http://localhost:4221/files/example.txt
```

Download a file:
```bash
curl http://localhost:4221/files/example.txt
```

### Key Components
- **HTTPServer**: Main server class handling connection management
- **Request Processing**: Dedicated methods for GET and POST requests
- **File Operations**: Binary-safe file handling
- **Compression**: Gzip compression support
- **Multi-threading**: Thread-per-client connection model

### Technical Considerations
- Binary data handling for file operations
- Thread safety in concurrent operations
- Content-Type and Content-Length header management
- Proper HTTP response formatting
- Secure file path handling

## Future Enhancements
- Support for additional HTTP methods (PUT, DELETE)
- HTTPS support
- Request rate limiting
- Cache control implementation
- Enhanced logging capabilities
