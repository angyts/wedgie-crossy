//! Minimal allocation-free grass game loop using the bounded world window.
use crate::{Camera, Move, Player, StepResult, WIDTH};
use crate::world::GrassWindow;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Game {
    pub player: Player,
    pub camera: Camera,
    pub tick: u32,
    pub score: u32,
    pub dead: bool,
    pub world: GrassWindow,
}

impl Game {
    pub fn new(world: GrassWindow, column: u8) -> Result<Self, &'static str> {
        if column >= WIDTH as u8 { return Err("invalid column"); }
        let start = world.get(0).ok_or("missing starting row")?;
        if start.trees & (1u16 << column) != 0 {
            return Err("blocked starting tile");
        }
        Ok(Self {
            player: Player { row: 0, column },
            camera: Camera::new(100, 20, -3),
            tick: 0, score: 0, dead: false, world,
        })
    }

    /// One input per tick; missing or evicted rows are not traversable.
    pub fn step(&mut self, movement: Move) -> StepResult {
        if self.dead { return StepResult::Dead; }
        let next_tick = match self.tick.checked_add(1) {
            Some(tick) => tick,
            None => { self.dead = true; return StepResult::Dead; }
        };
        let (dy, dx): (i8, i8) = match movement {
            Move::Wait => (0, 0),
            Move::Forward => (1, 0),
            Move::Back => (-1, 0),
            Move::Left => (0, -1),
            Move::Right => (0, 1),
        };
        let target_row = if dy == 1 { self.player.row.checked_add(1) }
            else if dy == -1 { self.player.row.checked_sub(1) }
            else { Some(self.player.row) };
        let target_col = i16::from(self.player.column) + i16::from(dx);
        let mut blocked = false;
        match target_row {
            Some(row) if (0..WIDTH).contains(&target_col) => {
                match self.world.get(row) {
                    Some(grass) => {
                        if grass.trees & (1u16 << target_col) != 0 {
                            blocked = true;
                        } else {
                            self.player.row = row;
                            self.player.column = target_col as u8;
                        }
                    }
                    None => { self.dead = true; return StepResult::Dead; }
                }
            }
            _ => { self.dead = true; return StepResult::Dead; }
        }
        self.tick = next_tick;
        self.score = self.score.max(self.player.row);
        if self.camera.update(self.player.row, self.tick) {
            self.dead = true;
            StepResult::Dead
        } else if blocked {
            StepResult::Blocked
        } else {
            StepResult::Alive
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::world::GrassRow;

    fn world() -> GrassWindow {
        let mut w = GrassWindow::new();
        for index in 0..4 {
            w.push(GrassRow { index, trees: if index == 1 { 1 << 5 } else { 0 } }).unwrap();
        }
        w
    }

    #[test]
    fn blocks_and_moves_with_correct_target_mask() {
        let mut g = Game::new(world(), 5).unwrap();
        assert_eq!(g.step(Move::Forward), StepResult::Blocked);
        assert_eq!(g.tick, 1);
        assert_eq!(g.player.row, 0);
        assert_eq!(g.step(Move::Right), StepResult::Alive);
        assert_eq!(g.step(Move::Forward), StepResult::Alive);
        assert_eq!(g.score, 1);
    }

    #[test]
    fn death_is_terminal() {
        let mut g = Game::new(world(), 0).unwrap();
        assert_eq!(g.step(Move::Back), StepResult::Dead);
        assert_eq!(g.step(Move::Forward), StepResult::Dead);
        assert_eq!(g.player.row, 0);
    }

    #[test]
    fn rejects_blocked_start() {
        assert!(Game::new(world(), 12).is_err());
        let mut w = GrassWindow::new();
        w.push(GrassRow { index: 0, trees: 1 << 5 }).unwrap();
        assert!(Game::new(w, 5).is_err());
    }

    #[test]
    fn missing_row_fails_closed() {
        let mut g = Game::new(world(), 0).unwrap();
        for _ in 0..3 { assert_eq!(g.step(Move::Forward), StepResult::Alive); }
        assert_eq!(g.step(Move::Forward), StepResult::Dead);
    }

    #[test]
    fn tick_overflow_fails_closed() {
        let mut g = Game::new(world(), 0).unwrap();
        g.tick = u32::MAX;
        assert_eq!(g.step(Move::Wait), StepResult::Dead);
    }
}
