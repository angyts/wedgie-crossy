//! Display-neutral drawing interface: the platform supplies the driver.
use crate::render::{Frame, Tile};
use crate::{WIDTH, WINDOW_ROWS};

/// The driver receives every tile, followed by HUD data, then one flush.
/// This interface requires neither an allocator nor a framebuffer.
pub trait Display {
    fn draw_tile(&mut self, row: u8, column: u8, tile: Tile);
    fn draw_hud(&mut self, score: u32, game_over: bool);
    fn flush(&mut self);
}

pub fn draw_frame<D: Display>(frame: &Frame, display: &mut D) {
    for row in 0..WINDOW_ROWS {
        for column in 0..WIDTH as usize {
            display.draw_tile(row as u8, column as u8, frame.tiles[row][column]);
        }
    }
    display.draw_hud(frame.score, frame.game_over);
    display.flush();
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::render::snapshot;
    use crate::world::{GrassRow, GrassWindow};
    use crate::Player;

    struct Recorder {
        calls: usize,
        chicken: usize,
        trees: usize,
        score: u32,
        over: bool,
        flushes: usize,
    }

    impl Display for Recorder {
        fn draw_tile(&mut self, _row: u8, _column: u8, tile: Tile) {
            self.calls += 1;
            if tile == Tile::Chicken { self.chicken += 1; }
            if tile == Tile::Tree { self.trees += 1; }
        }
        fn draw_hud(&mut self, score: u32, over: bool) {
            self.score = score;
            self.over = over;
        }
        fn flush(&mut self) { self.flushes += 1; }
    }

    #[test]
    fn draws_exactly_one_frame_and_hud() {
        let mut world = GrassWindow::new();
        world.push(GrassRow { index: 0, trees: 1 << 2 }).unwrap();
        let frame = snapshot(&world, Player { row: 0, column: 5 }, 9, false);
        let mut d = Recorder { calls: 0, chicken: 0, trees: 0,
                               score: 0, over: true, flushes: 0 };
        draw_frame(&frame, &mut d);
        assert_eq!(d.calls, 192);
        assert_eq!(d.chicken, 1);
        assert_eq!(d.trees, 1);
        assert_eq!(d.score, 9);
        assert!(!d.over);
        assert_eq!(d.flushes, 1);
    }

    #[test]
    fn dead_frame_has_no_chicken() {
        let world = GrassWindow::new();
        let frame = snapshot(&world, Player { row: 0, column: 5 }, 4, true);
        let mut d = Recorder { calls: 0, chicken: 0, trees: 0,
                               score: 0, over: false, flushes: 0 };
        draw_frame(&frame, &mut d);
        assert_eq!(d.chicken, 0);
        assert!(d.over);
        assert_eq!(d.flushes, 1);
    }
}
