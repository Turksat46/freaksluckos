import pygame
import secrets
import time
import logging
import sqlite3
import alles_spitze

# --- Konstanten ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_RED = (100, 0, 0)
GREY = (128, 128, 128)
GOLD = (255, 215, 0)

TITLE_POS_Y = 20
SYMBOL_BOX_WIDTH = 150
SYMBOL_BOX_HEIGHT = 400
SYMBOL_BOX_LEFT_X = 20
SYMBOL_BOX_RIGHT_X = SCREEN_WIDTH - SYMBOL_BOX_WIDTH - 20
CASH_POT_POS_Y = 540
CONTROL_PANEL_POS_Y = 500
BOTTOM_BAR_HEIGHT = 60
CREDIT_DISPLAY_POS_X = 150
CREDIT_DISPLAY_POS_Y = SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT + 15

# --- Initialisierung ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Merkur Alles Spitze 1:1 Reel")
clock = pygame.time.Clock()

try:
    font_title = pygame.font.Font("casino.ttf", 48)
    font_labels = pygame.font.Font("விலானᮼ.ttf", 18)
    font_small_labels = pygame.font.Font("விலானᮼ.ttf", 14)
except FileNotFoundError:
    font_title = pygame.font.Font(None, 40)
    font_labels = pygame.font.Font(None, 18)
    font_small_labels = pygame.font.Font(None, 14)
    print("Schriftarten nicht gefunden! Verwende Systemschriftarten.")

