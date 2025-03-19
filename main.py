import pygame
import secrets
import time
import logging
import sqlite3
import alles_spitze  # Importiere die Spiele-Datei

# --- Konstanten ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FONT_SIZE = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# --- Initialisierung ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Merkur Automat")
clock = pygame.time.Clock()
font = pygame.font.Font(None, FONT_SIZE)

# --- Datenbank ---
db_connection = sqlite3.connect("automat.db")
db_cursor = db_connection.cursor()
db_cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
db_connection.commit()

# --- Logging ---
logging.basicConfig(filename='automat.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Zustandsautomat ---
class State:
    IDLE = 0
    PLAYING = 1
    PAYOUT = 2
    ERROR = 3  # Fehlerzustand hinzugefügt

current_state = State.IDLE
credit = 500

# --- Zufallsgenerator ---
rng = secrets.SystemRandom()

# --- Spiele-Instanz erstellen ---
spiel = alles_spitze.AllesSpitze(screen, font, rng)  # Übergabe von screen, font, und rng

# --- Funktionen für Ein-/Auszahlung (Platzhalter, unverändert) ---
def insert_coin(amount):
    global credit
    credit += amount
    logging.info(f"Münze eingeworfen: {amount}. Neues Guthaben: {credit}")

def payout():
    global credit
    logging.info(f"Auszahlung: {credit}")
    credit = 0  # Hier: Kommunikation mit Auszahlungsmodul

def handle_hardware_event(event_type, event_data):
    if event_type == "COIN_INSERTED":
        insert_coin(event_data["amount"])
    elif event_type == "PAYOUT_BUTTON_PRESSED":
        payout()
    # Weitere Ereignisse hier...

def update_display():
    screen.fill(BLACK)
    credit_text = font.render(f"Guthaben: {credit}", True, WHITE)
    screen.blit(credit_text, (10, 10))

    if current_state == State.PLAYING:
        spiel.update()  # Immer aufrufen, wenn im Spielzustand

    pygame.display.flip()

# --- Hauptschleife ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if current_state == State.PLAYING:
                if spiel.game_state == "risk_game":
                    if event.key == pygame.K_r:
                        won, amount = spiel.risk_game("risk")
                        if not won and amount == 0:  # Verloren, zurück
                            current_state = State.IDLE

                    elif event.key == pygame.K_c:
                        won, amount = spiel.risk_game("collect")  # Gewinn einsammeln
                        credit += amount  # Gewinn hinzufügen
                        current_state = State.IDLE  # Zurück

            if event.key == pygame.K_SPACE:
                if current_state == State.IDLE:
                    spiel.bet = 5  # Beispielhafter Einsatz
                    if credit >= spiel.bet:
                        credit -= spiel.bet
                        current_state = State.PLAYING
                        spiel.game_state = "spinning"
                        won, amount = spiel.spin_tower()  # Rückgabewerte für Gewinn/Verlust
                        if not won:  # Verloren
                            current_state = State.IDLE
                elif spiel.game_state == "won":  # Bei Gewinn, nach Leertaste, zurück
                    credit += spiel.last_win  # Gewinn einsammeln
                    spiel.reset_game()
                    current_state = State.IDLE

        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_state == State.IDLE:
                spiel.bet = 5
                if credit >= spiel.bet:
                    credit -= spiel.bet
                    current_state = State.PLAYING
                    spiel.game_state = "spinning"
                    won, amount = spiel.spin_tower()
                    if not won:  # Verloren
                        current_state = State.IDLE

            elif spiel.game_state == "won":  # Touch für Gewinn.
                credit += spiel.last_win  # Gewinn einsammeln
                spiel.reset_game()
                current_state = State.IDLE

    if current_state == State.PLAYING:
        if credit < spiel.bet and spiel.game_state == "idle":
            current_state = State.IDLE
            logging.warning("Nicht genugend Guthaben")

    # --- Hardware-Ereignisse (Platzhalter, unverändert) ---
    # hardware_event = get_hardware_event()
    # if hardware_event:
    #    handle_hardware_event(hardware_event["type"], hardware_event["data"])

    update_display()
    clock.tick(30)

# --- Aufräumen ---
db_connection.close()
pygame.quit()
logging.shutdown()