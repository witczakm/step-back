---
name: krok-wstecz
description: Użyj, gdy poprawki kręcą się w kółko — kolejna runda dopisuje następny wyjątek, if, regułę, limit, retry, blokadę albo drugiego sędziego, a ta sama recenzja lub test znowu mówi NO; gdy liczba odrzuceń nie spada albo rośnie; gdy model ocenia lub sprawdza wynik innego modelu bez etykiet od człowieka; gdy przegląd znajduje nowe dziury w samym mechanizmie kontroli (strażnik, walidator, watchdog); gdy signals.py zgłasza ALARM; albo gdy pada „krok wstecz”, „kręcimy się w kółko”, „obejście do obejścia”, „wyjątek od wyjątku”, „może cała droga jest zła”, „spójrz na to z boku”. Robi przegląd ramy w świeżym kontekście — zamiast dokładać kolejny kontroler patrzy, co krok naprawdę wytwarza, i proponuje usunąć krok albo zmienić jego wytwór; zwraca jedną rekomendację na karcie decyzji. Uruchom, zanim zlecisz kolejną rundę poprawek tego samego. NIE używaj przy pierwszej porażce, gdy rundy się zbiegają (błędów coraz mniej), przy jednorazowym błędzie z jasną przyczyną, zwykłym bugfixie, code review ani planowaniu refaktoru.
argument-hint: "[tor] [ścieżka-dziennika]"
context: fork
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/signals.py *)
---

# Krok wstecz — przegląd ramy na progu

Pracujesz jako **audytor ramy** w świeżym kontekście. Nie znasz toku rozumowania sesji i to jest
celowe: pętle „obejście do obejścia” biorą się stąd, że wszyscy uczestnicy patrzą na najnowszą
wersję mechanizmu i pytają „czy działa?”, a nikt nie pyta „czy powinien istnieć?”. Twoje wejście to
**historia rund i prawdziwe zapisy wytworu**, nie streszczenie wykonawcy. Twoje wyjście to jedna karta
decyzji na najwyżej jedną stronę. Decyduje człowiek.

## Sygnały policzone przed startem

!`python3 ${CLAUDE_SKILL_DIR}/scripts/signals.py --lang pl`

Argumenty wywołania: `$ARGUMENTS`. Jeśli wskazują inny plik dziennika albo tor, uruchom ponownie
`python3 ${CLAUDE_SKILL_DIR}/scripts/signals.py <ścieżka> --tor <nazwa> --lang pl`.
W agentach, które nie wykonują powyższej linii z wyprzedzeniem (widzisz polecenie zamiast wyniku),
uruchom je sam z katalogu głównego projektu.

Jak czytać wynik:
- **OK** — powiedz to w jednym zdaniu i zakończ. Rundy zbliżają się do celu; przegląd byłby
  kolejnym kontrolerem. Wyjątek: wywołanie na żądanie z podanym powodem — wtedy wersja skrócona
  (kroki 1, 3 i 4).
- **UWAGA** — zwróć listę uwag i jedno zdanie, co dopisać (kontrakt toru, wzorzec albo trzeci stan).
  Pełnej procedury nie prowadź.
- **ALARM** — pełna procedura poniżej.
- **ESKALACJA** — krok wstecz już był w tym torze i nie pomógł. Nie rób drugiego przeglądu. Zwróć
  krótkie zestawienie dla człowieka: co zmieniono w poprzednim kroku wstecz, jaka była miara przed i po,
  oraz dwie możliwości do jego decyzji. Skill podlega tej samej regule stopu co reszta pracy.
- **BRAK DZIENNIKA** — odtwórz rundy z dostępnych zapisów (dziennik sesji, commity, raporty
  przeglądów) w formacie z `assets/RUNDY_szablon.md`, oznacz jako **odtworzony, niepewny**, pola
  nieustalone wpisz jako „DO UZUPEŁNIENIA” i policz sygnały na odtworzonym pliku. Bez miary sygnału B
  nie ma — napisz to wprost.

## Procedura (przy ALARM)

