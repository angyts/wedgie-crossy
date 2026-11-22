# Generator gating: conservative baseline

The new `ApprovedWorld` is a separate opt-in generator that only emits
grass with a permanently open center corridor. It demonstrates a
fail-closed allowlist, reproducible generation and bounded memory.
`assert_approved` rejects roads, rivers, railways and blocked center
corridors. The original `World` generator is unchanged and still emits
uncertified candidates.

This is **not** full procedural fairness certification. It is deliberately
boring and is NOT the production Crossy terrain mix. Next implement
explicit entry/exit state propagation, a common time/physics contract,
and a reviewed catalog of compatible hazard sections before permitting
roads, rivers or railways in an approved generator. There is still no
playable Wedgie app or physical-device acceptance.
