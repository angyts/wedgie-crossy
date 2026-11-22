# Successor-state checks (experimental)

The successor checker starts from an exact six-field boundary state,
restoring player position, absolute hazard tick, camera progress, last
progress time and death boundary. It then searches for a continuation
using the same fixed-point simulation. A batch checker fails closed on
empty state sets and reports which supplied states have no route.

This is NOT production certification: it only checks supplied states,
finite horizons, and the provisional instantaneous-movement model.
No guarantee exists that these are all possible or all relevant entry
states; the generator is still grass-only. State transfer is now explicit
but needs full phase enumeration, dominance pruning, and adversarial
composition tests before admitting hazards.