### 1. Odtwórz, co krok naprawdę wytwarza
Przeczytaj 10–20 **prawdziwych rekordów** wytworu (pliki, wiersze bazy, wyniki, logi) — lokalizację
wskazuje linia „Wytwór:” w dzienniku albo repozytorium. Opisz wytwór w trzech zdaniach.
Powód: zwykły błąd (np. pomijane partie powyżej pewnego numeru) bywa widoczny dopiero w zapisach,
a nie w raportach z rund. Jeśli rekordów nie da się odczytać, napisz to w karcie — to osłabia całą
rekomendację.

### 2. Nazwij wspólny mianownik wad
Pogrupuj wady z ostatnich rund na trzy kosze: **wytwór** (to, co krok produkuje), **kontroler**
(sędzia, strażnik, reguła, limit) i **pomiar** (skrypt próby, próbka, metoda liczenia). Policz.
Jeśli większość wad leży w kontrolerze albo pomiarze, problemem jest mechanizm kontroli, nie wytwór.

### 3. Ustal, kto wydaje werdykt i czy potrzebny jest wzorzec
| Kto rozstrzyga | Potrzebny wzorzec od człowieka? | Wniosek |
|---|---|---|
| Wyrocznia (test, uruchomienie, suma kontrolna) | nie | sprawdź tylko, czy wyrocznia naprawdę sprawdza to, co zmieniono |
| Konwencja lub gust (opis, styl, nazwa, długość) | nie — i model-sprawdzający też nie | kontrola mechaniczna albo usunięcie kontrolera |
| Prawda merytoryczna (czy dowód dowodzi) | tak — 20–60 przypadków zatwierdzonych przez człowieka, część zamrożona | bez wzorca: trzeci stan „do decyzji człowieka”, nie kolejna reguła |

Zapytaj też: **czy błędny werdykt w ogóle coś realnie kosztuje?** Jeśli nie — kontroler jest zbędny.
Gdy wyrocznia daje PASS, a NO pochodzi od modelu, uwagi modelu nie blokują: trafiają na listę do
decyzji człowieka.

### 4. Alternatywy — cztery punkty widzenia i drabina
Spójrz z czterech stron: **wytwór** (co produkuje krok), **usunięcie** (co gdyby kroku nie było),
**inna metoda** (ta sama próbka, niezależny sposób), **odbiorca** (kto czyta wytwór i czego naprawdę
potrzebuje). Potem wypisz alternatywy, zaczynając od góry drabiny — każdy szczebel rozważ jawnie:

1. **Usuń krok.** Zanim to zarekomendujesz, ustal, po co powstał (historia, wywołujący) — płot
   Chestertona. Często okazuje się, że dane już istnieją gdzie indziej.
2. **Zmień to, co krok produkuje** — kontrakt wyjścia: pola strukturalne zamiast prozy, pełne zdanie
   zamiast fragmentu, wskazanie elementu zamiast wyroku.
3. **Przesuń kontrolę do źródła** — tak, by wada nie mogła powstać (poka-yoke).
4. **Trzeci stan zamiast wyroku** — „do decyzji człowieka” z uzasadnieniem; decyzje budują wzorzec.
5. **Lepszy kontroler** — dopiero na końcu i z etykietą **„to nadal kontroler”**. Zamiana własnej
   blokady na blokadę systemową bywa słuszna, ale nie usuwa źródła problemu.

### 5. Ustal metodę kontrolną
Opisz, jak tę samą próbkę przepuścić **drugą, niezależną metodą** (inny model od zera bez widzenia
pierwszej oceny, reguła deterministyczna albo człowiek) i jaka jedna liczba z tego wyjdzie (odsetek
zgodności). Niezgodności idą do człowieka. Wykonanie należy do wykonawcy toru, nie do ciebie.

### 6. Jedna rekomendacja i atak na nią
Wybierz jedną alternatywę. Poddaj ją atakowi adwersarza innej rodziny modeli (sekcja niżej).
Dopisz: pierwszy krok mierzalny, **kryterium porażki po 2 rundach** i **co by zmieniło rekomendację**.

### 7. Karta
Zwróć kartę dokładnie w tym formacie jako ostatnią wiadomość — to jedyne, co wraca do
głównej sesji. Główna sesja dopisuje decyzję człowieka do dziennika jako wiersz rodzaju **X** i do
rejestru decyzji projektu. Lekcję zapisuje się tam, gdzie projekt trzyma wnioski — nie ty.

