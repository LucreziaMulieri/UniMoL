
from flask import Flask, request, render_template, redirect, url_for, session,jsonify,flash
from datetime import datetime, time, timedelta
import sqlite3
import secrets

app = Flask(__name__)

app.secret_key = secrets.token_hex(16) 


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        matricola = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("SELECT * FROM utenti WHERE matricola = ? AND password = ?", (matricola, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['username'] = user['username']
            session['ruolo'] = user['ruolo']
            return redirect(url_for('laboratorio'))
        else:
            return "Credenziali errate", 401

    return render_template('login.html')



@app.route('/api/corsi')
def api_corsi():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM prenotazioni")
    corsi = c.fetchall()
    corsi_list = []
    for corso in corsi:
        data = corso["data"]           
        ora_inizio = corso["ora_inizio"]  
        ora_fine = corso["ora_fine"]      
        corsi_list.append({
            "title": corso["tipo"]+"  "+corso["descrizione"],
            "start": f"{data}T{ora_inizio}",
            "end": f"{data}T{ora_fine}"
        })
    conn.close()
    return jsonify(corsi_list)


@app.route('/laboratorio')
def laboratorio():
    if 'username' in session:
        return render_template('laboratorio.html', username=session['username'])
    return redirect(url_for('login'))

def get_corsi():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM prenotazioni")
    corsi = c.fetchall()
    conn.close()
    return corsi

@app.route('/corso/<int:corso_id>', methods=['GET', 'POST'])
def dettaglio_corso(corso_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM corsi WHERE id = ?", (corso_id,))
    corso = c.fetchone()

    
    c.execute("SELECT * FROM iscrizioni WHERE username = ? AND corso_id = ?", (username, corso_id))
    iscrizione = c.fetchone()

    if request.method == 'POST':
        if 'iscriviti' in request.form and not iscrizione:
            c.execute("INSERT INTO iscrizioni (username, corso_id) VALUES (?, ?)", (username, corso_id))
        elif 'cancella' in request.form and iscrizione:
            c.execute("DELETE FROM iscrizioni WHERE username = ? AND corso_id = ?", (username, corso_id))
        conn.commit()
        return redirect(url_for('dettaglio_corso', corso_id=corso_id))

    conn.close()
    return render_template('corso_dettaglio.html', corso=corso, iscrizione=iscrizione, username=username)


@app.route('/corsi')
def corsi():
    if 'username' in session:
        return render_template('corsi.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/tecnico/gestione')
def gestione():
    if 'username' in session:
        return render_template('tecnico/gestione.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/crea_corso')
def crea_corso():
    if 'username' in session:
        return render_template('crea_corsi.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/tecnico/strumenti')
def strumenti():
    if 'username' in session:
        return render_template('tecnico/strumenti.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/tecnico/crea_strumento', methods=['GET', 'POST'])
def crea_strumento():
    if request.method == 'POST':
        nome = request.form['nome']
        descrizione = request.form['descrizione']
        quantita = int(request.form['quantita'])

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO strumenti (nome, descrizione, quantita) VALUES (?, ?, ?)', (nome, descrizione, quantita))
        conn.commit()
        conn.close()

        flash("Strumento creato con successo!")
        return redirect(url_for('crea_strumento'))

    return render_template('tecnico/crea_strumento.html')

@app.route('/tecnico/modifica_strumento', methods=['GET', 'POST'])
def modifica_strumento():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if request.method == 'POST':
        id_materiale = request.form['id']
        nome = request.form['nome']
        descrizione = request.form['descrizione']
        quantita = request.form['quantita']

        c.execute('''
            UPDATE strumenti
            SET nome = ?, descrizione = ?, quantita = ?
            WHERE id = ?
        ''', (nome, descrizione, quantita, id_materiale))
        conn.commit()
        flash('Strumento modificato con successo!')

    c.execute('SELECT * FROM strumenti')
    st = c.fetchall()
    conn.close()
    return render_template('tecnico/modifica_strumento.html',st=st)

@app.route('/tecnico/elimina_strumento', methods=['GET', 'POST'])
def elimina_strumento():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if request.method == 'POST':
        id_materiale = request.form['id']
        c.execute('DELETE FROM strumenti WHERE id = ?', (id_materiale,))
        conn.commit()
        flash('Strumento eliminato con successo!')

    c.execute('SELECT * FROM strumenti')
    st = c.fetchall()
    conn.close()
    return render_template('tecnico/elimina_strumento.html', st=st)

@app.route('/tecnico/materiali')
def materiali():
    if 'username' in session:
        return render_template('tecnico/materiali.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/tecnico/crea_materiale', methods=['GET', 'POST'])
def crea_materiale():
    if request.method == 'POST':
        nome = request.form['nome']
        descrizione = request.form['descrizione']
        quantita = int(request.form['quantita'])

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO materiali (nome, descrizione, quantita) VALUES (?, ?, ?)', (nome, descrizione, quantita))
        conn.commit()
        conn.close()

        flash("Materiale creato con successo!")
        return redirect(url_for('crea_materiale'))

    return render_template('tecnico/crea_materiale.html')

@app.route('/tecnico/modifica_materiale', methods=['GET', 'POST'])
def modifica_materiale():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if request.method == 'POST':
        id_materiale = request.form['id']
        nome = request.form['nome']
        descrizione = request.form['descrizione']
        quantita = request.form['quantita']

        c.execute('''
            UPDATE materiali
            SET nome = ?, descrizione = ?, quantita = ?
            WHERE id = ?
        ''', (nome, descrizione, quantita, id_materiale))
        conn.commit()
        flash('Materiale modificato con successo!')

    c.execute('SELECT * FROM materiali')
    materiali = c.fetchall()
    conn.close()
    return render_template('tecnico/modifica_materiale.html', materiali=materiali)

@app.route('/tecnico/elimina_materiale', methods=['GET', 'POST'])
def elimina_materiale():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if request.method == 'POST':
        id_materiale = request.form['id']
        c.execute('DELETE FROM materiali WHERE id = ?', (id_materiale,))
        conn.commit()
        flash('Materiale eliminato con successo!')

    c.execute('SELECT * FROM materiali')
    materiali = c.fetchall()
    conn.close()
    return render_template('tecnico/elimina_materiale.html', materiali=materiali)

def get_utente():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM utenti WHERE username = ?", (session['username'],))
    utente = c.fetchone()
    conn.close()
    return utente

# --- CREAZIONE PRENOTAZIONE ---
@app.route('/prenotazione', methods=['GET', 'POST'])
def prenotazione():
    if 'username' not in session or session['ruolo'] not in ['professore', 'ricercatore']:
        flash("Accesso non autorizzato.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        tipo = request.form['tipo']
        data_str = request.form['data']
        ora_inizio = request.form['ora_inizio']
        ora_fine = request.form['ora_fine']
        descrizione = request.form['descrizione']
        max_partecipanti = int(request.form['max_partecipanti'])

        try:
            data = datetime.strptime(data_str, '%Y-%m-%d').date()
            inizio = datetime.strptime(ora_inizio, '%H:%M').time()
            fine = datetime.strptime(ora_fine, '%H:%M').time()

            if data.weekday() >= 5:
                flash("Non puoi prenotare in un giorno festivo o weekend.")
                return redirect(url_for('prenotazione'))

            if inizio < time(7, 30) or fine > time(19, 0) or inizio >= fine:
                flash("Orario non valido. Orari ammessi: 07:30 - 19:00")
                return redirect(url_for('prenotazione'))

            if tipo == 'lezione' and (datetime.combine(data, fine) - datetime.combine(data, inizio)) > timedelta(hours=2):
                flash("Una lezione può durare al massimo 2 ore.")
                return redirect(url_for('prenotazione'))

            if data < datetime.now().date() + timedelta(days=5):
                flash("Prenotazioni possibili solo con almeno 5 giorni di anticipo.")
                return redirect(url_for('prenotazione'))

            if max_partecipanti > 20:
                flash("Massimo 20 partecipanti consentiti.")
                return redirect(url_for('prenotazione'))

            utente = get_utente()
            conn = sqlite3.connect('database.db')
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            c.execute("""
                SELECT * FROM prenotazioni
                WHERE data = ?
                AND (
                    (ora_inizio <= ? AND ora_fine > ?) OR
                    (ora_inizio < ? AND ora_fine >= ?)
                )
            """, (data_str, ora_inizio, ora_inizio, ora_fine, ora_fine))
            conflitti = c.fetchall()

            if conflitti:
                flash("Esiste già una prenotazione in questo orario.")
                return redirect(url_for('prenotazione'))

            c.execute("""
                INSERT INTO prenotazioni (utente_id, tipo, data, ora_inizio, ora_fine, descrizione, max_partecipanti)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (utente['id'], tipo, data_str, ora_inizio, ora_fine, descrizione, max_partecipanti))

            conn.commit()
            conn.close()
            flash("Prenotazione registrata con successo!")
            return redirect(url_for('prenotazione'))

        except Exception as e:
            flash(f"Errore: {e}")
            return redirect(url_for('prenotazione'))

    return render_template('prof_rice/prenotazione.html')
    
@app.route('/modifica_prenotazione', methods=['GET', 'POST'])
def modifica_prenotazione(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    utente = get_utente()
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM prenotazioni WHERE id = ?', (id,))
    pren = c.fetchone()

    if not pren or pren['utente_id'] != utente['id']:
        flash("Prenotazione non trovata o non autorizzato.")
        return redirect(url_for('prenotazione'))

    data_pren = datetime.strptime(pren['data'], '%Y-%m-%d').date()
    if data_pren <= datetime.now().date() + timedelta(days=3):
        flash("Modifiche consentite solo fino a 3 giorni prima.")
        return redirect(url_for('prenotazione'))

    if request.method == 'POST':
        data_str = request.form['data']
        ora_inizio = request.form['ora_inizio']
        ora_fine = request.form['ora_fine']
        descrizione = request.form['descrizione']

        c.execute('''
            UPDATE prenotazioni
            SET data = ?, ora_inizio = ?, ora_fine = ?, descrizione = ?
            WHERE id = ?
        ''', (data_str, ora_inizio, ora_fine, descrizione, id))
        conn.commit()
        conn.close()
        flash("Prenotazione modificata con successo.")
        return redirect(url_for('prenotazione'))

    conn.close()
    return render_template('prof_rice/modifica_prenotazione.html', pren=pren)

# --- ELIMINA PRENOTAZIONE ---
@app.route('/elimina_prenotazione', methods=['POST'])
def elimina_prenotazione(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    utente = get_utente()
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM prenotazioni WHERE utente_id = ? ORDER BY data, ora_inizio', (utente['id'],))
    prenotazioni = c.fetchall()
    conn.close()

    return render_template('le_mie_prenotazioni.html', prenotazioni=prenotazioni)

if __name__ == '__main__':
    app.run(debug=True)



#if __name__ == "__main__":
  #   from waitress import serve
 #   serve(app, host="0.0.0.0", port=5000)
