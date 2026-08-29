# Virtual Switch — funkcionális specifikáció

## 1. Cél

A `virtual_switch` integráció egy valós smart kapcsoló elérhetőségét és belső állapotát szimulálja. Egy config entry egy Device-ot, két switch entitást és egy select entitást hoz létre:

| Entitás | Szerep |
|---|---|
| `switch.<name>_main` | A szimulált smart kapcsoló. |
| `switch.<name>_internal` | Az eszköz tényleges, belső on/off állapota. |
| `select.<name>_status` | A Main elérhetőségét és jelentett állapotát szabályozza. |

## 2. Tárolt állapot

Két állapotérték tárolódik:

| Érték | Kezdőérték | Jelentés |
|---|---|---|
| `internal_state` | `False` | Az egyetlen on/off állapot-igazságforrás. |
| `status` | `online` | A szimulált eszköz kiválasztott státusza. |

Nincs külön `main_state`, `reported_state`, utoljára ismert állapot vagy szinkronizáló állapotgép.

## 3. Entitásviselkedés

### Main

- `online` státuszban az `is_on` közvetlenül `internal_state`.
- Az `available` és a nem-online `is_on` értékét a státuszdefiníció adja.
- `online` állapotban a Main kapcsolása módosítja az `internal_state` értékét.
- Más státuszban a Main parancsa nem módosítja az Internal állapotot.
- A Main nem tárol saját állapotot.

### Status

- Fix opciói: `online`, `unavailable`, `unknown`, `error`.
- Egyedi opciók formátuma: `<name>[:available][:is_on]`.
- Az egyedi alapérték `available=True`, `is_on=None`.
- A kiválasztás az `internal_state` értékét nem módosítja.
- A saját dashboard-kártya az opciókat dinamikus, rádiógombszerű gombokként jeleníti meg.

### Internal

- `is_on` közvetlenül `internal_state`.
- Mindig elérhető és vezérelhető.
- Kapcsolása online és offline állapotban is módosítja az `internal_state` értékét.

## 4. Állapottábla

| Státusz | `available` | Main `is_on` / HA-állapot |
|---|---:|---|
| `online` | `True` | `internal_state` → `on`/`off` |
| `unavailable` | `False` | `None` → `unavailable` |
| `unknown` | `True` | `None` → `unknown` |
| `error` | `True` | `None` → `unknown` |
| custom | konfigurált, alapból `True` | konfigurált, alapból `None` |

Minden művelet idempotens. Egy tényleges változás pontosan egy mentést és egy dispatcher-frissítést okoz; változatlan érték beállítása egyiket sem.

## 5. Perzisztencia

- Csak az `internal_state` és a `status` tárolódik config entrynként HA `Store`-ban.
- A régi boolean `online` tárolóérték betöltéskor `online`/`unavailable` státuszra migrálódik.
- Újraindítás után mindkét érték visszaáll.
- Hiányzó tároló esetén a kezdőértékek használatosak.
- Sérült vagy érvénytelen tároló esetén figyelmeztetés naplózandó és a kezdőértékek használatosak.
- Config entry törlésekor a saját Store törlendő.

## 6. UI és dashboard-kártya

- A config flow teljesen UI-alapú és a példány nevét kéri.
- Mindhárom entitás egy közös Device-hoz tartozik.
- A `custom:virtual-switch-card` megjelenik a grafikus kártyaválasztóban, YAML nélkül hozzáadható, és a grafikus szerkesztő a VirtualSwitch Main entitásaira szűr.
- Egy Main entity ID-ból automatikusan megtalálja az Internal és Status entitást.
- A státuszgombok a szabványos `select.select_option` műveletet hívják.
- A resource automatikusan, verzióparaméterrel regisztrálódik.

## 7. TimedSwitch együttműködés

- A TimedSwitch a Main entitást szabványos switch célként használhatja.
- A két integráció között nincs privát állapot- vagy controllerkapcsolat.

## 8. Elfogadási tesztek

| Teszt | Kezdőállapot | Művelet | Elvárás |
|---|---|---|---|
| T1 | online, Internal OFF | Internal ON | Main `on`, Internal `on` |
| T2 | online, Internal ON | Status unavailable | Main `unavailable`, Internal `on` |
| T3 | unavailable, Internal ON | Internal OFF | Main `unavailable`, Internal `off` |
| T4 | unavailable, Internal OFF | Internal ON | Main `unavailable`, Internal `on` |
| T5 | unavailable, Internal ON | Status online | Main elérhető és `on` |
| T6 | unavailable, Internal OFF | Status online | Main elérhető és `off` |
| T7 | online, Internal OFF | Main ON | Internal és Main `on` |
| T8 | unavailable, Internal OFF | Main ON service | Internal változatlan, Main `unavailable` |
| T9 | tetszőleges | azonos érték ismétlése | változatlan, nincs mentés/frissítési loop |
| T10 | error, Internal ON | mentés és újratöltés | error, Internal ON áll vissza |
