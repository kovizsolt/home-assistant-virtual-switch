# Virtual Switch — specifikáció

## 1. Cél

A `virtual_switch` Home Assistant custom integration egy egyszerű virtuális eszközt
szimulál. Egy config entry pontosan három kapcsolót hoz létre:

| Entitás | Szerep |
|---|---|
| `switch.<name>_main` | A Home Assistant által ismert, utoljára jelentett eszközállapot és normál vezérlőkapcsoló. |
| `switch.<name>_internal` | A szimulált eszköz tényleges belső állapota; fizikai, HA-n kívüli állapotváltozás szimulálására használható. |
| `switch.<name>_online` | Meghatározza, hogy az eszköz belső állapotváltozásai eljutnak-e a főkapcsolóhoz. |

Mindhárom entitás ugyanahhoz a Home Assistant Device-hoz tartozik.

### 1.1 Dashboard-kártya

Az integráció saját `custom:virtual-switch-card` dashboard-kártyát szállít, amely egy
Virtual Switch config entry három kapcsolóját egyetlen vizuális egységben jeleníti meg.

- A kártya megjelenik a Home Assistant grafikus kártyaválasztójában
  (`window.customCards`).
- A kártya teljesen UI-ból, YAML szerkesztése nélkül hozzáadható.
- A grafikus konfigurációs űrlap egy `switch.<name>_main` entitás kiválasztását kéri, és
  kizárólag a `virtual_switch` integráció főkapcsolóira szűr.
- Entitásalapú kártyaajánlásnál minden `switch.<name>_main` felajánlja a teljes Virtual
  Switch Cardot.
- A `switch.<name>_internal` és `switch.<name>_online` entitást a kártya a dokumentált
  szuffixumok alapján automatikusan azonosítja; ezeket nem kell külön konfigurálni.
- A kártya a HA szabványos switch service call-jait használja, és nem tartalmaz saját
  állapotlogikát.
- Hiányzó vagy letiltott másodlagos entitás nem omlaszthatja össze a kártyát; a megmaradt
  vezérlők továbbra is használhatók.
- A kártya mobil és asztali nézetben is reszponzív, vízszintes görgetés nélkül használható.
- A frontend JavaScript resource-ot az integráció automatikusan regisztrálja és
  verzióparaméterrel frissíti; kézi fájlmásolás vagy resource-bejegyzés nem szükséges.

## 2. Rögzített szótár

### 2.1 Állapotok

Az elérhetőségi állapotgép állapotai:

| Állapot | Jelentés | Kezdőállapot |
|---|---|---|
| `ONLINE` | A belső állapot változásai azonnal megjelennek a főkapcsolón. | igen |
| `OFFLINE` | A belső állapot változásai nem módosítják a főkapcsoló HA-ban látható állapotát. | nem |

Tárolt logikai értékek:

| Érték | Jelentés | Kezdőérték |
|---|---|---|
| `internal_state` | A szimulált eszköz tényleges, belső állapota. | `False` (KI) |
| `reported_state` | A Home Assistantnak utoljára jelentett állapot. Ezt mutatja a főkapcsoló. | `False` (KI) |

### 2.2 Események

| Esemény | Forrás |
|---|---|
| `main_on` | A főkapcsoló bekapcsolása. |
| `main_off` | A főkapcsoló kikapcsolása. |
| `internal_on` | A belső kapcsoló bekapcsolása. |
| `internal_off` | A belső kapcsoló kikapcsolása. |
| `go_online` | Az online kapcsoló bekapcsolása. |
| `go_offline` | Az online kapcsoló kikapcsolása. |

## 3. Átmeneti tábla

Minden `(állapot × esemény)` pár szerepel a táblában.

