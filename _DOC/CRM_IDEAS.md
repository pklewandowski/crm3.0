
## WYSZUKIWANIE 
  - Możliwość zapisania filrtrów użytkownika

## DOKUMENTY 
### LISTA DOKUMENTÓW:
- Jak najeżdża się na status, to pokazuje się diagram przedstawiający ścieżkę pozytywną i w którym miejscu dokument obecnie jest
### PROCESSFLOW
- przy każdym przejściu procesu molżliwość zdefioniowania treści komunikatu 
- Powiązanie dokumentów - parent aby możliwe było tworzenie np. aneksów do umów
- 
## KALENDARZ
- pokazać wykres liczby zdarzeń po m-cu/dniu. Np. po kliknięciu w słupek m-ca pojawia się wykres dzienny.
- wyszarzyć godziny poza godzinami pracy rónież dla pól godzin oraz zmienić kolor czcionki na szary
- przy chowaniu panelu kalendarza miesięcznego i filtrów zwijać go do ikony, którą jak się kliknie, to panel się pojawi overlaped

## LISTY PRZEGLĄDANIA
### SORTOWANIE 
- po kliknięciu w przycisk kierunku sortowania wyskakuje okienko z literami alfabetu, żeby wybrać od której litery ma przesunąć.
Musi być posotrowane po danym polu, żeby można tak było to zrobić.

- Jeśli pole błędne i wpisano nową wartość, to usuwany błędny layout i ew. zaznaczenie, że zmieniono.
### GLOBALNE UNDO:
- Lista zmian dla wszystkich kontrolek formularza, z możliwością cofnięcia np:
```json
    {
        "id_xxx": ["val1", "val2", "val3", ...],
        "id_yyy": [number1, number2, ...]
    }
```
- lista tworzona (na kliencie oczywiście) podczas ładowania formularza, z wartościami inicjalnymi wszystkich pól.
- obsługa zdarzenia:
```js
        $(document).on('change', 'input, select, textarea', function() {
             // - wyszukanie w liście kontrolki
             // - dodanie wartości do listy, jeśli inna, niż ostatnio dodana
        });
```

## GLOBALNE WYŚRODKOWANIE formularzy i layoutu 
- jak coś mniejsze niż col-lg-12 to niech będzie na wyśrodkowane

## ZAŁĄCZNIKI
 - Podczas tworzenia zzipowanych załączników do downloadu powinien tworzyć podkatalogi zgodnie ze strukturą folderów

- Odsetki ustawowe
  - nowy produkt powinien przy tworzeniu przyjmować odsetki ustawowe. Procedura taka, jak podczas wprowadzania nowych zmian.
    dane do generowania z tabeli ProductInterestGlobal

- Przy dodawaniu / edycji użytkownika kliknięcie w rolę wyświetla listę uprawnień dla roli

- POLA STRUKTURALNE:
  -- pole nie dające się wypełnić bezpośrednio, ale, które po uzyskaniu focusu rozwija diva z polami "wewnętrznymi" - np. pole kompaktowego adresu - po rozwinięciu pola ulicy, nr domu, kod itp...

## WPROWADZANIE KLIENTA
  -- po wpisaniu NIP lub REGON sprawdzanie w CEiDG danych klienta i skopiowanie do odp. pól ----- ZROBIONE -----

## PRODUKT
### KALKULACJA
- przy tabeli kalkulacyjnej pokazać (np. ikona dwonka przy wierszu) zdarzenia, jakie występiły w danym dniu dla danego produktu. 
Po najechaniu myszką na ikonkę pokazuje listę szczegółów zdarzenia (np. kwota wpłaty, koszt itp)
  
### TABELA KALKULACYJNA
    - Poprawić, żeby podświetlały się wszystkie cele w rzędzie podczas hoover-a

## KLIENCI
  - sprawdzanie w białej liście

## ATRYBUTY DOKUMENTU
* Możliwość utworzenia struktury na podstawie pliku Excela
* Jeśli podczas tworzenia layoutu nie wiadomo, gdzie ma się pole znaleźć, można je przenieść do "poczekalni" - osobny div gdzie pole może czekać, aż
zostanie przygotowane dla niego miejsce
   
### WARUNKI
* Dodać funkcjonalność definiowana z aplikacji kontroli, czy warunki spełnione
podanie, które pola odpowiadają za warunki i przypodrządkowanie do nich akcji
      
### LABELKI PÓL
* jeśli tekst nie mieści się (ellipsis) i jeśli atrybut nie ma wypełnionej właściwości "description":
pokazać pełną treść labelki w tooltpip-ie po najechaniu na labelkę
skorzystać z jqureryExt: frontend\_core\jqueryExt\jqueryExt.js, $(label).is(":truncated")
Jeśli jest "description", to pokazać oczywiście tekst z "description"
         
## MAILING
* wysyłanie maili wprost z CRM
* historia maili do klientów / userów
* wysyłanie maili z załącznikami z poziomu załączników
* wysyłanie maili z pismami wychodzącymi

## PLIKI
* Zrobić globalne repozytorium plików dla wszystkich aplikacji

## AKTUALIZACJA DANYCH GLOBALNYCH
* System odpytuje serwer o stan zmiennych globalnych, jak np. __odsetki ustawowe, odsetki za opóźnienie__ itp.
* jeśli jest zmiana, to dla danego typu danych uruchamiane są odpowiednie funkcje ustawiające, wscześniej zdefiniowane