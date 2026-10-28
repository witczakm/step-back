# krok-wstecz (step-back)

[English](README.md) · **Polski**

> **Zamiast obejścia do obejścia.** Skill dla agentów AI (Claude Code, Codex, aplikacja Claude), który
> zauważa, że kolejne rundy poprawek kręcą się w kółko, i pyta, czy zawodzący krok w ogóle powinien istnieć.
>
> Gdy agent dokłada kolejnych sędziów, strażników, reguły i wyjątki do kroku, który ciągle zawodzi,
> `krok-wstecz` robi **przegląd ramy**: zamiast poprawiać krok po raz kolejny, kwestionuje sam krok.
> Patrzy na **to, co ten krok wytwarza** (jego faktyczny wynik, np. pliki, rekordy albo oceny)
> i rekomenduje zmianę tego wyniku albo usunięcie kroku.
>
> **Dla kogo:** dla każdego, kto prowadzi wielorundową pracę z agentami AI. **Wypróbuj w minutę:**
> [Szybki start](#szybki-start). Angielska wersja skilla: `step-back`.

[![Wersja](https://img.shields.io/badge/wersja-0.1.0-blue)](CHANGELOG.md)
[![Licencja](https://img.shields.io/badge/licencja-MIT-green)](LICENSE)
[![Platformy](https://img.shields.io/badge/platformy-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20aplikacja%20Claude-orange)](#instalacja)
[![Format](https://img.shields.io/badge/format-Agent%20Skills-blueviolet)](https://agentskills.io)
[![Status](https://img.shields.io/badge/status-eksperymentalny-lightgrey)](EVALS.md)
[![test](https://github.com/witczakm/step-back/actions/workflows/test.yml/badge.svg)](.github/workflows/test.yml)

<details>
<summary><b>Spis treści</b></summary>

- [Jaką pętlę przerywa](#jaką-pętlę-przerywa)
- [Szybki start](#szybki-start)
- [Przykład z życia](#przykład-z-życia)
- [Jak to działa](#jak-to-działa)
- [Czy to dla ciebie?](#czy-to-dla-ciebie)
- [Instalacja](#instalacja)
- [Dziennik rund](#dziennik-rund)
- [Jak wpleść to w pracę](#jak-wpleść-to-w-pracę)
- [Prywatność i bezpieczeństwo](#prywatność-i-bezpieczeństwo)
- [Ograniczenia](#ograniczenia)
- [Dowody](#dowody)
- [Inspiracje i podziękowania](#inspiracje-i-podziękowania)
- [Współpraca i licencja](#współpraca-i-licencja)

</details>

---

## Jaką pętlę przerywa

```
runda 1   sędzia mówi NO             →  dodaj regułę
runda 2   sędzia mówi NO             →  dodaj wyjątek od reguły
runda 3   przegląd znajduje dziurę   →  dodaj drugiego sędziego do głosowania
runda 4   sędziowie się nie zgadzają →  dodaj regułę rozstrzygającą
   …      każda runda z osobna ma sens; razem nigdy się nie zbiegają
```

Wszyscy w pętli (wykonawca, recenzent, prowadzący) patrzą na najnowszą wersję mechanizmu kontroli
i pytają *„czy działa?”*. Nikt nie pyta *„czy powinien istnieć?”* ani *„co ten krok naprawdę
wytwarza?”*. `krok-wstecz` obsadza to puste miejsce.

Skill powstał po jednym dniu pracy, w którym w prawdziwym projekcie z agentami AI zdarzyły się trzy
takie pętle (9, 36 i 10 rund). Żadnej nie zamknął lepszy kontroler. Pierwszą zamknęła decyzja
człowieka, która zawęziła, co uznajemy za prawdę. Drugą zamknęło usunięcie kroku. Trzecią
zamknęło skasowanie tego, czego pilnowano.

## Szybki start

W Claude Code:

```text
/plugin marketplace add witczakm/step-back
/plugin install krok-wstecz@step-back      # wersja polska
```

Utwórz w projekcie plik `docs/RUNDY.md`. Każdy *tor* (krok, nad którym idzie kilka rund) to osobna sekcja: trzy linie nagłówka i jeden wiersz na każdą rundę.
`Wytwór:` to to, co krok produkuje, `Bramki:` mówią, kto wydaje werdykt PASS/NO (tu: model), `Budżet:` to liczba rund, na którą się godzisz.

```markdown
## Tor: sprawdzanie dowodu
Wytwór: cytat z dokumentu źródłowego + ocena (rekordy: out/oceny.jsonl)
Bramki: sedzia=model
Budżet: 2
| r | bramka | wynik | miara | rodzaj | notatka |
|---|---|---|---|---|---|
| 1 | sedzia | NO | 14 | K | reguła liczebnika |
| 2 | sedzia | NO | 5  | K | reguła nazwy własnej |
```

Po każdej odebranej rundzie uruchom:

```text
/krok-wstecz:krok-wstecz
```

Najpierw, bez modelu, liczone są sygnały. Dla dziennika powyżej:

```text
ALARM     | sprawdzanie dowodu | rund: 2
          - A: bramka „sedzia” (model bez wzorca) mówi NO w rundach 1 i 2
```

Przy ALARM przegląd rusza w świeżym kontekście i zwraca kartę decyzji na jedną stronę: co krok
naprawdę wytwarza, pięć alternatyw, jedną rekomendację, linię netto („mechanizmów kontroli: 5 → 2”)
i pole na twoją decyzję ([pełna karta z prawdziwego przebiegu, po angielsku](docs/evidence/e2e-alarm-card.txt)).
Gdy rundy się zbiegają, dostajesz [jedną linię](docs/evidence/e2e-ok-oneliner.txt) i nic więcej.

## Przykład z życia

Importer działał co minutę. Żeby zgadzał się z wdrożoną wersją, skrypt wyjmował z repozytorium
**kopię importera dla każdej wersji**. Pewnego dnia kopia była niekompletna i przez dobę nic się nie
zaimportowało.

Potem przyszło dziesięć rund utwardzania *strażnika wokół kopii*: próbne ładowanie, lista zależności,
własna blokada (cztery rundy błędów samej blokady), własny limit czasu, obsługa procesów potomnych.
Każdy przegląd znajdował nowy przypadek brzegowy **w samym strażniku**. Testy przechodziły, NO
mówili tylko recenzenci-modele.

`krok-wstecz` podnosi alarm po drugiej z tych rund (sygnał A: bramka modelowa bez wzorca dwa razy
mówi NO). Zauważa, że wyrocznia daje PASS, i przechodzi drabinę od góry: **usuń krok**. Importer
staje się częścią instalacji aplikacji, a kopia, jej kontrole i jej blokada znikają. Liczba
mechanizmów kontroli spada z pięciu–sześciu do dwóch: blokady systemowej i alarmu „brak importu
od 3 godzin”.

## Jak to działa

```
BRIEF (przed rundą 1)          RAPORT Z RUNDY (wykonawca)           PRÓG
Wytwór: co krok produkuje      RUNDA n | bramka | PASS/NO |         signals.py (bez modelu):
Bramki: kto orzeka             liczba problemów | K/W/P/U           OK · UWAGA · ALARM · ESKALACJA
Budżet: 2 rundy                                                            │ ALARM
                                                                           ▼
                     /krok-wstecz — podagent w świeżym kontekście → karta na 1 stronę → decyduje człowiek
```

**1 · Sygnały się liczy, a nie wyczuwa.** Mały skrypt na samej bibliotece standardowej czyta dziennik:

| Sygnał | Kiedy | Dlaczego |
|---|---|---|
| **A** | bramka typu `model` (bez wzorca od człowieka) mówi NO w dwóch ostatnich rundach | kryterium przesuwa się razem z każdą poprawką, więc postępu nie da się zmierzyć |
| **B** | rund jest więcej niż budżet, bramka dalej mówi NO, a liczba problemów nie spadła | budżet wydany, zbieżności brak |

Jeśli w tym torze był już krok wstecz, nowy alarm zamienia się w **ESKALACJĘ**: decyduje człowiek,
a skill nie przegląda sam siebie w kółko. Projekt opiera się na jednej obserwacji: *aktywność to nie postęp*.
Z samej konstrukcji bezpiecznik liczący zmiany plików nie zadziałałby w żadnej z trzech pętli, bo każda
runda zmieniała pliki.

**2 · To, kto wydaje werdykt, rozstrzyga, czy potrzebny jest wzorzec.**

| Kto orzeka | Wzorzec od człowieka? | Wniosek |
|---|---|---|
| Wyrocznia: test, uruchomienie, suma kontrolna | nie | sprawdź tylko, czy wyrocznia testuje to, co zmieniono |
| Konwencja lub gust: opis, styl, nazwa | nie, i model-sprawdzający też nie | kontrola mechaniczna albo usunięcie kontrolera |
| Prawda merytoryczna: czy dowód dowodzi | tak, 20–60 przypadków, część zamrożona | do tego czasu trzeci stan „do decyzji człowieka”, a nie kolejna reguła |

Gdy wyrocznia daje PASS, a NO pochodzi od recenzenta-modelu, uwagi modelu **nie blokują**.

**3 · Przegląd działa w świeżym kontekście** (`context: fork`). Zna dziennik i prawdziwe zapisy, a nie
tok rozumowania sesji. Zaczyna od przeczytania 10–20 rzeczywistych rekordów wytworu. W jednej
z pierwotnych pętli przyczyną był zwykły błąd (partie o numerze powyżej 99 pomijane), widoczny
dopiero w zapisach.

**4 · Alternatywy powstają według drabiny, od góry:**

1. **Usuń krok**, ale najpierw ustal, po co powstał (płot Chestertona).
2. **Zmień to, co krok wytwarza:** pola zamiast prozy, pełne zdanie zamiast fragmentu.
3. **Przesuń kontrolę do źródła**, żeby wada nie mogła powstać (poka-yoke).
4. **Wprowadź trzeci stan zamiast wyroku:** „do decyzji człowieka”. Te decyzje stają się wzorcem.
5. **Lepszy kontroler** na samym końcu, z etykietą *„to nadal kontroler”*.

**5 · Jedna rekomendacja na jednej stronie.** Karta zawiera też metodę kontrolną (ta sama próbka,
druga metoda, jedna liczba), kryterium porażki po dwóch rundach oraz to, *co zmieniłoby
rekomendację*. Zewnętrzne modele są opcjonalne, w budżecie do 5 wywołań. Żaden model nie rozstrzyga,
co jest prawdą.

## Czy to dla ciebie?

✅ Prowadzisz wielorundową pracę z agentami AI: zlecasz, oni oddają, ktoś recenzuje.  
✅ Używasz modeli do oceniania lub sprawdzania innych modeli albo trzymasz strażników i walidatory wokół zawodnych kroków.  
✅ Złapałeś się na pisaniu „jeszcze jednego wyjątku” po raz trzeci.

❌ Zadania jednorazowe albo szybkie poprawki błędów z jasną przyczyną.  
❌ Rundy, które już się zbiegają. Skill powie to jedną linią i zakończy.  
❌ Chcesz automatycznej bramki blokującej merge. Ten skill z założenia tylko doradza.

## Instalacja

### Claude Code: plugin (zalecane)

```text
/plugin marketplace add witczakm/step-back
/plugin install krok-wstecz@step-back      # polski
/plugin install step-back@step-back        # angielski
```

Skille z pluginów mają przedrostek, więc komenda to `/krok-wstecz:krok-wstecz` (albo `/step-back:step-back`).

<details>
<summary><b>Claude Code i Codex: skrypt instalacyjny (bez sieci, z kopią zapasową istniejącej instalacji)</b></summary>

```bash
git clone https://github.com/witczakm/step-back.git
cd step-back
./install.sh --lang pl       # wersja polska (krok-wstecz) do ~/.claude/skills i ~/.codex/skills
./install.sh                 # wersja angielska (step-back)
./install.sh --dry-run       # tylko podgląd
```

Po takiej instalacji komenda to po prostu `/krok-wstecz` (albo `/step-back`). Wymaga `python3`.
</details>

<details>
<summary><b>Aplikacja Claude (web, desktop): paczka zip</b></summary>

Pobierz `dist/krok-wstecz-pl.zip` (albo `dist/step-back-en.zip`) i dodaj w Customize → Skills. W aplikacji nie ma rozwidlonego
kontekstu ani wstępnie wykonywanego polecenia: skill sam uruchamia skrypt i pracuje w głównej
rozmowie. Zobacz [Ograniczenia](#ograniczenia).
</details>

## Dziennik rund

Jeden plik Markdown na projekt: `docs/RUNDY.md` (polskie słowa kluczowe) albo `docs/ROUNDS.md`
(angielskie). Oba są akceptowane. Pełny szablon:
[`assets/RUNDY_szablon.md`](plugins/krok-wstecz/skills/krok-wstecz/assets/RUNDY_szablon.md).

| Pole | Wartości |
|---|---|
| `Bramki:` | `nazwa=wyrocznia` · `nazwa=wzorzec` · `nazwa=model` |
| `wynik` | `PASS` / `NO`. Każda bramka w rundzie to osobny wiersz. |
| `miara` | liczba problemów w tej rundzie (mniej = lepiej). Zawsze ta sama jednostka; nowa jednostka to nowa bramka. |
| `rodzaj` | `K` kontrola · `W` wytwór · `P` pomiar · `U` usunięcie · `X` decyzja po kroku wstecz |

## Jak wpleść to w pracę

Skill działa najlepiej w trzech miejscach, które i tak już masz. Gotowe linie są w katalogu
[`snippets/`](plugins/krok-wstecz/skills/krok-wstecz/snippets/):

- **Brief:** trzy linie toru plus wymagana ostatnia linia każdego raportu wykonawcy:
  `RUNDA n | bramka | PASS/NO | liczba problemów | K/W/P/U`.
- **Polecenia przeglądu:** dopisz pytanie *„czy ten mechanizm w ogóle powinien istnieć i co usunąć,
  żeby ta klasa błędów nie mogła powstać?”*.
- **Odbiór:** dopisz wiersz i uruchom `/krok-wstecz` (`/krok-wstecz:krok-wstecz` przy instalacji jako plugin). Przy ALARM działaj według karty, przy ESKALACJI
  decyduje człowiek.

## Prywatność i bezpieczeństwo

- `signals.py` korzysta tylko z biblioteki standardowej Pythona. **Bez sieci i bez telemetrii**,
  zawsze kończy się kodem 0.
- Przegląd czyta pliki w twoim repozytorium: dziennik i rekordy wskazane w linii `Wytwór:`. Nie trzymaj
  w nich sekretów.
- Inne rodziny modeli woła **tylko wtedy, gdy masz już takie narzędzie** (drugi CLI agenta albo skrypt
  konsensusu), w budżecie 5 wywołań i zgodnie z twoimi ustawieniami uprawnień. W przeciwnym razie karta mówi `DEGRADACJA: jedna rodzina modeli`.
  Nie kieruj go na nic, czego nie wysłałbyś do modelu w chmurze.
- Niczego nie blokuje, nie zmienia kodu i nie robi commitów. Wydaje kartę, a decydujesz ty.

## Ograniczenia

- **Mała baza dowodów.** Sygnały wyprowadzono z prawdziwych pętli jednego projektu. Przetestowano je
  na 12 przypadkach: 5 pętli, 5 torów zbieżnych i 2 wczesnych ostrzeżeniach, z czego część wymyślono
  dla pokrycia krawędzi. Progi (dwie rundy, budżet 2) to punkt wyjścia, a nie kalibracja.
- **Słabe samoczynne uruchamianie.** W testach wyzwalania skill uruchomił się sam dla 3 z 9 (polski) i 2 z 9
  (angielski) zapytań, w których powinien, i dla 0 z 9, w których nie powinien. Nie licz na to, że Claude sam go wybierze:
  uruchamiaj go sam przy odbiorze rundy albo dopisz snippet.
- **Zależy od dyscypliny dziennika.** Bez wierszy nie ma sygnałów, a bez miary nie ma sygnału B.
- **Typy bramek deklaruje człowiek.** Nazwanie bramki modelowej `wyrocznią` wycisza sygnał A.
- **Różnice między platformami.** `context: fork` i wstępnie wykonywane polecenia to funkcje Claude
  Code. W Codex i aplikacji Claude skill działa w głównym kontekście i sam uruchamia skrypt.
- Alternatyw z wielu rodzin modeli nie sprawdzono jeszcze w pełnym przebiegu. Wszystkie zapisane
  przebiegi korzystały z jednej rodziny modeli (DEGRADACJA).

## Dowody

Małe i jawne; szczegóły w [EVALS.md](EVALS.md).

| Sprawdzenie | Wynik | Jak to czytać |
|---|---|---|
| Test wsteczny sygnałów: 12 przypadków po polsku i angielsku, obie wersje | 50 / 50 | reguły wyprowadzone z tych samych przypadków, część wymyślona; ryzyko dopasowania |
| Ślepe przebiegi: 3 zadania, ze skillem i bez | 12 / 12 wobec 7 / 12 kryteriów | jeden przebieg na zadanie, ocena autora; jedno kryterium (format karty) z definicji sprzyja skillowi |
| Pełny przebieg przez zainstalowany plugin | tor zbieżny: jedna linia OK; pętla: ALARM i karta w dokładnym formacie | mechanika Claude Code działa |
| Samoczynne uruchamianie, 18 zapytań na język | trafienia 3 / 9 (PL), 2 / 9 (EN); fałszywe 0 / 9 | uruchamiaj sam, nie czekaj, aż ruszy |

Największa różnica wyszła przy strażniku kopii. Bez skilla agent zaproponował lepszą blokadę i więcej
testów, czyli kolejny kontroler. Ze skillem zaproponował usunięcie kopii, i właśnie to zamknęło
pierwotny przypadek.

## Inspiracje i podziękowania

Nie skopiowano kodu z żadnego z tych projektów. Idee, na których opiera się projekt:
- **System produkcyjny Toyoty:** 5 × dlaczego, *jidoka* (stop-the-line), *poka-yoke*;
- **pre-mortem** Gary'ego Kleina;
- **polityka budżetu błędów** z Google SRE: z góry ustal, co się dzieje po przekroczeniu budżetu;
- **strangler fig** Martina Fowlera: zastępuj zamiast łatać;
- **płot Chestertona**;
- **evals skills** Hamela Husaina i Shreyi Shankar: sprawdzaj sędziego na etykietach człowieka;
- [obra/superpowers](https://github.com/obra/superpowers) `systematic-debugging`: „≥ 3 nieudane poprawki → zakwestionuj architekturę”;
- bezpiecznik z [frankbria/ralph-claude-code](https://github.com/frankbria/ralph-claude-code), który nauczył, że zmiany plików to nie postęp;
- [lessdumb](https://github.com/enkhbold470/lessdumb): najpierw usuń, potem optymalizuj.

**Co tu jest nowego:** alarm liczony z tego, *kto wydaje werdykt* i *czy liczba problemów spada*,
na prostym dzienniku rund. Alternatywy powstają według drabiny, w której „lepszy kontroler” jest
ostatni. Przegląd prowadzi audytor w świeżym kontekście, który czyta prawdziwe zapisy, a wynikiem
jest karta na jedną stronę, na której decyduje człowiek. Zobacz
[THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

Powiązane: [konsylium](https://github.com/witczakm/konsylium) (konsylium wielu perspektyw do decyzji)
i [cykl-lifecycle](https://github.com/witczakm/cykl-lifecycle) (pamięć projektu między sesjami agenta).

## Współpraca i licencja

Zgłoszenia i pull requesty są mile widziane, zwłaszcza **prawdziwe pętle** (zanonimizowane dzienniki
rund), których sygnały nie łapią albo oznaczają błędnie. Zobacz [CONTRIBUTING.md](CONTRIBUTING.md).

[MIT](LICENSE) © 2026 Michał Witczak
