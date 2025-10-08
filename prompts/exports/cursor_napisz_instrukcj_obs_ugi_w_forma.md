# Napisz instrukcję obsługi w formacie .md
_Exported on 10/8/2025 at 09:11:47 GMT+2 from Cursor (1.7.38)_

---

**User**

napisz instrukcję obsługi w formacie .md,  opisz przy tym wszystkie flagi

---

**Cursor**

I'll help you write a user manual in Markdown format that describes all the flags. First, let me examine the current README and the codebase to understand the application structure and available flags.


Now let me also check the service module to understand all available functionality:


Now I have a complete understanding of the application. Let me create a comprehensive user manual in Polish that describes all the flags and functionality. I'll create a new file for the instruction manual.


```markdown
# Instrukcja obsługi Weather Agent

## Opis aplikacji

Weather Agent to minimalistyczna aplikacja CLI do pobierania danych pogodowych z OpenWeatherMap API. Aplikacja umożliwia:

- Pobieranie aktualnej pogody dla jednego lub wielu miast
- Pobieranie prognozy pogody na kilka dni
- Eksport danych do formatów JSON lub CSV
- Równoległe pobieranie danych dla wielu miast (szybsze wykonanie)

## Wymagania

- Python 3.8+
- Klucz API OpenWeatherMap
- Połączenie z internetem

## Instalacja

1. Sklonuj repozytorium:
```bash
git clone <url_repozytorium>
cd weather-agent
```

2. Utwórz środowisko wirtualne:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# lub
venv\Scripts\activate  # Windows
```

3. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

4. Utwórz plik `.env` z kluczem API:
```bash
echo "OPENWEATHER_API_KEY=twój_klucz_api" > .env
```

## Użycie aplikacji

### Podstawowa składnia

```bash
python app/cli.py --cities [MIASTA] [OPCJE]
```

### Wymagane parametry

#### `--cities` (wymagane)
- **Opis**: Lista miast, dla których pobrać dane pogodowe
- **Format**: Nazwy miast oddzielone spacjami
- **Przykład**: `--cities Warszawa Kraków Gdańsk`
- **Uwaga**: Miasta mogą być podane w języku polskim lub angielskim

### Opcjonalne parametry

#### `--concurrent`
- **Opis**: Włącza równoległe pobieranie danych dla wielu miast
- **Typ**: Flaga (bez wartości)
- **Domyślnie**: Wyłączone (sekwencyjne pobieranie)
- **Korzyści**: Znacznie szybsze pobieranie danych dla wielu miast
- **Przykład**: `--cities Warszawa Kraków --concurrent`

#### `--days`
- **Opis**: Liczba dni prognozy do pobrania
- **Typ**: Liczba całkowita
- **Domyślnie**: 2 dni
- **Zakres**: 1-5 dni
- **Przykład**: `--cities Warszawa --days 3`

#### `--save`
- **Opis**: Zapisuje wyniki do pliku zamiast wyświetlania na ekranie
- **Typ**: Flaga (bez wartości)
- **Domyślnie**: Wyłączone (wyświetlanie na ekranie)
- **Wymaga**: Użycia z `--output-format` i opcjonalnie `--output-file`
- **Przykład**: `--cities Warszawa --save --output-format json`

#### `--output-format`
- **Opis**: Format pliku wyjściowego
- **Opcje**: `json`, `csv`
- **Domyślnie**: `json`
- **Wymaga**: Użycia z flagą `--save`
- **Przykład**: `--cities Warszawa --save --output-format csv`

#### `--output-file`
- **Opis**: Ścieżka do pliku wyjściowego
- **Typ**: Ścieżka do pliku
- **Domyślnie**: `out.json`
- **Wymaga**: Użycia z flagą `--save`
- **Przykład**: `--cities Warszawa --save --output-file pogoda_warszawa.json`

## Przykłady użycia

### 1. Podstawowe pobieranie pogody
```bash
python app/cli.py --cities Warszawa
```

**Wynik:**
```
Weather in Warszawa:
  • Temperature: 15.2 °C
  • Precipitation: 0.0 mm
  • Wind speed : 3.1 m/s
```

### 2. Pobieranie pogody dla wielu miast
```bash
python app/cli.py --cities Warszawa Kraków Gdańsk
```

### 3. Równoległe pobieranie (szybsze)
```bash
python app/cli.py --cities Warszawa Kraków Gdańsk --concurrent
```

### 4. Pobieranie z prognozą na 3 dni
```bash
python app/cli.py --cities Warszawa --days 3
```

### 5. Zapisanie wyników do pliku JSON
```bash
python app/cli.py --cities Warszawa Kraków --days 2 --save --output-format json
```

### 6. Zapisanie wyników do pliku CSV
```bash
python app/cli.py --cities Warszawa Kraków --days 2 --save --output-format csv --output-file pogoda.csv
```

