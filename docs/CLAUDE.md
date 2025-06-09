# TrueNAS Middleware Repository Overview

## Purpose
This is the TrueNAS middleware repository - the layer between the OS and frontend/UI that manages user actions through an API server. TrueNAS is built on Debian, and this repository creates Debian packages as part of the TrueNAS build process.

## Repository Structure

### Debian Packages
This repository contains 4 Debian packages:

1. **Main Package** (`./debian/`)
   - Aggregates all packages in the repository
   - Contains systemd service definitions and Debian packaging rules

2. **Middlewared Package** (`./src/middlewared/`)
   - Core API server that handles user requests
   - Most critical component of the repository
   - Contains all business logic and service implementations

3. **Documentation Package** (`./src/middlewared_docs/`)
   - Generates documentation for TrueNAS
   - API documentation and developer guides

4. **FreeNAS Package** (`./src/freenas/`)
   - System configuration files and utilities
   - Check `./src/freenas/debian/rules` for build details

### Key Directories

- **`/tests/`** - Integration tests for the middleware
- **`/docs/`** - Developer documentation and guides

## Development Guidelines

### Service Architecture
- Services extend base classes: `Service`, `ConfigService`, `CRUDService`, or `SystemServiceService`
- Each service manages a specific aspect of TrueNAS functionality
- Services expose methods through the API with proper validation

### API Versioning
- API versions follow YY.MM format (e.g., 25.04, 25.10)
- Each release has its own API version with Pydantic models
- Backward compatibility is maintained through version adapters

### Database
- Uses SQLite3 with SQLAlchemy ORM
- Alembic handles schema migrations
- Data migrations require running middleware

### Testing
- Unit tests: `./src/middlewared/middlewared/pytest/`
- Integration tests: `./tests/`
- Run tests with appropriate pytest commands

## Getting Started

1. **Understanding Services**: Start by exploring `./src/middlewared/middlewared/plugins/` to see how different services are implemented
2. **API Development**: Check `./src/middlewared/middlewared/api/` for API model definitions
3. **Configuration**: Look at `./src/middlewared/middlewared/etc_files/` for system configuration generation

## Build Process
The repository uses standard Debian packaging:
- Each package has its own `debian/` directory with control files
- Build with standard `dpkg-buildpackage` or similar tools
- Services are installed as systemd units

## Important Notes
- This is a non-standard filesystem structure due to Debian packaging requirements
- The middleware boots as a systemd service and provides the REST/WebSocket API
- All user-facing functionality goes through the middleware layer