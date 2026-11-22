# Test and milestone corrections

The `save` firmware module is imported only inside `run`, allowing pure host tests to import the app without installing MicroPython firmware modules. The existing boot smoke test now expects the single full-width 20px HUD background rectangle. The score is yellow/bold only when the current score is a positive multiple of ten, and returns to normal immediately on the next score. No 900ms hold or timer. The previously hardware-verified scrolling checkpoint is preserved in history. Run the full Python suite and inspect CI before declaring this revision verified.
