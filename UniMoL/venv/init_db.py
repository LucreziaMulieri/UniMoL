import sqlite3
import os
from datetime import datetime, timedelta

# Rimuovi database esistente
if os.path.exists("database.db"):
    os.remove("database.db")

conn = sqlite3.connect("database.db")
c = conn.cursor()

# === UTENTI ===
c.execute('''
CREATE TABLE utenti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matricola TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    ruolo TEXT NOT NULL CHECK (ruolo IN ('professore', 'ricercatore', 'studente', 'tecnico'))
)
''')


# === PARTECIPAZIONE a LEZIONI ===    per studenti
c.execute('''
CREATE TABLE partecipazioni (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utente_id INTEGER NOT NULL,
    lezione_id INTEGER NOT NULL,
    FOREIGN KEY (utente_id) REFERENCES utenti(id),
    FOREIGN KEY (lezione_id) REFERENCES lezioni(id)
)
''')

# === MATERIALI ===
c.execute('''
CREATE TABLE materiali (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descrizione TEXT NOT NULL,
    quantita INTEGER NOT NULL
)
''')

# === MATERIALI ===
c.execute('''
CREATE TABLE strumenti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descrizione TEXT NOT NULL,
    quantita INTEGER NOT NULL
)
''')
# === PRENOTAZIONI LABORATORIO ===
c.execute('''
CREATE TABLE prenotazioni (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utente_id INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('lezione', 'attività')),
    data TEXT NOT NULL,
    ora_inizio TEXT NOT NULL,
    ora_fine TEXT NOT NULL,
    descrizione TEXT,
    max_partecipanti INTEGER,
    FOREIGN KEY (utente_id) REFERENCES utenti(id)
)
''')

# === MATERIALI associati alle prenotazioni ===
c.execute('''
CREATE TABLE prenotazioni_materiali (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prenotazione_id INTEGER NOT NULL,
    materiale_id INTEGER NOT NULL,
    quantita_usata INTEGER NOT NULL,
    FOREIGN KEY (prenotazione_id) REFERENCES prenotazioni(id),
    FOREIGN KEY (materiale_id) REFERENCES materiali(id)
)
''')

# === DATI FINTI ===

# utenti
utenti = [
    ("S1119045", "Ronchini Davide", "pwd", "professore"),
    ("S1119245", "Rossi Mario", "pwd", "studente"),
    ("S1119345", "Verdi Giuseppe", "pwd", "tecnico"),
    ("S1119545", "Bianchi Luigi", "pwd", "ricercatore")
]
c.executemany("INSERT INTO utenti (matricola, username, password, ruolo) VALUES (?, ?, ?, ?)", utenti)


# materiali
materiali = [
    ("Microscopio", "Microscopio ottico ad alta risoluzione", 5),
    ("Vetrini", "Set di vetrini da laboratorio", 100),
    ("Reagente X", "Soluzione chimica reagente", 30)
]
c.executemany("INSERT INTO materiali (nome, descrizione, quantita) VALUES (?, ?, ?)", materiali)

conn.commit()
conn.close()
print("Database creato con successo.")
