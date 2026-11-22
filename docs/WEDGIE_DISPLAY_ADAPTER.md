# Wedgie display-neutral integration

`Game::frame()` now snapshots player, grass, trees, score and game-over state. `display::draw_frame` calls a minimal `Display` trait with 192 tile draws, HUD data and one flush per frame. A hardware-specific implementation can translate these calls into the actual Wedgie graphics API without adding heap allocation to the core runtime.

This is not yet a Wedgie display driver, and no physical display or button integration has been verified. The approved runtime remains grass-only. Next: identify Wedgie firmware and display APIs and add an adapter against them.
