(Przykład poglądowy — liczby ilustracyjne, przypadek zanonimizowany.)

KROK WSTECZ — strażnik kopii programu — 2026-10-09 — po rundzie 2
Modele: DEGRADACJA: jedna rodzina modeli | wywołań: 0/5
Sygnały: ALARM — A: bramka „przeglad” (model bez wzorca) NO w rundach 1 i 2; wyrocznia „atrapa” PASS → uwagi modelu nie blokują
Co krok wytwarza (na podstawie 12 rekordów): przy każdej nowej wersji skrypt wyjmuje z repozytorium kopię kodu importera dla tego commitu. Raz kopia była niekompletna i automat nie zapisywał przez dobę. Wszystkie kolejne mechanizmy (próbne ładowanie, lista zależności, własna blokada, limit czasu) pilnują tej kopii.
Wspólny mianownik: wady wytworu 1 | kontrolera 6 | pomiaru 1 → problemem jest mechanizm pilnujący kopii, a nie importer.
Werdykt wydaje: prawda techniczna z wyrocznią (atrapa, 113/0) → wzorzec niepotrzebny; NO pochodzi z przeglądów modeli
Alternatywy:
| szczebel | propozycja | koszt | ryzyko |
| 1 usuń krok | nie wyjmować kopii per wersja; importer instalowany razem z aplikacją w jednym stałym katalogu | ok. 2 dni | poprawka importera wymaga wdrożenia aplikacji |
| 2 zmień wytwór | kopia jako spakowany, sprawdzony sumą artefakt z kompilacji | 3 dni | nadal dwa źródła prawdy |
| 3 kontrola u źródła | próbny import w skrypcie wdrożenia | 0,5 dnia | — (dodatek do 1) |
| 4 trzeci stan | uwagi przeglądu na listę do decyzji, bez nowej rundy | 0 | uwagi mogą czekać |
| 5 lepszy kontroler (to nadal kontroler) | blokada systemowa zamiast własnej | 0,5 dnia | przypadki brzegowe zostają |
REKOMENDACJA: szczebel 1 + 3 — usunąć kopię per wersja; próbny import w skrypcie wdrożenia; alarm ciszy po 3 h bez udanego importu.
Linia netto: mechanizmów kontroli 6 → 2 (blokada systemowa, alarm ciszy)
Pierwszy krok i miara: na gałęzi; 3 wdrożenia próbne z próbnym importem 3/3   Kryterium porażki po 2 rundach: próbny import nie przechodzi w 2 kolejnych wdrożeniach
Metoda kontrolna: ten sam zestaw 15 plików testowych przez stary i nowy automat; liczba różnic w bazie = 0
Atak adwersarza: „od razu kolejka zadań w bazie” — zostaje jako krok na później, gdy wzrośnie wolumen
Co by zmieniło rekomendację: wymóg poprawiania importera bez wdrażania całej aplikacji
Czego nie wiemy: czas migracji na prawdziwych danych
Decyzja człowieka: [ ] przyjmuję  [ ] inaczej: ______   → wiersz rodzaju X w dzienniku
