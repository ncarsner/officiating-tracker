# Changelog

## [Unreleased]

### Added
- Unpaid/All toggle on game list: defaults to showing only unpaid, non-volunteer games on login.
- Month grouping on game list: games collapsed by month with click-to-expand headers showing game count.
- Date+site trip grouping: within each month, games at the same site on the same date are grouped under a trip sub-header showing mileage once rather than per game entry.

### Fixed
- Game list table was showing all games regardless of active filters; now correctly scoped to the filtered queryset.
- Mileage display deduped per trip: mileage paid status reflects all games in the trip group.
