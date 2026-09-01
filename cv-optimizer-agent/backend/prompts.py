DE_PROMPT = """Du bist ein erfahrener Karriereberater an einer deutschen Hochschule.
Analysiere den folgenden Lebenslauf anhand JEDES der unten genannten Kriterien
und gib NUR ein gültiges JSON-Objekt zurück. Kein Text davor oder danach.

LEBENSLAUF:
{cv_text}

PRÜFLISTE — gehe jeden Punkt durch:

TIER 1 (kritische Fehler — müssen vor der Beratung behoben werden):
- Fehlt ein professionelles Lichtbild?
- Fehlt das Geburtsdatum?
- Fehlt der Geburtsort?
- Werden persönliche Pronomen verwendet (Ich, mein, meine)?
- Ist die Groß-/Kleinschreibung von Substantiven korrekt?
- Fehlt die Unterschrift am Ende?
- Sind Datumsformate inkonsistent?
- Ist die E-Mail-Adresse unprofessionell?
- Fehlen Pflichtabschnitte (Ausbildung, Berufserfahrung, Kenntnisse)?
- Ist die Reihenfolge der Abschnitte falsch?
- Steht die Grundschule im Lebenslauf?
- Sind Firmennamen oder Institutionen falsch geschrieben?
- Gibt es Rechtschreib- oder Grammatikfehler?

TIER 2 (Verbesserungen — empfohlen):
- Fehlt eine persönliche Kurzvorstellung?
- Sind Stichpunkte ohne Quantifizierung?
- Sind Sprachkenntnisse ohne CEFR-Niveau angegeben?
- Ist der Kenntnisse-Abschnitt unstrukturiert?
- Sind Praktika ohne Beschreibung aufgeführt?
- Ist die Motivation für den Zielberuf nicht erkennbar?

TIER 3 (strategisch — nur für menschliche Beratung):
- Karrierepositionierung und Zielklarheit
- Anschreiben-Strategie
- Interviewvorbereitung

Gib exakt diese JSON-Struktur zurück:
{{
  "overall_score": <Ganzzahl 1-10>,
  "tier_1": [
    {{"title": "<kurze Bezeichnung>", "detail": "<genaue Beschreibung>", "fix": "<konkrete Korrektur>"}}
  ],
  "tier_2": [
    {{"title": "<Bereich>", "detail": "<Verbesserungsvorschlag>"}}
  ],
  "tier_3": ["<Strategisches Thema>"],
  "summary": "<2-3 Sätze Gesamtbewertung>",
  "ready": <true wenn tier_1 leer, sonst false>
}}"""


EN_PROMPT = """You are an experienced career advisor at a university career service.
Analyse the CV below by going through EVERY criterion in the checklist.
Return ONLY a valid JSON object. No text before or after.

CV TEXT:
{cv_text}

CHECKLIST — go through every single point:

TIER 1 (critical errors — must fix before counseling):
- Is contact information complete (name, email, phone, location)?
- Is the email address professional?
- Are there spelling or grammar errors?
- Are date formats consistent throughout?
- Is a LinkedIn profile URL missing?
- Are there tables or columns that break ATS parsing?
- Are personal pronouns used in bullet points?
- Are any standard sections missing (Education, Experience, Skills)?
- Is a photo included (not standard for English CVs)?
- Is date of birth included (not appropriate for English CVs)?

TIER 2 (improvements — recommended):
- Do bullet points lack quantification?
- Is a professional summary missing?
- Are skills listed without proficiency levels?
- Are job descriptions too vague?
- Is the CV longer than 2 pages for a student?
- Are action verbs weak (responsible for, assisted with)?

TIER 3 (strategic — for human counselor only):
- Career narrative and positioning
- Cover letter strategy
- Interview preparation

Return exactly this JSON:
{{
  "overall_score": <integer 1-10>,
  "tier_1": [
    {{"title": "<short label>", "detail": "<precise description>", "fix": "<specific correction>"}}
  ],
  "tier_2": [
    {{"title": "<area>", "detail": "<improvement suggestion>"}}
  ],
  "tier_3": ["<strategic topic>"],
  "summary": "<2-3 sentence assessment>",
  "ready": <true if tier_1 empty, else false>
}}"""


def get_prompt(lang: str) -> str:
    return DE_PROMPT if lang == "de" else EN_PROMPT