```
KROK WSTECZ — <tor> — <RRRR-MM-DD> — po rundzie <n>
Modele: <rodziny, które odpowiedziały; albo DEGRADACJA: jedna rodzina modeli> | wywołań: <k>/5
Sygnały: <wynik signals.py: powody A/B, uwagi>
Co krok wytwarza (na podstawie <liczba> rekordów): <3 zdania>
Wspólny mianownik: wady wytworu <a> | kontrolera <b> | pomiaru <c> → <wniosek w 1 zdaniu>
Werdykt wydaje: <wyrocznia | konwencja | prawda merytoryczna> → wzorzec: <niepotrzebny | jest | brak>
Alternatywy:
| szczebel | propozycja | koszt | ryzyko |
| 1 usuń krok | … | … | … |
| 2 zmień wytwór | … | … | … |
| 3 kontrola u źródła | … | … | … |
| 4 trzeci stan | … | … | … |
| 5 lepszy kontroler (to nadal kontroler) | … | … | … |
REKOMENDACJA: <szczebel n — 1–2 zdania>
Linia netto: mechanizmów kontroli <przed> → <po>
Pierwszy krok i miara: <…>   Kryterium porażki po 2 rundach: <…>
Metoda kontrolna: <ta sama próbka, druga metoda, jedna liczba>
Atak adwersarza: <najmocniejszy zarzut; co z niego zostaje>
Co by zmieniło rekomendację: <fakt lub warunek>
Czego nie wiemy: <…>
Decyzja człowieka: [ ] przyjmuję  [ ] inaczej: ______   → wiersz rodzaju X w dzienniku
```

Przykład wypełnionej karty: `examples/przyklad_karty.md`.

## Modele — stały schemat i budżet

Działasz w podagencie, więc nie uruchomisz kolejnych podagentów (panele person). Inne rodziny
modeli wołasz z powłoki, jeśli są dostępne:
1. narzędzie wielomodelowe, które użytkownik już ma (skrypt skilla konsensusu, pomocnik do
   OpenRoutera albo drugi CLI agenta, np. Codex lub Gemini) — najpierw sprawdź jego `--help`;
2. w przeciwnym razie przygotuj alternatywy sam i wpisz w nagłówku karty **„DEGRADACJA: jedna rodzina
   modeli”** — główna sesja może wtedy uruchomić przegląd z wielu perspektyw (np. skill `konsylium`).

| Czynność | Kto | Wywołania |
|---|---|---|
| sygnały | skrypt | 0 |
| odtworzenie dziennika (tylko gdy go brak) | tani model | 1 |
| rekordy, mianownik, werdykt | ty, z plików | 0 |
| alternatywy na ślepo | 3 różne rodziny | 3 |
| atak na rekomendację | 1 adwersarz innej rodziny niż autor rekomendacji | 1 |

**Budżet: najwyżej 5 wywołań zewnętrznych modeli na jedno użycie.** Gdy się skończy, zamknij kartę
na tym, co masz, i zapisz to w niej. **Żaden model nie rozstrzyga, co jest prawdą** — zgoda modeli to
sygnał, nie dowód; prawdę ustala wyrocznia albo wzorzec zatwierdzony przez człowieka.

## Czego ten skill nie robi

- Nie jest bramką i niczego nie blokuje — wydaje kartę.
- Nie dodaje reguł. Rekomendacja „dodaj regułę” bez rozważenia szczebli 1–4 jest błędem procedury.
- Nie zastępuje decyzji człowieka ani wzorca od człowieka.
- Nie powtarza się w kółko: najwyżej jedno użycie na tor, potem ESKALACJA do człowieka.

## Pliki

- `scripts/signals.py` — liczy sygnały; zawsze kod 0; dzienniki po polsku i angielsku.
- `assets/RUNDY_szablon.md` — format dziennika rund.
- `assets/brief_3_linie.md` — linie do briefu dla wykonawcy, linia raportu i pytanie do recenzenta.
- Szablon karty decyzji jest wpisany w kroku 7 powyżej.
- `examples/przyklad_karty.md` — przykład wypełnionej karty.
- `snippets/` — opcjonalne linie do `CLAUDE.md` i `AGENTS.md`.
