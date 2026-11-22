"""Stable 32-bit xorshift PRNG. Never change v1 output silently."""
MASK = 0xffffffff
ZERO_SEED = 0x6d2b79f5

class PRNG:
    def __init__(self, seed):
        if not isinstance(seed, int) or not 0 <= seed <= MASK:
            raise ValueError("seed must be a uint32")
        self.seed = seed
        self.state = seed or ZERO_SEED

    def next_u32(self):
        x = self.state
        x ^= (x << 13) & MASK
        x ^= x >> 17
        x ^= (x << 5) & MASK
        self.state = x & MASK
        return self.state

    def below(self, limit):
        """Unbiased bounded sample by rejection, 1 <= limit <= 2**32."""
        if not isinstance(limit, int) or not 1 <= limit <= (1 << 32):
            raise ValueError("invalid limit")
        threshold = (1 << 32) % limit
        while True:
            value = self.next_u32()
            if value >= threshold:
                return value % limit
