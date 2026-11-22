#![no_std]
//! Small, allocation-free gameplay foundation.
//! Grass-only until hazard physics matches the Python reference.

pub mod world;

pub const WIDTH: i16 = 12;
pub const WINDOW_ROWS: usize = 16;
pub const MAX_TREES: u16 = (1 << WIDTH) - 1;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Move { Wait, Forward, Back, Left, Right }

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Player { pub row: u32, pub column: u8 }

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Camera {
    pub best_row: u32,
    pub last_progress_tick: u32,
    pub boundary: i64,
    pub grace_ticks: u32,
    pub pressure_interval: u32,
    pub initial_boundary: i64,
}

impl Camera {
    pub const fn new(grace_ticks: u32, pressure_interval: u32, initial_boundary: i64) -> Self {
        Self { best_row: 0, last_progress_tick: 0, boundary: initial_boundary,
               grace_ticks, pressure_interval, initial_boundary }
    }

    pub fn update(&mut self, row: u32, tick: u32) -> bool {
        if row > self.best_row {
            self.best_row = row;
            self.last_progress_tick = tick;
        }
        let elapsed = tick.saturating_sub(self.last_progress_tick);
        if elapsed > self.grace_ticks && self.pressure_interval > 0 {
            let advance = 1 + (elapsed - self.grace_ticks - 1) / self.pressure_interval;
            let candidate = self.initial_boundary.saturating_add(advance as i64);
            self.boundary = self.boundary.max(candidate);
        }
        i64::from(row) <= self.boundary
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum StepResult { Alive, Blocked, Dead }

/// Pure bounded grass transition. Tree collisions block movement.
/// A blocked move still consumes a tick, matching Python step_fp.
pub fn step_grass(player: &mut Player, camera: &mut Camera, tick: u32,
                  movement: Move, tree_mask: u16, last_row: u32) -> StepResult {
    let (dy, dx): (i8, i8) = match movement {
        Move::Wait => (0, 0), Move::Forward => (1, 0),
        Move::Back => (-1, 0), Move::Left => (0, -1),
        Move::Right => (0, 1),
    };
    let target_row = if dy > 0 { player.row.checked_add(1) }
                     else if dy < 0 { player.row.checked_sub(1) }
                     else { Some(player.row) };
    let target_col = i16::from(player.column) + i16::from(dx);
    let mut blocked = false;
    if let Some(row) = target_row {
        if row <= last_row && (0..WIDTH).contains(&target_col) {
            if (tree_mask & (1u16 << target_col)) != 0 {
                blocked = true;
            } else {
                player.row = row;
                player.column = target_col as u8;
            }
        } else {
            return StepResult::Dead;
        }
    } else {
        return StepResult::Dead;
    }
    if camera.update(player.row, tick) { StepResult::Dead }
    else if blocked { StepResult::Blocked }
    else { StepResult::Alive }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn moves_and_bounds() {
        let mut p = Player { row: 0, column: 5 };
        let mut c = Camera::new(100, 20, -3);
        assert_eq!(step_grass(&mut p, &mut c, 1, Move::Forward, 0, 4), StepResult::Alive);
        assert_eq!(p.row, 1);
        assert_eq!(step_grass(&mut p, &mut c, 2, Move::Left, 0, 4), StepResult::Alive);
        assert_eq!(p.column, 4);
    }
    #[test] fn tree_blocks_but_tick_advances() {
        let mut p = Player { row: 0, column: 5 };
        let mut c = Camera::new(100, 20, -3);
        assert_eq!(step_grass(&mut p, &mut c, 1, Move::Forward, 1 << 5, 4), StepResult::Blocked);
        assert_eq!(p.row, 0);
    }
    #[test] fn camera_pressure() {
        let mut c = Camera::new(1, 1, -1);
        assert!(!c.update(0, 1));
        assert!(c.update(0, 2));
        assert_eq!(c.boundary, 0);
        assert!(c.update(0, 3));
    }
    #[test] fn camera_progress_resets_inactivity_clock() {
        let mut c = Camera::new(1, 1, -1);
        assert!(!c.update(0, 1));
        assert!(!c.update(1, 2));
        assert_eq!(c.boundary, -1);
        assert!(!c.update(1, 3));
        assert!(!c.update(1, 4));
        assert_eq!(c.boundary, 0);
        assert!(c.update(1, 5));
    }
    #[test]
    fn shared_camera_parity_vectors() {
        let fixtures = include_str!("../../fixtures/camera_parity.csv");
        let mut cases = 0;
        for line in fixtures.lines().filter(|s| !s.starts_with('#') && !s.is_empty()) {
            let parts: Vec<&str> = line.split(',').collect();
            assert_eq!(parts.len(), 6);
            let grace: u32 = parts[0].parse().unwrap();
            let interval: u32 = parts[1].parse().unwrap();
            let initial: i64 = parts[2].parse().unwrap();
            let mut cam = Camera::new(grace, interval, initial);
            let rows: Vec<u32> = parts[3].split(':').map(|s| s.parse().unwrap()).collect();
            let deaths: Vec<u8> = parts[4].split(':').map(|s| s.parse().unwrap()).collect();
            let boundaries: Vec<i64> = parts[5].split(':').map(|s| s.parse().unwrap()).collect();
            assert_eq!(rows.len(), deaths.len());
            assert_eq!(rows.len(), boundaries.len());
            for (i, row) in rows.iter().enumerate() {
                let dead = cam.update(*row, (i + 1) as u32);
                assert_eq!(dead as u8, deaths[i], "case {cases}, tick {}", i + 1);
                assert_eq!(cam.boundary, boundaries[i], "case {cases}, tick {}", i + 1);
            }
            cases += 1;
        }
        assert_eq!(cases, 4);
    }
    #[test] fn no_heap_required() {
        assert!(core::mem::size_of::<Player>() <= 8);
        assert!(core::mem::size_of::<Camera>() <= 48);
    }
}
