//! Fixed-capacity grass window for embedded rendering and collisions.
//! Rows are addressed by absolute indices; storage never allocates.
use crate::WINDOW_ROWS;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct GrassRow {
    pub index: u32,
    pub trees: u16,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct GrassWindow {
    rows: [Option<GrassRow>; WINDOW_ROWS],
    start: u32,
    len: usize,
}

impl GrassWindow {
    pub const fn new() -> Self {
        Self { rows: [None; WINDOW_ROWS], start: 0, len: 0 }
    }

    pub fn len(&self) -> usize { self.len }
    pub fn is_empty(&self) -> bool { self.len == 0 }
    pub fn start(&self) -> u32 { self.start }

    /// Append the next contiguous absolute row, evicting the oldest if full.
    pub fn push(&mut self, row: GrassRow) -> Result<(), &'static str> {
        if row.trees & !crate::MAX_TREES != 0 {
            return Err("tree mask outside board");
        }
        if self.len == 0 {
            self.start = row.index;
        } else if self.start.checked_add(self.len as u32) != Some(row.index) {
            return Err("noncontiguous row");
        }
        self.rows[row.index as usize % WINDOW_ROWS] = Some(row);
        if self.len < WINDOW_ROWS {
            self.len += 1;
        } else {
            self.start += 1;
        }
        Ok(())
    }

    pub fn get(&self, index: u32) -> Option<GrassRow> {
        if index < self.start || index - self.start >= self.len as u32 {
            return None;
        }
        self.rows[index as usize % WINDOW_ROWS]
    }
}

impl Default for GrassWindow {
    fn default() -> Self { Self::new() }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn bounded_after_many_rows() {
        let mut w = GrassWindow::new();
        for i in 0..100_000 {
            w.push(GrassRow { index: i, trees: 0 }).unwrap();
            assert!(w.len() <= WINDOW_ROWS);
        }
        assert_eq!(w.len(), WINDOW_ROWS);
        assert_eq!(w.start(), 100_000 - WINDOW_ROWS as u32);
        assert!(w.get(0).is_none());
        assert_eq!(w.get(99_999).unwrap().index, 99_999);
    }

    #[test]
    fn rejects_gaps_without_mutating() {
        let mut w = GrassWindow::new();
        w.push(GrassRow { index: 7, trees: 0 }).unwrap();
        let before = w;
        assert!(w.push(GrassRow { index: 9, trees: 0 }).is_err());
        assert_eq!(w, before);
    }

    #[test]
    fn rejects_invalid_mask() {
        let mut w = GrassWindow::new();
        assert!(w.push(GrassRow { index: 0, trees: 1 << 12 }).is_err());
        assert!(w.is_empty());
    }

    #[test]
    fn small_fixed_memory() {
        assert!(core::mem::size_of::<GrassWindow>() <= 256);
    }
}
