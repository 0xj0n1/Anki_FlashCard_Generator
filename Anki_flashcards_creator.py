# import required packages
import PyPDF2
import os
from openai import OpenAI
import sys

# SICHERE Methode für API-Schlüssel
# Option 1: Umgebungsvariable verwenden (empfohlen)
api_key = os.environ.get("OPENAI_API_KEY")

# Option 2: Aus einer separaten, nicht unter Versionskontrolle stehenden Datei laden
if not api_key:
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.strip().startswith("OPENAI_API_KEY="):
                    api_key = line.strip().split("=", 1)[1].strip()
                    break
    except Exception as e:
        print(f"Fehler beim Lesen der .env-Datei: {e}")

# Prüfen ob API-Schlüssel vorhanden ist
if not api_key:
    print("Fehler: Kein OpenAI API-Schlüssel gefunden.")
    print("Bitte setzen Sie die Umgebungsvariable OPENAI_API_KEY oder erstellen Sie eine .env-Datei.")
    sys.exit(1)

# OpenAI Client initialisieren
client = OpenAI(api_key=api_key)


ROOT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
SOURCE_DIR = os.path.join(ROOT_DIRECTORY, "SOURCE_DOCUMENTS")
OUTPUT_DIR = ROOT_DIRECTORY

# Sicherstellen, dass das Quellverzeichnis existiert
if not os.path.exists(SOURCE_DIR):
    os.makedirs(SOURCE_DIR)
    print(f"Verzeichnis erstellt: {SOURCE_DIR}")
    print("Bitte legen Sie Ihre PDF-Dateien in diesem Verzeichnis ab.")

# Read PDF
def read_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = " ".join([page.extract_text() for page in reader.pages])
        return text
    except FileNotFoundError:
        print(f"Fehler: Die Datei {file_path} wurde nicht gefunden.")
        print(f"Bitte legen Sie die PDF-Datei im Verzeichnis {SOURCE_DIR} ab.")
        return None
    except Exception as e:
        print(f"Fehler beim Lesen der PDF-Datei: {e}")
        return None

# dividing text into smaller chunks:
def divide_text(text, section_size):
    sections = []
    start = 0
    end = section_size
    while start < len(text):
        section = text[start:end]
        sections.append(section)
        start = end
        end += section_size
    return sections

# Create Anki cards
def create_anki_cards(pdf_text):
    if not pdf_text:
        return False
        
    SECTION_SIZE = 1000
    divided_sections = divide_text(pdf_text, SECTION_SIZE)
    generated_flashcards = ''
    
    print(f"Verarbeite {len(divided_sections)} Textabschnitte...")
    
    try:
        for i, text in enumerate(divided_sections):
            print(f"Verarbeite Abschnitt {i+1}/{len(divided_sections)}...")
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Create anki flashcards with the provided text using a format: question;answer next line question;answer etc. Keep question and the corresponding answer on the same line {text}"}
            ]

            # Neue OpenAI API-Syntax verwenden
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages, 
                temperature=0.3,
                max_tokens=2048
            )

            response_from_api = response.choices[0].message.content
            generated_flashcards += response_from_api + "\n\n"
            
            # Diese Zeile entfernt, damit alle Abschnitte verarbeitet werden
            # if i==0:
            #    break

        # Speichern mit vollständigem Pfad
        output_path = os.path.join(OUTPUT_DIR, "flashcards.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(generated_flashcards)
        
        print(f"Erfolgreich! Flashcards wurden in {output_path} gespeichert.")
        return True
    
    except Exception as e:
        print(f"Fehler bei der Erstellung der Flashcards: {e}")
        return False

# Main script execution
if __name__ == "__main__":
    # PDF-Datei
    pdf_file = "Global Business - Unit 2.pdf"
    pdf_path = os.path.join(SOURCE_DIR, pdf_file)
    
    # Prüfen, ob die Datei existiert
    if not os.path.exists(pdf_path):
        print(f"Die Datei {pdf_file} wurde nicht gefunden in {SOURCE_DIR}.")
        print("Verfügbare PDF-Dateien:")
        pdf_files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith('.pdf')]
        
        if pdf_files:
            for i, file in enumerate(pdf_files):
                print(f"{i+1}. {file}")
            selection = input("Wählen Sie eine Datei aus (Nummer eingeben) oder drücken Sie Enter, um zu beenden: ")
            
            if selection.isdigit() and 1 <= int(selection) <= len(pdf_files):
                pdf_file = pdf_files[int(selection)-1]
                pdf_path = os.path.join(SOURCE_DIR, pdf_file)
            else:
                print("Keine gültige Auswahl. Programm wird beendet.")
                sys.exit(1)
        else:
            print(f"Keine PDF-Dateien in {SOURCE_DIR} gefunden.")
            sys.exit(1)
    
    # PDF lesen und Flashcards erstellen
    print(f"Lese PDF: {pdf_file}...")
    pdf_text = read_pdf(pdf_path)
    
    if pdf_text:
        print("PDF erfolgreich gelesen. Erstelle Flashcards...")
        create_anki_cards(pdf_text)
    else:
        print("Programm wird beendet, da die PDF-Datei nicht gelesen werden konnte.")





