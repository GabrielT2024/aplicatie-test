# aplicatie-test
aplicatie organizare santier
# Aplicatie gestionare sudori autorizati

Aceasta aplicatie ofera un API REST construit cu [FastAPI](https://fastapi.tiangolo.com/) pentru evidenta sudorilor si a autorizatiilor lor conform standardelor ASME Sectiunea IX si prescriptiilor ISCIR (CR9 si CR7).

## Functionalitati principale

- adaugare, listare, editare si stergere sudori autorizati;
- gestionarea autorizatiilor pentru fiecare sudor, inclusiv standardul aplicabil si domeniul de calificare;
- raportare autorizatii care expira intr-un interval configurabil;
- endpoint de sanatate pentru monitorizare.

## Configurare mediu

1. Creeaza si activeaza un mediu virtual Python 3.11 (recomandat):

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   ```

2. Instaleaza dependintele:

   ```bash
   pip install -r requirements.txt
   ```

## Rulare aplicatie

Baza de date implicita este un fisier SQLite `welding.db` creat in directorul proiectului.

Porneste serverul local cu:

```bash
uvicorn app.main:app --reload
```

Aplicatia va fi disponibila la http://127.0.0.1:8000, iar documentatia interactiva Swagger la http://127.0.0.1:8000/docs.

## Testare

Ruleaza testele automate (pytest) cu:

```bash
pytest
```

Testele folosesc o baza de date SQLite in memorie pentru a nu afecta datele reale.
