# Changelog

## [Unreleased]

### Added
- Collapsible sections on Stats page: Year and League expand on load; Assignor, Position, and Site collapse. Toggle buttons have a bordered rectangle style with left-side chevron; first-column table header removed (button label serves as the group title); smooth CSS grid transition on expand/collapse.

### Changed
- Unpaid/All toggle on game list is now client-side: all game rows render in DOM with `data-paid` attribute; toggling hides/shows rows instantly with no page reload or network request. Initial tab state still reflects the `f_paid` query param.

---

- Fee column in game list: shows effective fee per game as whole dollars ($N); volunteer games show a dash.
- Paid toggle in game list: single-click icon in each game row fires a POST to `toggle_fee_paid`, flips `fee_paid` in place without page reload, and reverts with an alert on server error.
- `POST /game/<id>/toggle-paid/` endpoint: flips `fee_paid`, returns `{"fee_paid": bool}`; requires login, 405 on non-POST, 404 for other users' games.
- Unpaid/All toggle on game list: defaults to showing only unpaid, non-volunteer games on login.
- Month grouping on game list: games collapsed by month with click-to-expand headers showing game count.
- Date+site trip grouping: within each month, games at the same site on the same date are grouped under a trip sub-header showing mileage once rather than per game entry.
- PRD and task JSON for game list UX improvements (`plans/game-list-ux-improvements-prd.md`, `plans/game-list-ux-improvements-prd.json`).

### Changed
- Edit and Delete text buttons in the game list replaced with outlined SVG icon buttons (pen / X); amber for Edit, red for Delete; 40x40px touch targets with aria-labels for accessibility.
- Stats page fee columns (Total Fees, Paid, Unpaid) now display as whole dollars with no decimal places across all five stat tables.
- Game list summary widget is now responsive: single-column stack on mobile (below 640px), 2x2 grid on wider viewports.

### Fixed
- Game list table was showing all games regardless of active filters; now correctly scoped to the filtered queryset.
- Mileage display deduped per trip: mileage paid status reflects all games in the trip group.
