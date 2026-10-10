
import pygame
import random

from .player import Player
from .enemy import EnemyGrid
from .bullet import Bullet

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 60, 60)
BLACK = (0, 0, 0)


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.player = Player(width // 2 - 20, height - 50, 40, 20)
        self.enemy_grid = EnemyGrid(width)

        self.player_bullets = []
        self.enemy_bullets = []

        self._shoot_cooldown = 0
        self.enemy_fire_chance = 0.0005

        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over_font = pygame.font.SysFont("Arial", 48)

        self.game_over = False
        self.won = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not self.game_over and self._shoot_cooldown <= 0:
                    bullet_x = self.player.center_x() - 2

                    self.player_bullets.append(
                        Bullet(
                            bullet_x,
                            self.player.y,
                            direction=-1
                        )
                    )

                    self._shoot_cooldown = 15

    def handle_input(self):
        if self.game_over:
            return

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move(-self.player.speed, self.width)

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move(self.player.speed, self.width)

    def update(self):
        if self.game_over:
            return

        if self._shoot_cooldown > 0:
            self._shoot_cooldown -= 1

        # Move enemies.
        self.enemy_grid.move()

        # Let living enemies fire.
        for enemy in self.enemy_grid.alive_enemies():
            if random.random() < self.enemy_fire_chance:
                bullet_x = enemy.x + enemy.width // 2

                self.enemy_bullets.append(
                    Bullet(
                        bullet_x,
                        enemy.y + enemy.height,
                        direction=1
                    )
                )

        # Move player bullets and remember their previous positions.
        for bullet in self.player_bullets:
            bullet.previous_y = bullet.y
            bullet.move()

        # Move enemy bullets.
        for bullet in self.enemy_bullets:
            bullet.move()

        # Detect player-bullet collisions.
        # Iterate over a copy so removing a bullet is safe.
        for bullet in self.player_bullets[:]:
            previous_y = getattr(bullet, "previous_y", bullet.y)

            # Check the area travelled during this frame.
            swept_top = min(previous_y, bullet.y)
            swept_height = bullet.height + abs(bullet.y - previous_y)

            swept_rect = pygame.Rect(
                bullet.x,
                swept_top,
                bullet.width,
                swept_height
            )

            for enemy in self.enemy_grid.alive_enemies():
                if swept_rect.colliderect(enemy.rect()):
                    enemy.alive = False
                    self.player_bullets.remove(bullet)
                    self.score += 1
                    break

        # Remove off-screen bullets.
        self.player_bullets = [
            bullet for bullet in self.player_bullets
            if not bullet.off_screen(self.height)
        ]

        self.enemy_bullets = [
            bullet for bullet in self.enemy_bullets
            if not bullet.off_screen(self.height)
        ]

        # Detect enemy bullets hitting the player.
        for bullet in self.enemy_bullets:
            if bullet.rect().colliderect(self.player.rect()):
                self.game_over = True
                self.won = False
                break

        # Detect enemies reaching the player's area.
        if self.enemy_grid.reached_bottom(self.player.y):
            self.game_over = True
            self.won = False

        # Win when every enemy has been destroyed.
        if not self.enemy_grid.alive_enemies():
            self.game_over = True
            self.won = True

    def render(self, screen):
        # Draw the player.
        pygame.draw.rect(screen, GREEN, self.player.rect())

        # Draw living enemies.
        for enemy in self.enemy_grid.alive_enemies():
            pygame.draw.rect(screen, WHITE, enemy.rect())

        # Draw player bullets.
        for bullet in self.player_bullets:
            pygame.draw.rect(screen, WHITE, bullet.rect())

        # Draw enemy bullets.
        for bullet in self.enemy_bullets:
            pygame.draw.rect(screen, RED, bullet.rect())

        # Display score.
        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            WHITE
        )
        screen.blit(score_text, (10, 10))

        # Draw the end screen.
        if self.game_over:
            overlay = pygame.Surface(
                (self.width, self.height),
                pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 190))
            screen.blit(overlay, (0, 0))

            if self.won:
                heading = "YOU WIN!"
                heading_color = GREEN
            else:
                heading = "GAME OVER"
                heading_color = RED

            heading_text = self.game_over_font.render(
                heading, True, heading_color
            )
            score_text = self.font.render(
                f"Final Score: {self.score}", True, WHITE
            )
            exit_text = self.font.render(
                "Close the window to exit", True, WHITE
            )

            screen.blit(
                heading_text,
                heading_text.get_rect(
                    center=(self.width // 2, self.height // 2 - 60)
                )
            )
            screen.blit(
                score_text,
                score_text.get_rect(
                    center=(self.width // 2, self.height // 2)
                )
            )
            screen.blit(
                exit_text,
                exit_text.get_rect(
                    center=(self.width // 2, self.height // 2 + 50)
                )
            )
