# Changelog

All notable changes to DML Stream are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Enterprise file structure with modular architecture
- SQLite storage layer with repository pattern
- New constants package for centralized configuration
- Hierarchical exception structure
- CLI formatters (table, JSON, plain text)
- CLI middleware for error handling and version checking
- GitHub Actions workflows (CI, release, security, docker, codeql)
- VS Code development environment configuration
- Comprehensive test infrastructure
- Cross-platform storage paths (`~/DML Labs/DML Stream/`)
- Database migrations system

### Changed
- **BREAKING**: All data now stored in `~/DML Labs/DML Stream/` instead of project root
- Renamed `cli/main.py` to `cli/app.py` for clarity
- Renamed `cli/commands/config_cli.py` to `cli/commands/config.py`
- Moved `Dockerfile` and `docker-compose.yml` to `docker/` directory
- Split `models/entities.py` into domain-specific modules
- Split `core/constants.py` into dedicated constant modules
- Split `core/exceptions.py` into hierarchical exception packages
- Deprecated `core/constants.py` (use `constants.*` modules)
- Deprecated `core/exceptions.py` (use `exceptions.*` modules)
- Deprecated `models/entities.py` (use `models.*` split modules)
- Deprecated `models/repositories.py` (use `storage.*` modules)

### Improved
- Separation of concerns with dedicated packages
- Type safety with mypy strict mode compliance
- Cross-platform compatibility (pathlib.Path)
- Developer experience with Makefile and VS Code configs
- Documentation with storage paths guide

### Deprecated
- `core/constants.py` - Will be removed in v3.0.0
- `core/exceptions.py` - Will be removed in v3.0.0
- `models/entities.py` - Will be removed in v3.0.0
- `models/repositories.py` - Will be removed in v3.0.0
- JSON file storage - Will be removed in v3.0.0 (migrating to full SQLite)

### Removed
- Migration scripts (no users yet)
- Migration guide documentation

---

## [v3.0.0] - Planned (Q2 2026)

### Planned Changes
- **Full SQLite Migration** - Remove all JSON file storage
- **Database Migrations** - Alembic-based schema versioning
- **Performance Improvements** - Query optimization, indexing
- **API Cleanup** - Remove deprecated modules
- **Breaking Changes** - Drop support for v2.x config formats

### Migration Guide
- Automatic migration tool included
- Backward compatible import for v2.5.x
- Documentation updated

---

## [2.5.0] - 2024-02-26

### Added
- 35+ CLI commands for comprehensive control
- Enhanced storage management with SQLite backend
- Developer tools and debugging commands
- Batch download functionality
- Scheduled download daemon
- Interactive TUI mode with Rich
- Docker multi-stage builds
- Multi-architecture Docker support (amd64, arm64)

### Changed
- Modular command structure
- Improved error handling
- Enhanced progress tracking

### Fixed
- Various bug fixes and stability improvements

---

## [2.0.0] - 2023-12-01

### Added
- Initial release with core download functionality
- Basic CLI interface
- YouTube video and audio download support
- Playlist download support

---

## Legend

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Improved** - Performance or quality improvements
- **Security** - Security improvements
