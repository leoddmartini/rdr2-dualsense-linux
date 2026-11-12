# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project uses [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-11-12

### Added

- `rdr2-dualsense-native`: DSX-compatible UDP bridge that writes DualSense
  trigger effects and lightbar colour directly to hidraw (USB).
- `rdr2-with-triggers`: Steam launch wrapper that starts and stops the bridge
  with the game and refuses to start the game when the bridge is not ready.
- `install.sh` with install and uninstall support.
- Documentation: setup guide, protocol notes and troubleshooting.
- Unit tests and CI (unittest, ShellCheck, Ruff).
