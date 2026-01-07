"""Lightweight physics for puck and mallets (no Box2D)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from air_hockey.game.entities import MalletSpec, PuckSpec
from air_hockey.game.field import FieldSpec


@dataclass
class Body:
    position: tuple[float, float]
    linearVelocity: tuple[float, float]
    radius: float
    mass: float
    restitution: float
    damping: float = 0.0


@dataclass
class PhysicsEntities:
    puck: Body
    mallet_left: Body
    mallet_right: Body


class PhysicsWorld:
    def __init__(
        self,
        field: FieldSpec,
        on_puck_wall: Optional[Callable[[], None]] = None,
        on_puck_mallet: Optional[Callable[[], None]] = None,
        puck_restitution: float | None = None,
        puck_damping: float | None = None,
        max_puck_speed: float | None = None,
    ) -> None:
        self.field = field
        self.on_puck_wall = on_puck_wall
        self.on_puck_mallet = on_puck_mallet
        self.puck_restitution = puck_restitution
        self.puck_damping = puck_damping
        self.max_puck_speed = max_puck_speed
        self.entities = self._create_entities()

    def _create_entities(self) -> PhysicsEntities:
        puck_spec = PuckSpec()
        mallet_spec = MalletSpec()
        puck = Body(
            position=(0.0, 0.0),
            linearVelocity=(0.0, 0.0),
            radius=puck_spec.radius,
            mass=self._circle_mass(puck_spec.radius, puck_spec.density),
            restitution=self.puck_restitution
            if self.puck_restitution is not None
            else puck_spec.restitution,
            damping=self.puck_damping if self.puck_damping is not None else puck_spec.linear_damping,
        )
        mallet_left = Body(
            position=(-self.field.width * 0.25, 0.0),
            linearVelocity=(0.0, 0.0),
            radius=mallet_spec.radius,
            mass=self._circle_mass(mallet_spec.radius, mallet_spec.density),
            restitution=mallet_spec.restitution,
            damping=mallet_spec.linear_damping,
        )
        mallet_right = Body(
            position=(self.field.width * 0.25, 0.0),
            linearVelocity=(0.0, 0.0),
            radius=mallet_spec.radius,
            mass=self._circle_mass(mallet_spec.radius, mallet_spec.density),
            restitution=mallet_spec.restitution,
            damping=mallet_spec.linear_damping,
        )
        return PhysicsEntities(puck=puck, mallet_left=mallet_left, mallet_right=mallet_right)

    def step(self, time_step: float) -> None:
        puck = self.entities.puck
        self._apply_damping(puck, time_step)
        self._integrate_body(puck, time_step)

        self._apply_damping(self.entities.mallet_left, time_step)
        self._apply_damping(self.entities.mallet_right, time_step)
        self._integrate_body(self.entities.mallet_left, time_step)
        self._integrate_body(self.entities.mallet_right, time_step)

        self._resolve_puck_walls(puck)
        self._resolve_puck_mallet_collision(puck, self.entities.mallet_left)
        self._resolve_puck_mallet_collision(puck, self.entities.mallet_right)

        if self.max_puck_speed:
            self._clamp_puck_speed()

    def update_puck_settings(
        self, restitution: float, damping: float, max_speed: float
    ) -> None:
        self.max_puck_speed = None if max_speed <= 0 else max_speed
        puck = self.entities.puck
        puck.damping = max(0.0, damping)
        puck.restitution = restitution

    def set_mallet_positions(
        self,
        left_pos: tuple[float, float],
        right_pos: tuple[float, float],
        time_step: float,
        teleport: bool = False,
        max_speed: float | None = None,
    ) -> None:
        if teleport:
            self.entities.mallet_left.linearVelocity = (0.0, 0.0)
            self.entities.mallet_right.linearVelocity = (0.0, 0.0)
            self.entities.mallet_left.position = left_pos
            self.entities.mallet_right.position = right_pos
            return

        left_body = self.entities.mallet_left
        right_body = self.entities.mallet_right
        left_vel = (
            (left_pos[0] - left_body.position[0]) / time_step,
            (left_pos[1] - left_body.position[1]) / time_step,
        )
        right_vel = (
            (right_pos[0] - right_body.position[0]) / time_step,
            (right_pos[1] - right_body.position[1]) / time_step,
        )
        if max_speed and max_speed > 0:
            left_vel = self._clamp_velocity(left_vel, max_speed)
            right_vel = self._clamp_velocity(right_vel, max_speed)
        left_body.linearVelocity = left_vel
        right_body.linearVelocity = right_vel

    @staticmethod
    def _circle_mass(radius: float, density: float) -> float:
        return density * 3.141592653589793 * radius * radius

    @staticmethod
    def _integrate_body(body: Body, time_step: float) -> None:
        vx, vy = body.linearVelocity
        body.position = (
            body.position[0] + vx * time_step,
            body.position[1] + vy * time_step,
        )

    @staticmethod
    def _apply_damping(body: Body, time_step: float) -> None:
        if body.damping <= 0:
            return
        decay = max(0.0, 1.0 - body.damping * time_step)
        body.linearVelocity = (body.linearVelocity[0] * decay, body.linearVelocity[1] * decay)

    def _resolve_puck_walls(self, puck: Body) -> None:
        half_width = self.field.width / 2.0
        half_height = self.field.height / 2.0
        goal_half = self.field.goal_height / 2.0
        x, y = puck.position
        vx, vy = puck.linearVelocity
        radius = puck.radius
        hit_wall = False

        if y - radius < -half_height:
            y = -half_height + radius
            vy = abs(vy) if abs(vy) > 0.0 else 0.1
            hit_wall = True
        elif y + radius > half_height:
            y = half_height - radius
            vy = -abs(vy) if abs(vy) > 0.0 else -0.1
            hit_wall = True

        if abs(y) >= goal_half:
            if x - radius < -half_width:
                x = -half_width + radius
                vx = abs(vx) if abs(vx) > 0.0 else 0.1
                hit_wall = True
            elif x + radius > half_width:
                x = half_width - radius
                vx = -abs(vx) if abs(vx) > 0.0 else -0.1
                hit_wall = True

        if hit_wall:
            restitution = max(0.0, min(1.0, puck.restitution))
            puck.position = (x, y)
            puck.linearVelocity = (vx * restitution, vy * restitution)
            if self.on_puck_wall:
                self.on_puck_wall()

    def _resolve_puck_mallet_collision(self, puck: Body, mallet: Body) -> None:
        dx = puck.position[0] - mallet.position[0]
        dy = puck.position[1] - mallet.position[1]
        distance_sq = dx * dx + dy * dy
        min_dist = puck.radius + mallet.radius
        if distance_sq >= min_dist * min_dist:
            return

        distance = distance_sq ** 0.5 if distance_sq > 0 else min_dist
        nx = dx / distance
        ny = dy / distance

        penetration = min_dist - distance
        puck.position = (
            puck.position[0] + nx * penetration,
            puck.position[1] + ny * penetration,
        )

        rvx = puck.linearVelocity[0] - mallet.linearVelocity[0]
        rvy = puck.linearVelocity[1] - mallet.linearVelocity[1]
        vel_along_normal = rvx * nx + rvy * ny
        if vel_along_normal > 0:
            return

        restitution = max(0.0, min(1.0, (puck.restitution + mallet.restitution) * 0.5))
        inv_mass_puck = 1.0 / puck.mass if puck.mass > 0 else 0.0
        inv_mass_mallet = 1.0 / mallet.mass if mallet.mass > 0 else 0.0
        impulse = -(1.0 + restitution) * vel_along_normal
        impulse /= inv_mass_puck + inv_mass_mallet if (inv_mass_puck + inv_mass_mallet) > 0 else 1.0
        imp_x = impulse * nx
        imp_y = impulse * ny

        puck.linearVelocity = (
            puck.linearVelocity[0] + imp_x * inv_mass_puck,
            puck.linearVelocity[1] + imp_y * inv_mass_puck,
        )
        mallet.linearVelocity = (
            mallet.linearVelocity[0] - imp_x * inv_mass_mallet,
            mallet.linearVelocity[1] - imp_y * inv_mass_mallet,
        )
        if self.on_puck_mallet:
            self.on_puck_mallet()

    def _clamp_puck_speed(self) -> None:
        puck = self.entities.puck
        vx, vy = puck.linearVelocity
        speed_sq = vx * vx + vy * vy
        max_speed = self.max_puck_speed or 0.0
        if max_speed <= 0.0:
            return
        if speed_sq > max_speed * max_speed:
            scale = max_speed / (speed_sq ** 0.5)
            puck.linearVelocity = (vx * scale, vy * scale)

    @staticmethod
    def _clamp_velocity(velocity: tuple[float, float], max_speed: float) -> tuple[float, float]:
        vx, vy = velocity
        speed_sq = vx * vx + vy * vy
        if speed_sq <= max_speed * max_speed:
            return velocity
        scale = max_speed / (speed_sq ** 0.5)
        return (vx * scale, vy * scale)