| Aktuális állapot | Esemény | Következő állapot | Akció |
|---|---|---|---|
| `ONLINE` | `main_on` | `ONLINE` | `internal_state=True`, `reported_state=True` |
| `ONLINE` | `main_off` | `ONLINE` | `internal_state=False`, `reported_state=False` |
| `ONLINE` | `internal_on` | `ONLINE` | `internal_state=True`, `reported_state=True` |
| `ONLINE` | `internal_off` | `ONLINE` | `internal_state=False`, `reported_state=False` |
| `ONLINE` | `go_online` | `ONLINE` | Idempotens szinkron: `reported_state=internal_state` |
| `ONLINE` | `go_offline` | `OFFLINE` | Nincs állapot-szinkronizálás |
| `OFFLINE` | `main_on` | `OFFLINE` | `internal_state=True`; `reported_state` változatlan |
| `OFFLINE` | `main_off` | `OFFLINE` | `internal_state=False`; `reported_state` változatlan |
| `OFFLINE` | `internal_on` | `OFFLINE` | `internal_state=True`; `reported_state` változatlan |
| `OFFLINE` | `internal_off` | `OFFLINE` | `internal_state=False`; `reported_state` változatlan |
| `OFFLINE` | `go_online` | `ONLINE` | `reported_state=internal_state` |
| `OFFLINE` | `go_offline` | `OFFLINE` | Nincs művelet |

## 4. Peremfeltételek

- A főkapcsoló offline állapotban is elérhető és vezérelhető marad. Nem kap HA
  `unavailable` állapotot, mert az megakadályozná a kapcsolását.
- Offline állapotban a főkapcsolóra küldött parancs módosítja az `internal_state` értékét,
  de a kapcsoló HA-ban publikált `reported_state` értéke változatlan marad. A felület ezért
  a következő állapotfrissítéskor visszaáll az utoljára jelentett állapotra.
- A belső kapcsoló mindig az `internal_state` értéket mutatja. Ennek változása szándékosan
  látható a HA-ban; kizárólag a főkapcsolóra történő továbbítás marad rejtett offline módban.
- Online-ra váltáskor a szinkronizálás azonnali és a belső állapot az igazság forrása.
- Az azonos értékre történő ismételt kapcsolás idempotens.
- A config entry újratöltése és a HA újraindítása után mindhárom állapot a perzisztens
  tárolóból áll vissza. Első indításkor: `ONLINE`, belső KI, főkapcsoló KI.
- Ha a mentett állapot sérült vagy hiányos, az első indítás alapértékei használatosak,
  és a hiba figyelmeztetésként naplózandó.
- Ismeretlen esemény figyelmeztetésként naplózandó; állapotot nem változtathat és nem
  dobhat kivételt.
- Minden elérhetőségi átmenet naplózandó: régi állapot, új állapot, esemény és időbélyeg.

## 5. Elfogadási tesztek

| Teszt | Kezdőhelyzet | Események | Várt eredmény |
|---|---|---|---|
| T1 | ONLINE, belső KI, jelentett KI | `internal_on` | ONLINE, belső BE, jelentett BE |
| T2 | ONLINE, belső KI, jelentett KI | `go_offline`, `internal_on` | OFFLINE, belső BE, jelentett KI |
| T3 | T2 végállapota | `go_online` | ONLINE, belső BE, jelentett BE |
| T4 | ONLINE, belső BE, jelentett BE | `go_offline`, `internal_off` | OFFLINE, belső KI, jelentett BE |
| T5 | T4 végállapota | `go_online` | ONLINE, belső KI, jelentett KI |
| T6 | OFFLINE, belső KI, jelentett KI | `main_on` | OFFLINE, belső BE, jelentett KI |
| T7 | OFFLINE, belső BE, jelentett BE | `main_off` | OFFLINE, belső KI, jelentett BE |
| T8 | ONLINE, belső KI, jelentett KI | `main_on` | ONLINE, belső BE, jelentett BE |
| T9 | ONLINE, belső BE, jelentett BE | `main_off` | ONLINE, belső KI, jelentett KI |
| T10 | OFFLINE, belső BE, jelentett KI | `go_offline` | Minden érték változatlan |
| T11 | ONLINE, belső BE, jelentett BE | `go_online` | Minden érték változatlan |
| T12 | tetszőleges | ismeretlen esemény | Minden érték változatlan, figyelmeztetés naplózva |
| T13 | OFFLINE, belső BE, jelentett KI | mentés és visszatöltés | OFFLINE, belső BE, jelentett KI |

### 5.1 UI- és dashboard-elfogadási tesztek

