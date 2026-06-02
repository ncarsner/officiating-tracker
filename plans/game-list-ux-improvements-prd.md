# Improve Game List UX and Stats Readability

## Overview

Refine the game list and stats pages to reduce visual noise, speed up the most common user action (marking a game paid), and display financial figures consistently as whole dollars. These changes follow the recent UI layout work on the `ui-enhance` branch and address friction points identified in daily use.

## Goals

1. Game list table renders without the Site column, reducing horizontal clutter.
2. Users can mark a game paid or unpaid directly from the list in one click, without opening the edit form.
3. Toggling between Unpaid and All views happens instantly (no page reload) by filtering already-loaded data.
4. Edit and Delete affordances use icon buttons, reducing visual weight while remaining accessible.
5. Stats page displays all dollar amounts as whole integers, improving scannability.
6. Stats page sections are collapsible; the section label in the first column makes the h3 header redundant and removing it reduces visual weight.
7. The game list summary widget adapts from a 2x2 grid on wide viewports to a single-column list on mobile, preventing cramped layout on small screens.

## Non-goals

- No changes to mileage display or mileage-paid logic.
- No changes to the Add Game form or any other page.
- No backend API refactor; the inline paid toggle uses an existing or minimal new endpoint.
- No changes to filter behavior beyond the Unpaid/All client-side toggle.

## User stories

- As an official, I want to mark a game paid directly from the game list so that I do not have to open the edit form for a routine payment update.
- As an official, I want to switch between Unpaid and All games instantly so that I can scan my payment status without waiting for a page reload.
- As an official, I want the stats tables to show dollar amounts without cents so that financial totals are easier to read at a glance.
- As an official, I want icon-only Edit and Delete buttons so that the game list feels less cluttered and I can act on rows quickly.
- As an official, I want to collapse stats sections I am not focused on so that the page is less overwhelming and I can scan what matters.
- As an official viewing the game list on my phone, I want the summary figures to stack in a readable single column so that I do not have to squint at a cramped 2x2 grid.

## Requirements

1. Remove the Site column (`<th>` and all `<td>` cells) from `tracker/templates/game/list.html`. The table colspan counts must be updated to match.
2. Add a Fee column to the per-game rows in `list.html` that displays the game fee amount (e.g., `$75`).
3. Add an inline paid toggle icon button to each per-game row. Clicking it sends a POST to a toggle endpoint and updates the icon in place without a full page reload (AJAX or htmx-style form).
4. The toggle icon must visually distinguish paid (checkmark/green) from unpaid (dollar/gray) states and update immediately on success.
5. Replace the Edit text button with a pen icon button and the Delete text button with an X icon button. Both must retain their existing behavior and CSRF handling. Accessible `aria-label` attributes are required on each icon button.
6. The Unpaid / All toggle must filter rows client-side using a `data-paid` attribute on each row, with no HTTP request. The URL query param may still reflect the state for bookmarking.
7. Replace `floatformat:2` with `floatformat:0` on all fee columns in `tracker/templates/game/stats.html` (By Year, By League, By Assignor, By Position, By Site tables).
8. A new URL route and view method (e.g., `toggle_fee_paid`) must handle the AJAX POST for requirement 3, returning JSON `{"fee_paid": true/false}` and requiring `@login_required`.
9. Remove the `<h3>` section headers from each stats section in `stats.html`. Replace each `<section>` with a collapsible block whose toggle button displays the section name (e.g., "By Year"). By Year and By League expand by default; By Assignor, By Position, and By Site collapse by default. State is managed client-side via JS; no server round-trip.
10. Change the game list summary grid from `grid-cols-2` (fixed 2x2) to a responsive layout: `grid-cols-1` on mobile, `grid-cols-2` on `sm:` and wider. No change to the data or labels displayed.

## Acceptance criteria

- [ ] R1: The Site column header and all site data cells are absent from the game list table.
- [ ] R1: Table colspan values are consistent; no broken layout in collapsed or expanded month rows.
- [ ] R2: Each per-game row shows the fee amount formatted as a whole-dollar integer (e.g., `$75`, not `$75.00`).
- [ ] R3: Clicking the paid toggle icon on a game row sends exactly one POST to the toggle endpoint without navigating away.
- [ ] R4: After a successful toggle, the icon updates to reflect the new paid state without a page reload.
- [ ] R4: If the server returns an error, the icon reverts and no silent failure occurs.
- [ ] R5: Edit button renders as a pen SVG icon with `aria-label="Edit game"`.
- [ ] R5: Delete button renders as an X SVG icon with `aria-label="Delete game"`. Existing confirm dialog is preserved.
- [ ] R6: Clicking Unpaid shows only rows where `data-paid="false"`; clicking All shows all rows. No network request fires on toggle.
- [ ] R6: The active tab styling updates on click.
- [ ] R7: All fee cells in stats.html show values rounded to the nearest dollar with no decimal point.
- [ ] R8: The toggle endpoint is protected by `@login_required` and rejects non-POST requests with 405.
- [ ] R8: The endpoint only toggles games owned by the authenticated user; a 404 is returned for games belonging to other users.
- [ ] R9: Each `<h3>` section header is removed from stats.html.
- [ ] R9: Each stats section renders as a collapsible block with a toggle button showing the section name.
- [ ] R9: By Year and By League are expanded on initial page load; By Assignor, By Position, and By Site are collapsed.
- [ ] R9: Toggling a section shows or hides its table with no page reload.
- [ ] R10: The summary grid displays as a single column on viewports narrower than the Tailwind `sm` breakpoint (640px).
- [ ] R10: The summary grid displays as 2x2 on `sm:` and wider viewports.
- [ ] R10: No change to the content, labels, or values in the summary widget.

## Open questions

- Should the fee toggle icon button be an SVG inline or a Unicode character? SVG preferred for consistency with the existing `icon-checkmark.html` include pattern, but confirm before implementing.
- The client-side Unpaid/All toggle currently preserves the active filter state in the URL via `<a>` links that trigger a GET. Replacing with JS filtering means the URL will not update unless we push to history. Is URL persistence required for this toggle?
- Should the Stats page currency columns include a `$` prefix after the format change, or is the existing `$` literal in the template sufficient?
