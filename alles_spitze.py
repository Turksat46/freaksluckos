import pygame
import secrets

# --- Konstanten (Alles Spitze spezifisch) ---
SYMBOL_SIZE = 80
NUM_REELS = 1
NUM_ROWS = 3
# Erweitertes SYMBOLS-Array mit "halben" Symbolen
SYMBOLS = [
    "devil", "clover", "coin", "ladybug", "sun",
    "devil_clover", "clover_coin", "coin_ladybug", "ladybug_sun", "sun_devil" #Halbe Symbole unten
]

RISK_LADDER_STEPS = [0, 2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 100, 150, 250, "top"]

# Angepasste SYMBOL_WEIGHTS (Beispiel - muss feinabgestimmt werden!)
SYMBOL_WEIGHTS = [
    0.25, 0.15, 0.12, 0.08, 0.03,  # Ganze Symbole
    0.075, 0.075, 0.07, 0.06, 0.09  # Halbe Symbole (Summe muss 1 ergeben)
]


# --- Alles Spitze Klasse ---
class AllesSpitze:
    def __init__(self, screen, font, rng):
        self.screen = screen
        self.font = font
        self.rng = rng
        self.tower = ["devil", "devil", "devil"]
        self.current_risk_level = 0
        self.game_state = "idle"
        self.last_win = 0
        self.bet = 0

    def weighted_choice(self, choices, weights):
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

        # --- Gewinnlogik (angepasst für halbe Symbole) ---
        top_symbol = self.tower[0]

        if "_" in top_symbol:  # Halbes Symbol -> Kein Gewinn
            self.last_win = 0
            self.game_state = "idle"
            print(f"Spin Tower: Halbes Symbol - Kein Gewinn. Neuer Zustand: {self.game_state}")
            return False, 0

        if top_symbol == "devil":
            self.last_win = 0
            self.current_risk_level = 0
            self.game_state = "idle"
            print(f"Spin Tower: Teufel. Neuer Zustand: {self.game_state}")
            return False, 0

        if top_symbol == "sun":
            self.current_risk_level = len(RISK_LADDER_STEPS) - 1
            self.last_win = RISK_LADDER_STEPS[self.current_risk_level]
            self.game_state = "won"
            print(f"Spin Tower: Sonne. Neuer Zustand: {self.game_state}")
            return True, self.last_win

        if top_symbol in ["clover", "coin", "ladybug"]:
            if self.current_risk_level < len(RISK_LADDER_STEPS) - 1:
                self.current_risk_level += 1
            self.last_win = RISK_LADDER_STEPS[self.current_risk_level]
            self.game_state = "risk_game"
            print(f"Spin Tower: Gewinn. Neuer Zustand: {self.game_state}")
            return True, self.last_win

        # Sollte nicht erreicht werden
        self.game_state = "idle"
        return False, 0

    def risk_game(self, choice):
        """Führt das Risikospiel durch (unverändert)."""
        print(f"Risk Game ({choice}): Aktueller Zustand: {self.game_state}")
        if choice == "risk":
            if self.rng.random() < 0.5:
                if self.current_risk_level < len(RISK_LADDER_STEPS) - 1:
                    self.current_risk_level += 1
                self.last_win = RISK_LADDER_STEPS[self.current_risk_level]
                if RISK_LADDER_STEPS[self.current_risk_level] == "top":
                    self.game_state = "won"
                print(f"Risk Game ({choice}): Neuer Zustand: {self.game_state}")
                return True, self.last_win
            else:
                self.current_risk_level = 0
                self.last_win = 0
                self.game_state = "idle"
                print(f"Risk Game ({choice}): Neuer Zustand: {self.game_state}")
                return False, 0

        elif choice == "collect":
            self.game_state = "idle"
            print(f"Risk Game ({choice}): Neuer Zustand: {self.game_state}")
            return False, self.last_win

    def draw_tower(self):
        """Zeichnet den Turm (angepasst für halbe Symbole)."""
        y_offset = self.screen.get_height() - (NUM_ROWS * SYMBOL_SIZE) - 50

        for i, symbol in enumerate(self.tower):
            if "_" in symbol:  # Halbes Symbol
                # Teile den Symbolnamen in zwei Teile
                symbol1, symbol2 = symbol.split("_")
                img_path1 = f"images/{symbol1}.png"
                img_path2 = f"images/{symbol2}.png"

                try:
                    # Lade beide Bilder
                    img1 = pygame.image.load(img_path1)
                    img1 = pygame.transform.scale(img1, (SYMBOL_SIZE, SYMBOL_SIZE))
                    img2 = pygame.image.load(img_path2)
                    img2 = pygame.transform.scale(img2, (SYMBOL_SIZE, SYMBOL_SIZE))

                    # Zeichne die obere Hälfte von img1 und die untere Hälfte von img2
                    self.screen.blit(img1, (self.screen.get_width() // 2 - SYMBOL_SIZE // 2, y_offset + i * SYMBOL_SIZE), area=(0, 0, SYMBOL_SIZE, SYMBOL_SIZE // 2))
                    self.screen.blit(img2, (self.screen.get_width() // 2 - SYMBOL_SIZE // 2, y_offset + i * SYMBOL_SIZE + SYMBOL_SIZE // 2), area=(0, SYMBOL_SIZE // 2, SYMBOL_SIZE, SYMBOL_SIZE // 2))

                except FileNotFoundError:
                    # Fallback: Zeichne ein geteiltes Rechteck
                    pygame.draw.rect(self.screen, RED, (self.screen.get_width() // 2 - SYMBOL_SIZE // 2, y_offset + i * SYMBOL_SIZE, SYMBOL_SIZE, SYMBOL_SIZE // 2))
                    pygame.draw.rect(self.screen, BLUE, (self.screen.get_width() // 2 - SYMBOL_SIZE // 2, y_offset + i * SYMBOL_SIZE + SYMBOL_SIZE//2, SYMBOL_SIZE, SYMBOL_SIZE // 2))
                    text1 = self.font.render(symbol1, True, BLACK)
                    text2 = self.font.render(symbol2, True, BLACK)
                    self.screen.blit(text1, (self.screen.get_width()//2 - text1.get_width()//2, y_offset + i * SYMBOL_SIZE))
                    self.screen.blit(text2, (self.screen.get_width()//2 - text2.get_width()//2, y_offset + i*SYMBOL_SIZE + SYMBOL_SIZE//2))


            else:  # Ganzes Symbol (wie vorher)
                img_path = f"images/{symbol}.png"
                try:
                    img = pygame.image.load(img_path)
                    img = pygame.transform.scale(img, (SYMBOL_SIZE, SYMBOL_SIZE))
                    self.screen.blit(img, (self.screen.get_width() // 2 - SYMBOL_SIZE // 2, y_offset + i * SYMBOL_SIZE))
                except FileNotFoundError:
                    pygame.draw.rect(self.screen, RED, (self.screen.get_width() // 2 - SYMBOL_SIZE // 2, y_offset + i * SYMBOL_SIZE, SYMBOL_SIZE, SYMBOL_SIZE))
                    text = self.font.render(symbol, True, BLACK)
                    self.screen.blit(text, (self.screen.get_width() // 2 - text.get_width() // 2, y_offset + i * SYMBOL_SIZE + SYMBOL_SIZE // 2 - text.get_height() // 2))


    def draw_risk_ladder(self):
        """Zeichnet die Risikoleiter (unverändert)."""
        x = 50
        y_start = 100
        y_step = 30

        for i, value in enumerate(RISK_LADDER_STEPS):
            color = WHITE
            if i == self.current_risk_level:
                color = GREEN

            text = self.font.render(str(value), True, color)
            self.screen.blit(text, (x, y_start + i * y_step))

    def reset_game(self):
        """Setzt das Spiel zurück."""
        self.tower = ["devil", "devil", "devil"]
        self.current_risk_level = 0
        self.game_state = "idle"
        self.last_win = 0

    def update(self):
        """Aktualisiert die Spielanzeige."""
        if self.game_state in ["spinning", "risk_game", "won"]:
            self.draw_tower()
            self.draw_risk_ladder()

        if self.game_state == "risk_game":
            risk_text = self.font.render("Risiko? (R) oder Sammeln? (C)", True, (255, 255, 255))
            self.screen.blit(risk_text, (self.screen.get_width() // 2 - risk_text.get_width() // 2, 50))
        elif self.game_state == "won":
            win_text = self.font.render(f"Gewonnen: {self.last_win}", True, (0, 255, 0))
            self.screen.blit(win_text, (self.screen.get_width() // 2 - win_text.get_width() // 2, 50))