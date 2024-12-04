import os
from fpdf import FPDF

# Creazione del PDF
pdf = FPDF()
pdf.add_page()

# Impostazione del font
pdf.set_font("Arial", size=12)

# Titolo
pdf.set_font("Arial", 'B', 16)
pdf.cell(200, 10, txt="Report del Progetto S.A.D.A. v0.8", ln=True, align='C')

# Spazio
pdf.ln(10)

# Introduzione
pdf.set_font("Arial", 'B', 14)
pdf.cell(200, 10, txt="Introduzione", ln=True)
pdf.set_font("Arial", size=12)
intro = """Il progetto S.A.D.A. (Smart Anomaly Detection Assistant) è un'applicazione desktop sviluppata per l'analisi delle immagini con l'obiettivo di identificare e evidenziare anomalie visive. Questa versione 0.8 rappresenta un significativo miglioramento rispetto alle versioni precedenti, con l'introduzione di nuove funzionalità, correzioni di errori e ottimizzazioni dell'interfaccia utente."""
pdf.multi_cell(0, 10, intro)

# Spazio
pdf.ln(5)

# Funzionalità Principali
pdf.set_font("Arial", 'B', 14)
pdf.cell(200, 10, txt="Funzionalità Principali", ln=True)
pdf.set_font("Arial", size=12)
functionalities = [
    "1. Caricamento delle Immagini",
    "   - È possibile caricare immagini di vari formati (JPEG, PNG, BMP, TIFF) tramite un file dialog.",
    "   - Le immagini caricate vengono ridimensionate per adattarsi al canvas mantenendo le proporzioni originali.",
    "2. Selezione delle Aree",
    "   - Selezione Poligonale: Consente all'utente di selezionare un'area irregolare dell'immagine facendo clic sui punti del contorno.",
    "   - Selezione Rettangolare Standard: Consente di selezionare un'area rettangolare dell'immagine.",
    "3. Zoom",
    "   - Zoom In/Out: Consente di ingrandire o rimpicciolire l'intera immagine.",
    "   - Zoom to Selection: Consente di ingrandire l'area selezionata per una visualizzazione più dettagliata.",
    "4. Panoramica",
    "   - Consente di spostare l'immagine ingrandita all'interno del canvas per esplorare diverse parti dell'immagine.",
    "5. Modifica della Luminosità e del Contrasto",
    "   - Le barre di scorrimento per luminosità e contrasto consentono di regolare questi parametri sull'intera immagine o solo sull'area selezionata.",
    "   - Le modifiche non sono cumulative; tornare al valore di default (100) ripristina l'immagine ai valori originali.",
    "6. Analisi delle Anomalie",
    "   - Analizza l'immagine per rilevare anomalie visive (es. pixel più scuri o più chiari).",
    "   - Le anomalie possono essere evidenziate con colori specifici e l'intensità dell'analisi può essere regolata tramite il parametro threshold.",
    "7. Gestione della Storia",
    "   - Funzioni di undo e redo permettono di navigare tra le modifiche effettuate all'immagine.",
    "8. Salvataggio dell'Immagine",
    "   - Consente di salvare l'immagine analizzata in vari formati.",
    "9. Reset",
    "   - Ripristina l'immagine originale eliminando tutte le modifiche e le selezioni."
]
for line in functionalities:
    pdf.multi_cell(0, 10, line)

# Spazio
pdf.ln(5)

# Errori Maggiormente Riscontrati e Problemi Risolti
pdf.set_font("Arial", 'B', 14)
pdf.cell(200, 10, txt="Errori Maggiormente Riscontrati e Problemi Risolti", ln=True)
pdf.set_font("Arial", size=12)
errors = [
    "1. Errore di Selezione e Analisi",
    "   - Problema: L'analisi dell'immagine avveniva su tutta l'immagine invece che sull'area selezionata.",
    "   - Soluzione: È stata migliorata la gestione delle coordinate e degli offset per garantire che l'analisi fosse limitata all'area selezionata.",
    "2. Zoom to Selection",
    "   - Problema: L'area ingrandita non corrispondeva correttamente alla selezione effettuata.",
    "   - Soluzione: Sono state corrette le coordinate di zoom per garantire che l'area selezionata venisse visualizzata correttamente.",
    "3. Modifica Cumulativa di Luminosità e Contrasto",
    "   - Problema: Le modifiche a luminosità e contrasto si accumulavano, rendendo difficile il ripristino dei valori originali.",
    "   - Soluzione: È stata implementata una logica per applicare le modifiche solo sull'immagine originale o analizzata, senza accumulare i cambiamenti.",
    "4. Reset",
    "   - Problema: Il reset non eliminava correttamente le selezioni effettuate, richiedendo un doppio clic.",
    "   - Soluzione: Il metodo go_home è stato aggiornato per ripristinare correttamente l'immagine originale e rimuovere tutte le selezioni al primo clic."
]
for line in errors:
    pdf.multi_cell(0, 10, line)

# Spazio
pdf.ln(5)

# Tempo Impiegato
pdf.set_font("Arial", 'B', 14)
pdf.cell(200, 10, txt="Tempo Impiegato", ln=True)
pdf.set_font("Arial", size=12)
time_spent = """- Tempo della conversazione: La conversazione ha richiesto diverse ore, suddivise in più sessioni, per un totale di circa 10-12 ore di dialogo attivo.
- Tempo stimato per le modifiche: Considerando il tempo per la scrittura del codice, la risoluzione degli errori e i test, si stima un tempo complessivo di 20-25 ore per implementare e verificare tutte le funzionalità descritte."""
pdf.multi_cell(0, 10, time_spent)

# Spazio
pdf.ln(5)

# Miglioramenti Futuri
pdf.set_font("Arial", 'B', 14)
pdf.cell(200, 10, txt="Miglioramenti Futuri", ln=True)
pdf.set_font("Arial", size=12)
improvements = [
    "1. Ottimizzazione delle Prestazioni",
    "   - Implementare tecniche di caching per migliorare le prestazioni durante la modifica di immagini di grandi dimensioni.",
    "2. Supporto per Altri Formati di File",
    "   - Estendere il supporto ad altri formati di file, come RAW e HEIF.",
    "3. Interfaccia Utente Migliorata",
    "   - Migliorare l'interfaccia utente con icone e layout più intuitivi per una migliore esperienza utente.",
    "4. Funzionalità Avanzate di Analisi",
    "   - Aggiungere algoritmi di analisi delle immagini più avanzati, come il rilevamento di bordi e l'analisi dei pattern.",
    "5. Integrazione con Servizi Cloud",
    "   - Consentire il salvataggio e il caricamento di immagini direttamente da servizi cloud come Google Drive e Dropbox.",
    "6. Supporto Multilingua",
    "   - Implementare il supporto per più lingue per rendere l'applicazione accessibile a un pubblico più ampio."
]
for line in improvements:
    pdf.multi_cell(0, 10, line)

# Salva il PDF nella stessa directory del file .py
pdf_output_path = os.path.join(os.path.dirname(__file__), "SADA_Report_v0.8.pdf")
pdf.output(pdf_output_path)