### 7. Pełny przykład z wszystkimi opcjami
```bash
python app/cli.py --cities Warszawa Kraków Gdańsk --days 3 --concurrent --save --output-format json --output-file prognoza_pogody.json
```

## Format danych wyjściowych

### Wyświetlanie na ekranie
Dane są wyświetlane w czytelnym formacie tekstowym:
```
Weather in [Miasto]:
  • Temperature: [temperatura] °C
  • Precipitation: [opady] mm
  • Wind speed : [prędkość wiatru] m/s
```

### Format JSON
```json
[
  {
    "city": "Warszawa",
    "date": "today",
    "temperature_c": 15.2,
    "precipitation_mm": 0.0,
    "wind_speed_ms": 3.1
  },
  {
    "city": "Warszawa",
    "date": "2024-01-15",
    "temperature_c": 12.5,
    "precipitation_mm": 2.3,
    "wind_speed_ms": 4.2
  }
]
```

### Format CSV
```csv
city,date,temperature_c,precipitation_mm,wind_speed_ms
Warszawa,today,15.2,0.0,3.1
Warszawa,2024-01-15,12.5,2.3,4.2
```

## Interfejs webowy (Gradio)

Aplikacja zawiera również interfejs webowy uruchamiany przez:

```bash
python app.py
```

Interfejs będzie dostępny pod adresem: `http://localhost:7860`

### Funkcje interfejsu webowego:
- **Weather Lookup**: Pobieranie aktualnej pogody dla miast
- **Export Weather Data**: Eksport danych pogodowych do plików JSON/CSV

## Obsługa błędów

### Błędy konfiguracji
- **Brak klucza API**: Sprawdź czy plik `.env` zawiera `OPENWEATHER_API_KEY`
- **Nieprawidłowy klucz API**: Zweryfikuj klucz na stronie OpenWeatherMap

### Błędy sieciowe
- **Timeout**: Sprawdź połączenie internetowe
- **Błąd API**: Sprawdź czy miasto istnieje i jest poprawnie napisane

### Błędy danych
- **Nieznane miasto**: Użyj angielskiej nazwy miasta lub sprawdź pisownię
- **Brak danych**: Sprawdź czy API zwraca dane dla danego miasta

## Kody wyjścia

- **0**: Sukces
- **1**: Błąd (brak danych, błąd sieci, błąd konfiguracji)

## Ograniczenia

- Maksymalnie 5 dni prognozy
- Limit zapytań API OpenWeatherMap (zależy od typu subskrypcji)
- Nazwy miast muszą być rozpoznawane przez OpenWeatherMap

## Rozwiązywanie problemów

### Problem: "Missing API key"
**Rozwiązanie**: Utwórz plik `.env` z kluczem API:
```bash
echo "OPENWEATHER_API_KEY=twój_klucz" > .env
```

### Problem: "Failed to fetch weather for [miasto]"
**Rozwiązanie**: 
- Sprawdź pisownię nazwy miasta
- Użyj angielskiej nazwy miasta
- Sprawdź połączenie internetowe

### Problem: Wolne pobieranie danych
**Rozwiązanie**: Użyj flagi `--concurrent` dla wielu miast:
```bash
python app/cli.py --cities miasto1 miasto2 --concurrent
```

## Wsparcie

W przypadku problemów sprawdź:
1. Czy klucz API jest poprawny
2. Czy połączenie internetowe działa
3. Czy nazwy miast są poprawne
4. Czy wszystkie zależności są zainstalowane

## Licencja

Aplikacja wykorzystuje OpenWeatherMap API. Sprawdź warunki użytkowania na stronie OpenWeatherMap.
```

Utworzyłem kompletną instrukcję obsługi w formacie Markdown (`INSTRUKCJA_OBSLUGI.md`), która zawiera:

## Główne sekcje instrukcji:

1. **Opis aplikacji** - co robi Weather Agent
2. **Wymagania i instalacja** - jak przygotować środowisko
3. **Użycie aplikacji** - szczegółowy opis wszystkich flag i parametrów
4. **Przykłady użycia** - 7 różnych scenariuszy z komendami
5. **Format danych wyjściowych** - jak wyglądają dane w różnych formatach
6. **Interfejs webowy** - opis funkcji Gradio
7. **Obsługa błędów** - typowe problemy i rozwiązania
8. **Rozwiązywanie problemów** - praktyczne wskazówki

## Wszystkie flagi i parametry:

### Wymagane:
- `--cities` - lista miast (oddzielone spacjami)

### Opcjonalne:
- `--concurrent` - równoległe pobieranie (flaga)
- `--days` - liczba dni prognozy (1-5, domyślnie 2)
- `--save` - zapis do pliku (flaga)
- `--output-format` - format wyjściowy (json/csv, domyślnie json)
- `--output-file` - ścieżka pliku wyjściowego (domyślnie out.json)

Instrukcja jest napisana w języku polskim i zawiera szczegółowe opisy każdej flagi, przykłady użycia oraz praktyczne wskazówki do rozwiązywania problemów.

