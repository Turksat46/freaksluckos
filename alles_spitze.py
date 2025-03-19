import pygame
import secrets

# --- Konstanten (Layout & Aussehen) ---
SYMBOL_SIZE = 90
NUM_ROWS = 3
TOWER_POS_X = 420
TOWER_POS_Y = 150
SYMBOL_SPACING_Y = 100

NUM_REEL_SYMBOLS = 20 # Hinzugefügt: Definition für NUM_REEL_SYMBOLS
REEL_SPEED = 10 # Hinzugefügt: Definition für REEL_SPEED
SPIN_DURATION = 1500 # Hinzugefügt: Definition für SPIN_DURATION

SYMBOLS = [
    "devil", "clover", "coin", "ladybug", "sun",
    "devil_clover", "clover_coin", "coin_ladybug", "ladybug_sun", "sun_devil"
]
RISK_LADDER_STEPS = [0, 2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 100, 150, 250, "top"]
SYMBOL_WEIGHTS = [
    0.35, 0.20, 0.18, 0.12, 0.05,
    0.025, 0.025, 0.025, 0.025, 0
]


class AllesSpitze:
    def __init__(self, screen, font, rng):
        self.screen = screen
        self.font = font
        self.rng = rng
        self.reel_strip = self.create_reel_strip()
        self.reel_offset = 0
        self.tower = ["blank"] * NUM_ROWS
        self.current_risk_level = 0
        self.game_state = "idle"
        self.last_win = 0
        self.bet = 5
        self.animation_frame = 0
        self.animation_speed = 4
        self.new_tower = []

    def create_reel_strip(self):
        """Erstellt einen längeren Reel Streifen mit gewichteten Symbolen."""
        reel = []
        for _ in range(NUM_REEL_SYMBOLS):
            reel.append(self.weighted_choice(SYMBOLS, SYMBOL_WEIGHTS))
        return reel

    def weighted_choice(self, choices, weights):
        total = sum(weights)
        r = self.rng.uniform(0, total)
        upto = 0
        for c, w in zip(choices, weights):
            if upto + w >= r:
                return c
            upto += w

    def spin_tower(self):
        """Startet die Walzendrehung."""
        self.game_state = "spinning"
        self.spin_start_time = pygame.time.get_ticks()

        # Wähle zufälligen Index für das Ziel-Symbol auf dem Reel Streifen
        self.target_symbol_index = self.rng.randint(0, NUM_REEL_SYMBOLS - 1)
        return None, 0


    def animate_spin(self):
        """Animiert die Walzendrehung."""
        time_elapsed = pygame.time.get_ticks() - self.spin_start_time

        if time_elapsed < SPIN_DURATION:
            # Berechne Reel Offset basierend auf Zeit und Geschwindigkeit
            self.reel_offset = (self.reel_offset + REEL_SPEED) % (SYMBOL_SIZE * NUM_REEL_SYMBOLS)
            self.update_tower_from_reel()
            return True
        else:
            self.game_state = "process_results"
            self.process_spin_results()
            return False


    def update_tower_from_reel(self):
        """Aktualisiert den sichtbaren Turm basierend auf dem Reel Offset."""
        visible_symbols = []
        start_index = (self.reel_offset // SYMBOL_SIZE)

        for i in range(NUM_ROWS):
            reel_index = (start_index + i) % NUM_REEL_SYMBOLS
            visible_symbols.append(self.reel_strip[reel_index])

        self.tower = visible_symbols
        print(f"update_tower_from_reel: Tower Symbole: {self.tower}") # DEBUGGING


    def process_spin_results(self):
        """Wertet die Ergebnisse des Spins aus."""
        top_symbol = self.tower[0]
        print(f"process_spin_results() aufgerufen. Top Symbol: {top_symbol}")  # DEBUGGING

        if "_" in top_symbol:
            print("Halbes Symbol - Kein Gewinn")
            self.last_win = 0
            self.game_state = "idle"
            return False, 0

        if top_symbol == "devil":
            print("Teufel - Kein Gewinn")
            self.last_win = 0
            self.current_risk_level = 0
            self.game_state = "idle"
            return False, 0

        if top_symbol == "sun":
            print("Sonne - Gewinn!")
            self.current_risk_level = len(RISK_LADDER_STEPS) - 1
            self.last_win = 250
            self.game_state = "won"
            return True, self.last_win

        if top_symbol in ["clover", "coin", "ladybug"]:
            print(f"Symbol {top_symbol} - Gewinn!")
            self.current_risk_level += 1
            self.last_win = RISK_LADDER_STEPS[min(self.current_risk_level, len(RISK_LADDER_STEPS)-1)]
            self.game_state = "won"
            return True, self.last_win

        print("Kein Gewinn-Kriterium erfüllt - Kein Gewinn (Fallback)")
        self.game_state = "idle"
        return False, 0

    def risk_game(self, choice):
        return False, 0

    def draw_tower(self):
        """Zeichnet den Turm als Walze."""
        print("draw_tower() aufgerufen") # DEBUGGING
        # Fensterrahmen zeichnen (NEU)
        pygame.draw.rect(self.screen, (100, 0, 0), (TOWER_POS_X - SYMBOL_SIZE // 2 - 5, TOWER_POS_Y - SYMBOL_SIZE - 5, SYMBOL_SIZE + 10, NUM_ROWS * SYMBOL_SPACING_Y + 10), 3) # Rahmen um den Turm


        for i in range(NUM_ROWS):
            symbol = self.tower[i]
            if symbol == "blank":
                continue

            y_pos = TOWER_POS_Y + i * SYMBOL_SPACING_Y

            # Berechne Y-Offset für die Walzenbewegung
            reel_draw_offset = self.reel_offset % SYMBOL_SIZE
            y_draw_pos = y_pos - reel_draw_offset


            if "_" in symbol:
                symbol1, symbol2 = symbol.split("_")
                img_path1 = f"images/{symbol1}.png"
                img_path2 = f"images/{symbol2}.png"
                try:
                    img1 = pygame.image.load(img_path1).convert_alpha()
                    img1 = pygame.transform.scale(img1, (SYMBOL_SIZE, SYMBOL_SIZE))
                    img2 = pygame.image.load(img_path2).convert_alpha()
                    img2 = pygame.transform.scale(img2, (SYMBOL_SIZE, SYMBOL_SIZE))

                    self.screen.blit(img2, (TOWER_POS_X - SYMBOL_SIZE // 2, y_draw_pos - SYMBOL_SIZE // 2))
                    self.screen.blit(img1, (TOWER_POS_X - SYMBOL_SIZE // 2, y_draw_pos - SYMBOL_SIZE))
                    print(f"Zeichne halbes Symbol: {symbol}") # DEBUGGING

                except FileNotFoundError as e:
                    print(f"Fehler beim Laden von Bildern für halbes Symbol {symbol}: {e}") # DEBUGGING
                    pygame.draw.rect(self.screen, (255, 0, 0), (TOWER_POS_X - SYMBOL_SIZE // 2, y_draw_pos - SYMBOL_SIZE, SYMBOL_SIZE, SYMBOL_SIZE // 2))
                    pygame.draw.rect(self.screen, (0, 0, 255), (TOWER_POS_X - SYMBOL_SIZE // 2, y_draw_pos - SYMBOL_SIZE // 2, SYMBOL_SIZE, SYMBOL_SIZE // 2))
                    text1 = self.font.render(symbol1, True, (0, 0, 0))
                    text2 = self.font.render(symbol2, True, (0, 0, 0))
                    self.screen.blit(text1, (TOWER_POS_X - text1.get_width() // 2, y_draw_pos - SYMBOL_SIZE))
                    self.screen.blit(text2, (TOWER_POS_X - text2.get_width() // 2, y_draw_pos - SYMBOL_SIZE // 2))


            else: #Ganze Symbole
                img_path = f"images/{symbol}.png"
                print(f"Lade Bild für ganzes Symbol: {symbol} Pfad: {img_path}") # DEBUGGING
                try:
                    img = pygame.image.load(img_path).convert_alpha()
                    img = pygame.transform.scale(img, (SYMBOL_SIZE, SYMBOL_SIZE))
                    self.screen.blit(img, (TOWER_POS_X - SYMBOL_SIZE // 2, y_draw_pos - SYMBOL_SIZE))
                except FileNotFoundError as e:
                    print(f"Fehler beim Laden von Bild für ganzes Symbol {symbol}: {e}") # DEBUGGING
                    pygame.draw.rect(self.screen, (255, 0, 0), (TOWER_POS_X - SYMBOL_SIZE // 2, y_draw_pos - SYMBOL_SIZE, SYMBOL_SIZE, SYMBOL_SIZE))
                    text = self.font.render(symbol, True, (0, 0, 0))
                    self.screen.blit(text, (TOWER_POS_X - text.get_width() // 2, y_draw_pos - SYMBOL_SIZE + (SYMBOL_SIZE - text.get_height()) // 2))


    def draw_risk_ladder(self):
        pass

    def reset_game(self):
        self.tower = ["blank"] * NUM_ROWS
        self.current_risk_level = 0
        self.game_state = "idle"
        self.last_win = 0

    def update(self):
        """Aktualisiert den Spielzustand und die Anzeige."""
        if self.game_state == "spinning":
            if not self.animate_spin():
                self.game_state = "idle"

        self.draw_tower()