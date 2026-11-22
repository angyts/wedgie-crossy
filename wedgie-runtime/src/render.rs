//! Allocation-free visible tile snapshot, independent of the display driver.
use crate::{Player, WIDTH, WINDOW_ROWS};
use crate::world::GrassWindow;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Tile { Empty, Grass, Tree, Chicken }

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Frame {
    pub tiles: [[Tile; WIDTH as usize]; WINDOW_ROWS],
    pub first_row: u32,
    pub score: u32,
    pub game_over: bool,
}

impl Frame {
    pub fn tile(&self, screen_row: usize, column: usize) -> Option<Tile> {
        self.tiles.get(screen_row).and_then(|row| row.get(column)).copied()
    }
}

/// Screen row zero is the oldest visible world row; higher indices go forward.
/// Missing world rows remain empty. No framebuffer allocation is performed.
pub fn snapshot(world: &GrassWindow, player: Player, score: u32, dead: bool) -> Frame {
    let first_row = world.start();
    let mut frame = Frame {
        tiles: [[Tile::Empty; WIDTH as usize]; WINDOW_ROWS],
        first_row, score, game_over: dead,
    };
    for screen_y in 0..WINDOW_ROWS {
        let Some(world_y) = first_row.checked_add(screen_y as u32) else { break; };
        if let Some(row) = world.get(world_y) {
            for x in 0..WIDTH as usize {
                frame.tiles[screen_y][x] = if row.trees & (1u16 << x) != 0 {
                    Tile::Tree
                } else {
                    Tile::Grass
                };
            }
        }
    }
    if !dead && player.column < WIDTH as u8 && player.row >= first_row {
        let screen_y = (player.row - first_row) as usize;
        if screen_y < WINDOW_ROWS && world.get(player.row).is_some() {
            frame.tiles[screen_y][player.column as usize] = Tile::Chicken;
        }
    }
    frame
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::world::GrassRow;

    #[test]
    fn draws_chicken_and_tree() {
        let mut world = GrassWindow::new();
        world.push(GrassRow { index: 0, trees: 1 << 2 }).unwrap();
        let frame = snapshot(&world, Player { row: 0, column: 5 }, 7, false);
        assert_eq!(frame.tile(0, 2), Some(Tile::Tree));
        assert_eq!(frame.tile(0, 5), Some(Tile::Chicken));
        assert_eq!(frame.tile(0, 0), Some(Tile::Grass));
        assert_eq!(frame.tile(0, 12), None);
        assert_eq!(frame.score, 7);
    }

    #[test]
    fn missing_rows_are_empty() {
        let mut world = GrassWindow::new();
        world.push(GrassRow { index: 0, trees: 0 }).unwrap();
        let frame = snapshot(&world, Player { row: 0, column: 5 }, 0, false);
        assert_eq!(frame.tile(1, 5), Some(Tile::Empty));
    }

    #[test]
    fn scrolling_window_keeps_absolute_origin() {
        let mut world = GrassWindow::new();
        for index in 0..20 {
            world.push(GrassRow { index, trees: 0 }).unwrap();
        }
        let frame = snapshot(&world, Player { row: 19, column: 5 }, 19, false);
        assert_eq!(frame.first_row, 4);
        assert_eq!(frame.tile(15, 5), Some(Tile::Chicken));
    }

    #[test]
    fn dead_player_is_not_drawn() {
        let mut world = GrassWindow::new();
        world.push(GrassRow { index: 0, trees: 0 }).unwrap();
        let frame = snapshot(&world, Player { row: 0, column: 5 }, 0, true);
        assert_eq!(frame.tile(0, 5), Some(Tile::Grass));
        assert!(frame.game_over);
    }

    #[test]
    fn frame_has_fixed_memory_bound() {
        assert!(core::mem::size_of::<Frame>() <= 1024);
    }
}
