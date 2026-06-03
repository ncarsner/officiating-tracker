# Changelog

## [Unreleased]

### Added
- Unpaid/All toggle on game list: defaults to showing only unpaid, non-volunteer games on login.
- Month grouping on game list: games collapsed by month with click-to-expand headers showing game count.
- Date+site trip grouping: within each month, games at the same site on the same date are grouped under a trip sub-header showing mileage once rather than per game entry.
- PRD and task JSON for game list UX improvements (`plans/game-list-ux-improvements-prd.md`, `plans/game-list-ux-improvements-prd.json`).

### Changed
- Stats page fee columns (Total Fees, Paid, Unpaid) now display as whole dollars with no decimal places across all five stat tables.
- Game list summary widget is now responsive: single-column stack on mobile (below 640px), 2x2 grid on wider viewports.

### Fixed
- Game list table was showing all games regardless of active filters; now correctly scoped to the filtered queryset.
- Mileage display deduped per trip: mileage paid status reflects all games in the trip group.
