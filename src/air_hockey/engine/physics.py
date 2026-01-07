"""Box2D physics setup and stepping."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from Box2D import b2

from air_hockey.game.entities import MalletSpec, PuckSpec
from air_hockey.game.field import FieldSpec


@dataclass
class PhysicsEntities:
    puck: b2.body
    mallet_left: b2.body
    mallet_right: b2.body


class ContactListener(b2.contactListener):
    def __init__(
        self,
        on_puck_wall: Optional[Callable[[], None]] = None,
        on_puck_mallet: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__()
        self.on_puck_wall = on_puck_wall
        self.on_puck_mallet = on_puck_mallet

    def BeginContact(self, contact: b2.contact) -> None:
        body_a = contact.fixtureA.body
        body_b = contact.fixtureB.body
        type_a = body_a.userData
        type_b = body_b.userData

        if self._is_puck_wall(type_a, type_b) and self.on_puck_wall:
            self.on_puck_wall()
        elif self._is_puck_mallet(type_a, type_b) and self.on_puck_mallet:
            self.on_puck_mallet()

    @staticmethod
    def _is_puck_wall(type_a: object, type_b: object) -> bool:
        return (type_a == "puck" and type_b == "wall") or (
            type_b == "puck" and type_a == "wall"
        )

    @staticmethod
    def _is_puck_mallet(type_a: object, type_b: object) -> bool:
        return (type_a == "puck" and type_b == "mallet") or (
            type_b == "puck" and type_a == "mallet"
        )


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
        self.world = b2.world(gravity=(0.0, 0.0), doSleep=True)
        self.world.contactListener = ContactListener(
            on_puck_wall=on_puck_wall, on_puck_mallet=on_puck_mallet
        )
        self.puck_restitution = puck_restitution
        self.puck_damping = puck_damping
        self.max_puck_speed = max_puck_speed
        self.entities = self._create_entities()

    def _create_entities(self) -> PhysicsEntities:
        self._create_walls()
        puck = self._create_puck()
        mallet_left = self._create_mallet(side="left")
        mallet_right = self._create_mallet(side="right")
        return PhysicsEntities(puck=puck, mallet_left=mallet_left, mallet_right=mallet_right)

    def _create_walls(self) -> None:
        thickness = self.field.wall_thickness
        half_width = self.field.width / 2
        half_height = self.field.height / 2
        goal_half = self.field.goal_height / 2
        side_wall_half = max(0.0, half_height - goal_half) / 2

        def add_wall(center_x: float, center_y: float, half_w: float, half_h: float) -> None:
            body = self.world.CreateStaticBody(
                position=(center_x, center_y),
                shapes=b2.polygonShape(box=(half_w, half_h)),
            )
            body.userData = "wall"

        add_wall(0.0, -half_height - thickness, half_width, thickness)
        add_wall(0.0, half_height + thickness, half_width, thickness)
        if side_wall_half > 0:
            top_y = -(goal_half + side_wall_half)
            bottom_y = goal_half + side_wall_half
            add_wall(-half_width - thickness, top_y, thickness, side_wall_half)
            add_wall(-half_width - thickness, bottom_y, thickness, side_wall_half)
            add_wall(half_width + thickness, top_y, thickness, side_wall_half)
            add_wall(half_width + thickness, bottom_y, thickness, side_wall_half)

    def _create_puck(self) -> b2.body:
        spec = PuckSpec()
        restitution = self.puck_restitution if self.puck_restitution is not None else spec.restitution
        damping = self.puck_damping if self.puck_damping is not None else spec.linear_damping
        body = self.world.CreateDynamicBody(position=(0.0, 0.0))
        body.CreateCircleFixture(
            radius=spec.radius,
            density=spec.density,
            friction=spec.friction,
            restitution=restitution,
        )
        body.linearDamping = damping
        body.bullet = True
        body.allowSleep = False
        body.userData = "puck"
        return body

    def _create_mallet(self, side: str) -> b2.body:
        spec = MalletSpec()
        x = -self.field.width * 0.25 if side == "left" else self.field.width * 0.25
        body = self.world.CreateDynamicBody(position=(x, 0.0), fixedRotation=True)
        body.CreateCircleFixture(
            radius=spec.radius,
            density=spec.density,
            friction=spec.friction,
            restitution=spec.restitution,
        )
        body.linearDamping = spec.linear_damping
        body.bullet = True
        body.userData = "mallet"
        return body

    def step(self, time_step: float) -> None:
        self.world.Step(time_step, 10, 6)
        self.world.ClearForces()
        if self.max_puck_speed:
            self._clamp_puck_speed()
        self._resolve_puck_wall_stickiness()

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

    def _resolve_puck_wall_stickiness(self) -> None:
        puck = self.entities.puck
        if not puck.fixtures:
            return
        radius = puck.fixtures[0].shape.radius
        half_width = self.field.width / 2.0
        half_height = self.field.height / 2.0
        goal_half = self.field.goal_height / 2.0
        min_bounce = 0.15

        x, y = puck.position
        vx, vy = puck.linearVelocity
        adjusted = False

        if y - radius <= -half_height:
            y = -half_height + radius
            vy = abs(vy) if abs(vy) >= min_bounce else min_bounce
            adjusted = True
        elif y + radius >= half_height:
            y = half_height - radius
            vy = -abs(vy) if abs(vy) >= min_bounce else -min_bounce
            adjusted = True

        if abs(y) >= goal_half:
            if x - radius <= -half_width:
                x = -half_width + radius
                vx = abs(vx) if abs(vx) >= min_bounce else min_bounce
                adjusted = True
            elif x + radius >= half_width:
                x = half_width - radius
                vx = -abs(vx) if abs(vx) >= min_bounce else -min_bounce
                adjusted = True

        if adjusted:
            puck.position = (x, y)
            puck.linearVelocity = (vx, vy)

    def update_puck_settings(
        self, restitution: float, damping: float, max_speed: float
    ) -> None:
        self.max_puck_speed = None if max_speed <= 0 else max_speed
        puck = self.entities.puck
        puck.linearDamping = max(0.0, damping)
        if puck.fixtures:
            puck.fixtures[0].restitution = restitution

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
    def _clamp_velocity(velocity: tuple[float, float], max_speed: float) -> tuple[float, float]:
        vx, vy = velocity
        speed_sq = vx * vx + vy * vy
        if speed_sq <= max_speed * max_speed:
            return velocity
        scale = max_speed / (speed_sq ** 0.5)
        return (vx * scale, vy * scale)