db_connection = sqlite3.connect("automat.db")
db_cursor = db_connection.cursor()
db_cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
db_connection.commit()
logging.basicConfig(filename='automat.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Zustandsautomat ---
class State:
    IDLE = 0
    PLAYING = 1
    ANIMATING = 2

current_state = State.IDLE
credit = 500

# --- Zufallsgenerator & Spiele-Instanz ---
rng = secrets.SystemRandom()
spiel = alles_spitze.AllesSpitze(screen, font_labels, rng)

# --- Funktionen für Ein-/Auszahlung ---
def insert_coin(amount):
    global credit
    credit += amount
    logging.info(f"Münze eingeworfen: {amount}. Neues Guthaben: {credit}")

def payout():
    global credit
    logging.info(f"Auszahlung: {credit}")
    credit = 0
def handle_hardware_event(event_type, event_data):
    if event_type == "COIN_INSERTED":
        insert_coin(event_data["amount"])
    elif event_type == "PAYOUT_BUTTON_PRESSED":
        payout()


# --- Zeichenfunktionen ---
def draw_title():
    title_text = font_title.render("Alles Spitze", True, GOLD)
    title_rect = title_text.get_rect(midtop=(SCREEN_WIDTH // 2, TITLE_POS_Y))
    screen.blit(title_text, title_rect)

def draw_symbol_boxes():
    pygame.draw.rect(screen, DARK_RED, (SYMBOL_BOX_LEFT_X, TITLE_POS_Y, SYMBOL_BOX_WIDTH, SYMBOL_BOX_HEIGHT), 3)
    pygame.draw.rect(screen, DARK_RED, (SYMBOL_BOX_RIGHT_X, TITLE_POS_Y, SYMBOL_BOX_WIDTH, SYMBOL_BOX_HEIGHT), 3)

def draw_cash_pot_text():
    cash_pot_text = font_title.render("CASH POT", True, GOLD)
    cash_pot_rect = cash_pot_text.get_rect(midtop=(SCREEN_WIDTH // 2, CASH_POT_POS_Y))
    screen.blit(cash_pot_text, cash_pot_rect)

def draw_control_panel():
    pygame.draw.rect(screen, DARK_RED, (0, CONTROL_PANEL_POS_Y, SCREEN_WIDTH, SCREEN_HEIGHT - CONTROL_PANEL_POS_Y))
    pygame.draw.rect(screen, BLACK, (0, CONTROL_PANEL_POS_Y + 5, SCREEN_WIDTH, SCREEN_HEIGHT - CONTROL_PANEL_POS_Y - 10))

def draw_bottom_bar():
    pygame.draw.rect(screen, DARK_RED, (0, SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT, SCREEN_WIDTH, BOTTOM_BAR_HEIGHT))
    geldspeicher_text = font_small_labels.render("GELDSPEICHER (EURO)", True, WHITE)
    screen.blit(geldspeicher_text, (20, SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT + 5))
    credit_text = font_labels.render(f"{credit:.2f}", True, GOLD)
    screen.blit(credit_text, (CREDIT_DISPLAY_POS_X, CREDIT_DISPLAY_POS_Y))
    bank_bits_text = font_small_labels.render("BANK-BITS", True, WHITE)
    erfolg_bits_text = font_small_labels.render("ERFOLG-BITS", True, WHITE)
    level_bits_text = font_small_labels.render("LEVEL-BITS", True, WHITE)
    screen.blit(bank_bits_text, (300, SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT + 5))
    screen.blit(erfolg_bits_text, (450, SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT + 5))
    screen.blit(level_bits_text, (600, SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT + 5))
    bank_bits_value = font_labels.render("10000", True, GOLD)
    erfolg_bits_value = font_labels.render("0", True, GOLD)
    level_bits_value = font_labels.render("200", True, GOLD)
    screen.blit(bank_bits_value, (300, SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT + 25))
    screen.blit(erfolg_bits_value, (450, SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT + 25 ))
    screen.blit(level_bits_value, (600, SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT + 25))
    euro_text = font_small_labels.render("EURO", True, WHITE)
    bits_text = font_small_labels.render("BITS", True, WHITE)
    unterhaltung_text = font_small_labels.render("UNTERHALTUNG MIT BITS", True, WHITE)
    screen.blit(euro_text, (20, SCREEN_HEIGHT - 20))
    screen.blit(bits_text, (370, SCREEN_HEIGHT - 20))
    screen.blit(unterhaltung_text, (550, SCREEN_HEIGHT - 20))

def update_display():
    """Zeichnet den gesamten Bildschirm."""
    print(f"update_display(): current_state = {current_state}, spiel.game_state = {spiel.game_state}") # Debugging
    screen.fill(BLACK)

    draw_title()
    draw_symbol_boxes()
    draw_cash_pot_text()
    draw_control_panel()
    draw_bottom_bar()

    credit_text = font_labels.render(f"{credit:.2f}", True, GOLD)
    screen.blit(credit_text, (CREDIT_DISPLAY_POS_X, CREDIT_DISPLAY_POS_Y))

    if current_state == State.PLAYING or current_state == State.ANIMATING:
        spiel.update()

        if spiel.game_state == "won":
            win_message = font_title.render(f"Gewonnen: {spiel.last_win:.2f} EURO!", True, GOLD)
            screen.blit(win_message, (SCREEN_WIDTH // 2 - win_message.get_width() // 2, 100))

    pygame.display.flip()
    print(f"update_display() beendet") # Debugging


# --- Hauptschleife ---
running = True
while running:
    print(f"--- Schleifenstart: current_state = {current_state}, spiel.game_state = {spiel.game_state} ---") # Debugging
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_SPACE:
                if current_state == State.IDLE:
                    print("Zustand ist IDLE, Leertaste gedrückt") # Debugging
                    if credit >= spiel.bet:
                        credit -= spiel.bet
                        current_state = State.ANIMATING
                        print("Zustandswechsel zu ANIMATING") # Debugging
                        spiel.spin_tower()
                        print("spin_tower() aufgerufen") # Debugging

                elif current_state == State.PLAYING:
                    pass


        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_state == State.IDLE:
                if credit >= spiel.bet:
                    credit -= spiel.bet
                    current_state = State.ANIMATING
                    spiel.spin_tower()

            elif current_state == State.PLAYING:
                pass


    if current_state == State.ANIMATING:
        if spiel.game_state == "idle" or spiel.game_state == "won":
            current_state = State.IDLE
            if spiel.game_state == "won":
                credit += spiel.last_win
                spiel.reset_game()

    if current_state == State.PLAYING: # Dieser Zustand wird aktuell nicht genutzt
        pass

    update_display()
    clock.tick(30)
    print(f"Ereignisse verarbeitet") # Debugging

# --- Aufräumen ---
db_connection.close()
pygame.quit()
logging.shutdown()