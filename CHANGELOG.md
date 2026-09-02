# Changelog

All notable changes to Virtual Switch will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions use the project's `major.minor.build` numbering scheme.

## [Unreleased]

### Changed

- Classified each config entry as a device so the integration remains visible on the Home Assistant Integrations dashboard.
- Aligned the minimum supported Home Assistant version with Timed Switch at 2026.8.2.

## [0.3.0008] - 2026-08-29

### Added

- English and Hungarian user documentation.
- HACS metadata, MIT license, and GitHub Actions for HACS and Hassfest validation.
- A parameterized local validation script for repository checks, unit tests, and Dockerized Hassfest.

### Changed

- Prepared repository metadata for publication under the `kovizsolt` GitHub account.
- Declared Home Assistant 2025.9.4 as the minimum supported version and classified the integration as a helper.
- Added HACS custom-repository installation instructions.

### Fixed

- Hassfest validation now recognizes the HTTP dependency and config-entry-only setup.
- Custom-status field labels no longer contain angle brackets interpreted as HTML by translation validation.

## [0.2.0005] - 2026-08-19

### Added

- Stateful simulated main and internal switches.
- Built-in Online, Unavailable, Unknown, and Error statuses.
- User-defined statuses with configurable availability and reported ON/OFF state.
- Persistent status and internal state across Home Assistant restarts.
- Virtual Switch dashboard card.
- Home Assistant device grouping and integration branding.

### Fixed

- Validation, persistence, and display of custom statuses.
- Dashboard card selection and layout behavior.
