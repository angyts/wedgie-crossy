# Stage 6b — calm grass palette

Hardware-verified Stage 6 checkpoint: `9c5d449`. This is a rendering-only change: remove alternating full-width 20px green stripes and use a uniform soft green grass background. The HUD retains a dark background. Tree, chicken, world generation, scrolling, movement and collision logic are unchanged. Update the host LCD smoke assertion to expect zero full-width row stripes. Verify on the physical device before adding gameplay features.
