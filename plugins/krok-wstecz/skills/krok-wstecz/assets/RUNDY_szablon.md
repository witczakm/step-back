# Dziennik rund — <projekt>

Jeden plik na projekt (domyślnie `docs/RUNDY.md`). Jedna sekcja na tor, czyli jeden krok lub problem,
nad którym idą kolejne rundy. Wiersz dopisuje prowadzący przy odbiorze rundy.

## Tor: <krótka nazwa toru>
Wytwór: <co krok produkuje; gdzie leżą rekordy, np. out/opisy/*.json>
Bramki: <nazwa>=<wyrocznia|wzorzec|model>; <nazwa>=<...>
Budżet: 2

| r | bramka | wynik | miara | rodzaj | notatka |
|---|---|---|---|---|---|
| 1 | <nazwa> | NO | 14 | K | <co zmieniono> |

Pola:
- **Bramki** — kto wydaje werdykt:
  - `wyrocznia` — test, uruchomienie, suma kontrolna, porównanie z bazą;
  - `wzorzec` — model albo reguła sprawdzona na zestawie zatwierdzonym przez człowieka, albo decyzja człowieka;
  - `model` — model bez wzorca.
- **wynik** — `PASS` albo `NO`. Każda bramka w danej rundzie to osobny wiersz z tym samym `r`.
- **miara** — liczba problemów znalezionych przez bramkę w tej rundzie (mniej = lepiej). Pierwsza liczba w komórce. Licz zawsze w tej samej jednostce co poprzednie rundy tej bramki — zmiana jednostki (np. z „wady na zrzutach” na „czerwone testy”) to nowa bramka, inaczej spadek miary jest pozorny.
- **rodzaj** — co zmieniono w tej rundzie:
  - `K` — kontrola (reguła, sędzia, strażnik, limit);
  - `W` — wytwór;
  - `P` — pomiar;
  - `U` — usunięcie;
  - `X` — decyzja po przeglądzie „krok-wstecz” (od tej rundy liczenie zaczyna się od nowa).
