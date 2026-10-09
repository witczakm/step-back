# Do briefu dla wykonawcy (Claude Code / Codex)

## Na początku nowego toru — 3 linie (kopiuj też do docs/RUNDY.md)
Wytwór: <co krok ma produkować; 1 przykładowy rekord>
Bramki: <kto orzeka, czy jest dobrze: wyrocznia | wzorzec | model>   ← model bez wzorca: najpierw wzorzec albo trzeci stan
Budżet: 2 rundy na tę bramkę; po przekroczeniu — przegląd „krok-wstecz”, nie kolejna reguła

## Na końcu briefu — wymagana ostatnia linia raportu
Zakończ raport jedną linią na każdą bramkę:
RUNDA <n> | <bramka> | <PASS/NO> | <liczba problemów> | <K/W/P/U> | <co zmieniono, 1 zdanie>
Wynik bramki podaj z PEŁNEGO przebiegu, nie z części testów.

## Do każdego polecenia przeglądu (recenzent, inny model)
Oprócz „czy to jest poprawne?” odpowiedz: czy ten mechanizm w ogóle powinien istnieć?
Co trzeba by usunąć albo zmienić w tym, co krok wytwarza, żeby ta klasa błędów nie mogła powstać?
