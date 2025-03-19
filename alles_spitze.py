import pygame
import secrets

# --- Konstanten (Alles Spitze spezifisch) ---
SYMBOL_SIZE = 80
NUM_REELS = 1
NUM_ROWS = 3
SYMBOLS = ["joker", "clover", "coin", "blank"]
RISK_LADDER_STEPS = [0, 2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 100, 150, 250, "top"]
SYMBOL_WEIGHTS = [0.3, 0.3, 0.3, 0.1]  # Joker, Klee, Münze, Leer (anpassen!)

# --- Alles Spitze Variablen (jetzt als Klasse) ---
class AllesSpitze:
    def __init__(self, screen, font, rng):
        self.screen = screen
        self.font = font
        self.rng = rng  # Zufallsgenerator übergeben
        self.tower = ["blank", "blank", "blank"]
        self.current_risk_level = 0
        self.game_state = "idle"  # "idle", "spinning", "risk_game", "won"
        self.last_win = 0
        self.bet = 0  # Einsatz hinzugefügt


    def weighted_choice(self, choices, weights):
        """Wählt ein Element aus einer Liste mit gewichteten Wahrscheinlichkeiten."""
        total = sum(weights)
        r = self.rng.uniform(0, total)
        upto = 0
        for c, w in zip(choices, weights):
            if upto + w >= r:
                return c
            upto += w

    def spin_tower(self):
        """Simuliert das Drehen des Turms."""
        new_tower = []
        for _ in range(NUM_ROWS):
            new_tower.append(self.weighted_choice(SYMBOLS, SYMBOL_WEIGHTS))
        self.tower = new_tower

        # Gewinnlogik
        top_symbol = self.tower[0]
        if top_symbol == "blank":
            self.last_win = 0
            self.game_state = "idle"
            return False, 0

        if top_symbol == "joker":
            self.current_risk_level = len(RISK_LADDER_STEPS) - 1
            self.last_win = RISK_LADDER_STEPS[self.current_risk_level]
            self.game_state = "won"
            return True, self.last_win

        if self.current_risk_level < len(RISK_LADDER_STEPS) - 1:
            self.current_risk_level += 1
        self.last_win = RISK_LADDER_STEPS[self.current_risk_level]
        self.game_state = "risk_game"
        return True, self.last_win

    def risk_game(self, choice):
        """Führt das Risikospiel durch."""
        if choice == "risk":
            if self.rng.random() < 0.5:  # 50/50 Chance
                if self.current_risk_level < len(RISK_LADDER_STEPS) - 1:
                    self.current_risk_level += 1
                self.last_win = RISK_LADDER_STEPS[self.current_risk_level]
                if RISK_LADDER_STEPS[self.current_risk_level] == "top":
                    self.game_state = "won"
                return True, self.last_win #Rückgabe ob gewonnen und wie viel.
            else:
                self.current_risk_level = 0
                self.last_win = 0
                self.game_state = "idle"
                return False, 0

        elif choice == "collect":
            self.game_state = "idle"
            return False, self.last_win #Rückgabe: Nicht gewonnen, aber Gewinn einsammeln


    def draw_tower(self):
        """Zeichnet den Turm."""
        y_offset = self.screen.get_height() - (NUM_ROWS * SYMBOL_SIZE) - 50
        for i, symbol in enumerate(self.tower):
            if symbol != "blank":
                img_path = f"images/{symbol}.png"
                try:
                    img = pygame.image.load(img_path)
                    img = pygame.transform.scale(img, (SYMBOL_SIZE, SYMBOL_SIZE))
                    self.screen.blit(img, (self.screen.get_width() // 2 - SYMBOL_SIZE // 2, y_offset + i * SYMBOL_SIZE))
                except FileNotFoundError:
                    pygame.draw.rect(self.screen, (255, 0, 0), (self.screen.get_width() // 2 - SYMBOL_SIZE // 2, y_offset + i * SYMBOL_SIZE, SYMBOL_SIZE, SYMBOL_SIZE))
                    text = self.font.render(symbol, True, (0, 0, 0))
                    self.screen.blit(text, (self.screen.get_width() // 2 - text.get_width() // 2, y_offset + i * SYMBOL_SIZE + SYMBOL_SIZE // 2 - text.get_height() // 2))

    def draw_risk_ladder(self):
        """Zeichnet die Risikoleiter."""
        x = 50
        y_start = 100
        y_step = 30

        for i, value in enumerate(RISK_LADDER_STEPS):
            color = (255, 255, 255)
            if i == self.current_risk_level:
                color = (0, 255, 0)

            text = self.font.render(str(value), True, color)
            self.screen.blit(text, (x, y_start + i * y_step))

    def reset_game(self):
        """Setzt das Spiel zurück."""
        self.tower = ["blank", "blank", "blank"]
        self.current_risk_level = 0
        self.game_state = "idle"
        self.last_win = 0


    def update(self):
        """Aktualisiert die Spielanzeige (delegiert an Unterfunktionen)."""
        if self.game_state in ["spinning", "risk_game", "won"]:
            self.draw_tower()
            self.draw_risk_ladder()

        if self.game_state == "risk_game":
            risk_text = self.font.render("Risiko? (R) oder Sammeln? (C)", True, (255, 255, 255))
            self.screen.blit(risk_text, (self.screen.get_width() // 2 - risk_text.get_width() // 2, 50))
        elif self.game_state == "won":
            win_text = self.font.render(f"Gewonnen: {self.last_win}", True, (0, 255, 0))
            self.screen.blit(win_text, (self.screen.get_width() // 2 - win_text.get_width() // 2, 50))