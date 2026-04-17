# ✦ PCTO Manager

Sistema di gestione PCTO (Percorsi per le Competenze Trasversali e l'Orientamento).

## 🚀 Avvio rapido

### Metodo 1 — Doppio click
Fai doppio click su **`avvia.py`** (richiede Python installato).

### Metodo 2 — Terminale
```bash
pip install -r requirements.txt
python server.py
```

Il browser si aprirà automaticamente su **http://127.0.0.1:8000**

---

## 📱 Pagine del sito

| URL | Descrizione |
|-----|-------------|
| `/` | Login (studente / scuola / admin) |
| `/studente` | Dashboard studente |
| `/scuola` | Pannello scuola |
| `/admin` | Pannello amministrazione |

---

## 👤 Ruoli

### 🎓 Studente
- Scegli 3 enti preferiti (con dettagli e orari)
- Vedi l'ente assegnato + orario settimanale + contatti tutor
- Accedi al questionario
- Visualizza grafici

### 🏫 Scuola
- Assegna studenti agli enti
- Visualizza assegnazioni per ente
- Grafici distribuzione studenti

### ⚙️ Admin
- Gestione completa enti (aggiungi/modifica/elimina)
- Configura orari settimanali per ente
- Lista studenti con preferenze
- Risultati questionari
- Grafici statistici

---

## 🗄️ Database

Il sistema usa **MongoDB** se disponibile su `localhost:27017`.  
Se MongoDB non è installato, funziona con **dati demo in memoria** (si perdono al riavvio).

Per installare MongoDB: https://www.mongodb.com/try/download/community

---

## 🎨 Design

Ispirato al mockup originale con:
- Palette crema + rosa #FFB5A7
- Font Playfair Display + DM Sans  
- Illustrazione paesaggio SVG nella pagina di login
- Layout responsive mobile-first
