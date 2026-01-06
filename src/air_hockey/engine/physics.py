"""Box2D physics setup and stepping."""

from __future__ import annotations

from dataclasses import dataclass

from Box2D import b2

from air_hockey.game.entities import MalletSpec, PuckSpec
from air_hockey.game.field import FieldSpec


@dataclass
class PhysicsEntities:
    puck: b2.body
    mallet_left: b2.body
    mallet_right: b2.body


class PhysicsWorld:
    def __init__(self, field: FieldSpec) -> None:
        self.field = field
        self.world = b2.world(gravity=(0.0, 0.0), doSleep=True)
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

        def add_wall(center_x: float, center_y: float, half_w: float, half_h: float) -> None:
            self.world.CreateStaticBody(
                position=(center_x, center_y),
                shapes=b2.polygonShape(box=(half_w, half_h)),
            )

        add_wall(0.0, -half_height - thickness, half_width, thickness)
        add_wall(0.0, half_height + thickness, half_width, thickness)
        add_wall(-half_width - thickness, 0.0, thickness, half_height)
        add_wall(half_width + thickness, 0.0, thickness, half_height)

    def _create_puck(self) -> b2.body:
        spec = PuckSpec()
        body = self.world.CreateDynamicBody(position=(0.0, 0.0))
        body.CreateCircleFixture(
            radius=spec.radius,
            density=spec.density,
            friction=spec.friction,
            restitution=spec.restitution,
        )
        body.linearDamping = spec.linear_damping
        return body

    def _create_mallet(self, side: str) -> b2.body:
        spec = MalletSpec()
        x = -self.field.width * 0.25 if side == "left" else self.field.width * 0.25
        body = self.world.CreateDynamicBody(position=(x, 0.0))
        body.CreateCircleFixture(
            radius=spec.radius,
            density=spec.density,
            friction=spec.friction,
            restitution=spec.restitution,
        )
        body.linearDamping = spec.linear_damping
        return body

    def step(self, time_step: float) -> None:
        self.world.Step(time_step, vel_iters=8, pos_iters=3)
        self.world.ClearForces()