| Teszt | Művelet | Várt eredmény |
|---|---|---|
| UI1 | A felhasználó a Beállítások → Integrációk felületen hozzáad egy Virtual Switch példányt | A config flow csak a nevet kéri, majd létrejön egy Device a három kapcsolóval. |
| UI2 | A felhasználó megnyitja a dashboard grafikus kártyaválasztóját | A `Virtual Switch Card` kiválasztható, YAML írása nélkül. |
| UI3 | A kártya grafikus szerkesztője megnyílik | Csak a `virtual_switch` integráció `*_main` kapcsolói választhatók. |
| UI4 | A felhasználó egy `switch.<name>_main` entitásból indítja a kártya hozzáadását | A teljes Virtual Switch Card ajánlásként megjelenik. |
| UI5 | A kártyát csak az `entity: switch.<name>_main` konfigurációval betöltik | Automatikusan megjelenik a hozzá tartozó `main`, `internal` és `online` kapcsoló. |
| UI6 | A kártyán bármely kapcsolót átváltják | A megfelelő szabványos HA service call fut, és a SPEC 3. szakaszának átmenete érvényesül. |
| UI7 | Az `internal` vagy `online` entitás hiányzik vagy letiltott | A kártya működő része használható marad, JavaScript-hiba nélkül. |
| UI8 | Az integráció frissen települ vagy frissül | A kártya resource automatikusan elérhető és az új verzió töltődik be. |
| UI9 | A dashboard keskeny mobilnézetre vált | Mindhárom vezérlő ugyanazon kártyán, vízszintes görgetés nélkül használható. |

## 6. Implementációs korlátok

- Az állapotgép táblavezérelt; az átmenetek nem szétszórt `if/elif` láncokban élnek.
- Az állapot config entrynként, Home Assistant `Store` használatával perzisztens.
- Az entitások fix, dokumentált entity ID-t és stabil unique ID-t kapnak.
- Az entitások dispatcher-alapú frissítést használnak, polling nélkül.
- A config flow egy kötelező nevet kér; további működési beállítás nincs.
- A saját dashboard-kártya automatikusan regisztrált resource, grafikus config form és
  entitásalapú kártyaajánlás használatával teljesen UI-vezérelt.

## 7. Együttműködés a Timed Switch integrációval

- A `switch.<name>_main` szabványos Home Assistant `switch` entitás, ezért külső
  integráció — különösen a `timed_switch` — célentitásként használhatja.
- A Timed Switch egy meglévő Virtual Switch `main` entitását kiválaszthatja, vagy a saját
  config flow-jából elindíthatja egy új Virtual Switch létrehozását.
- A programból indított létrehozás is a Virtual Switch saját config flow-ját és ugyanazt
  a validációt használja, mint a Beállítások → Integrációk felületéről indított folyamat.
- A Virtual Switch önálló config entry és Device marad; a Timed Switch nem kap
  tulajdonjogot fölötte, és saját törlésekor nem törölheti azt.
- Az együttműködés nem igényel Virtual Switch-specifikus állapotlogikát a TimedSwitchben:
  a `main` kapcsoló vezérlése és figyelése kizárólag szabványos HA service callokkal és
  state change eseményekkel történik.
- Offline Virtual Switch esetén a Timed Switch csak a `main` utoljára jelentett állapotát
  látja. Az `internal` rejtett változásáról csak a Virtual Switch online-ra állásakor kap
  állapotváltozást; ez a szimuláció szándékos része.

### 7.1 Integrációs elfogadási tesztek

| Teszt | Művelet | Várt eredmény |
|---|---|---|
| I1 | A Timed Switch egy meglévő Virtual Switch `main` entitását kapcsolja | A parancs ugyanúgy működik, mint bármely szabványos switch célon. |
| I2 | A Timed Switch config flow új Virtual Switch létrehozását indítja | A Virtual Switch saját config flow-ja fut le, és önálló entry/Device jön létre. |
| I3 | A Virtual Switch OFFLINE, a Timed Switch kapcsolási parancsot küld a `main` entitásra | Az `internal_state` módosul, a `reported_state` változatlan; a Timed Switch nem kap hamis visszajelzést. |
| I4 | Az I3 után a Virtual Switch ONLINE-ra vált | A `main` publikálja az aktuális belső állapotot, amit a Timed Switch normál külső state change-ként észlel. |
| I5 | A kapcsolódó Timed Switch entryt törlik | A Virtual Switch entry, Device és állapot változatlanul megmarad. |
