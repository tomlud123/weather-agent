# Weather Agent

Aplikacja do pobierania danych pogodowych z OpenWeatherMap API.

# Demo
https://huggingface.co/spaces/tomlud123/weather-provider

## Funkcje

- Pobieranie aktualnej pogody dla miast
- Prognoza pogody na kilka dni
- Eksport danych do JSON/CSV

## Instalacja

### Utwórz plik `.env` z kluczem API:
```bash
echo "OPENWEATHER_API_KEY=twój_klucz" > .env
```

## Używanie

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


## Porównanie kodu wygenerowanego 

Perplexity free (m1) vs gemini 2.5 pro (m2) vs chat gpt 5 thinking (m3). Użyty prompt dostępny jest w lokacji prompts/initial.txt, a wygenerowany kod w lokacji app/generated.

Czytelność i styl pisania:

* m1 - skrypt składa się z funkcji main() i jednej funkcji pomocniczej. Krótki (68 linii), przejrzysty kod, surowe minimum funkcjonalne ze stosownymi komentarzami. Placeholder na api key jest w kodzie.
* m2 - skrypt dłuższy (104 linie), rozbudowany o walidacje, komentarze i argumenty dla wiersza poleceń (CLI). Dużo komentarzy wewnątrz funkcji, przy logice.
* m3 - skrypt najdłuższy (160 linii), najobszerniejsze komentarze przy definicjach, bogaty error handling, zawiera aż 5 statementów try podczas gdy konkurencyjne skrypty po jednym. Dobry pod dalszą rozbudowę, od razu definiuje parsera dla CLI, stosuje najprecyzyjniejsze nazewnictwo.

Poprawność i efektywność:

* m1 - prototypowanie możliwe od razu po ręcznym wpisaniu api key w kod. Przed wdrożeniem wymagałby jeszcze dodania konfigurowalności wyboru miasta i ekstrakcji api key.
* m2 - czyta zmienną środowiskową i działa od razu poprawnie, ograniczony error handling. Najbujniejszy format zwracanej odpowiedzi. 
* m3 - czyta zmienną środowiskową i działa od razu poprawnie, bogaty error handling i ustrukturyzowane parsowanie komendy wejściowej.


Zgodność z dobrymi praktykami:

* m1 - zgodny z KISS, użyteczny do szybkiego prototypowania. Brak parametrów konfiguracyjnych, brak definicji sygnatury wartości zwracanej przez funkcję, api key w kodzie przeczy dobrym praktykom i utrudnia dalszy rozwój.
* m2 - api key odwołuje się do zmiennej środowiskowej. Proste użycie requests z timeoutem, nadaje się na szybki proof-of-concept
* m3 - api key odwołuje się do słownika zawierającego zmienną środowiskową, oddzielna zmienna na timeouty. Rozwiązanie elastyczne, solidne dzięki walidacjom, najbardziej zgodne.


Wartość dodana:

* m1 - brak
* m2 - bez instrukcji wprost dodał argumenty CLI.
* m3 - bez instrukcji wprost dodał argumenty CLI oraz zaawansowaną obsługę edge-case’ów (wykazał się znajomością struktury błędów HTTP zwracanych przez OpenWeatherMap) i parametryzacją logiki.

## Podsumowanie

W tym wypadku najbardziej użyteczny kod wygenerował ChatGPT-5 Thinking. Był przygotowany profesjonalnie, z modularnością, czytelnym CLI i dobrymi praktykami. W części 1.2 kod ten zoptymalizowałem poprzez buforowanie wielu zapytań w ramach jednej sesji, opcjonalną asynchroniczność oraz modularne rozbicie kodu. Dodałem również funkcję poboru prognozowanych danych pogodowych na przyszłe dni dla wybranych lokalcji i zapisanie danych w pliku w formacie json lub csv. 

W części 1.2 zadania, współpraca z AI odbywała się głównie za pomocą IDE Cursor. Ograniczona była do wygenerowania asynchronicznego klienta HTTP i doradztwa w zakresie analizy kodu, brainstormingu, doboru narzędzi oraz pisania dokumentacji. Jednym z napotkanych problemów była duplikacja logiki i skomplikowana składnia kryjąca się za wygenerowanymi rozwiązaniami. Przykładowo, wskutek nie zdefiniowanego pierwotnie trybu wielu zapytań API dla jednego zapytania użytkownika końcowekgo, niepotrzebnie powstały oddzielne moduły dla pojedyńczych zapytań do serwera OWM (np. o pogodę w Warszawie teraz) i oddzielne dla zapytań złożonych w ramach jednego zapytania użytkownika (np. o pogodę w Warszawie i Paryżu w najbliższe 3 dni). Wskutek rewizji kodu, podjąłem decyzję o scaleniu obu funkcji i ujednolicenie opcji CLI. Innym problemem była nadgorliwość GenAI do generowania nowych funkcji jak np. logowanie poza konsolą. Podjętą decyzją było zdefiniowanie ograniczeń w promptach.

Eksport czatów ze współpracy z AI dostępny jest w lokacji prompts/exports.

### Wnioski
* ChatGPT 5 Thinking dostarczył kod bliższy standardom produkcyjnym niż Gemini 2.5 Pro oraz darmowa wersja Perplexity AI. Jego przewaga nie leżała w szybkości wygenerowania kodu, lecz w dojrzałości architektonicznej. Myślał "na wyrost" i wymagał najmniej fundamentalnych przeróbek.
* Cursor IDE przyspiesza refaktoryzację, ale trzeba pilnować zakresu. Sprawdza się też w brainstormingu i implementacji złożonych mechanizmów.
* ChatGPT 5, Gemini Pro i Cursor mają ograniczenia w wersji darmowej
