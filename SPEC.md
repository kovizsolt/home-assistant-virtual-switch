# Virtual Switch — funkcionális specifikáció

## 1. Cél

A `virtual_switch` integráció egy valós smart kapcsoló elérhetőségét és belső állapotát
szimulálja. Egy config entry egy Device-ot és pontosan három switch entitást hoz létre:

| Entitás | Szerep |
|---|---|
| `switch.<name>_main` | A szimulált smart kapcsoló. |
| `switch.<name>_online` | A Main elérhetőségét szabályozza. |
| `switch.<name>_internal` | Az eszköz tényleges, belső on/off állapota. |

## 2. Tárolt állapot

Pontosan két logikai érték tárolható:

| Érték | Kezdőérték | Jelentés |
|---|---|---|
| `internal_state` | `False` | Az egyetlen on/off állapot-igazságforrás. |
| `online` | `True` | A Main elérhető-e. |

Nincs külön `main_state`, `reported_state`, utoljára ismert állapot vagy szinkronizáló
állapotgép.

## 3. Entitásviselkedés

### Main

- `is_on` közvetlenül `internal_state`.
- `available` közvetlenül `online`.
- ONLINE állapotban a Main kapcsolása módosítja az `internal_state` értékét.
- OFFLINE állapotban a Main valódi HA `unavailable`, ezért nem vezérelhető.
- A Main nem tárol saját állapotot.

### Online

- `is_on` közvetlenül `online`.
- Kikapcsolása csak `online=False` értéket állít; az `internal_state` változatlan.
- Bekapcsolása csak `online=True` értéket állít. A Main elérhetővé válik, és közvetlenül
  az Internal aktuális értékével jelenik meg.

### Internal

- `is_on` közvetlenül `internal_state`.
- Mindig elérhető és vezérelhető.
- Kapcsolása online és offline állapotban is módosítja az `internal_state` értékét.

## 4. Állapottábla

| `online` | Művelet | Új `online` | Új `internal_state` | Main HA-állapot |
|---|---|---|---|---|
| `True` | Main ON | `True` | `True` | `on` |
| `True` | Main OFF | `True` | `False` | `off` |
| `True` | Internal ON/OFF | `True` | kért érték | az Internal értéke |
| `True` | Online OFF | `False` | változatlan | `unavailable` |
| `True` | Online ON | `True` | változatlan | az Internal értéke |
| `False` | Main ON/OFF service | `False` | változatlan | `unavailable` |
| `False` | Internal ON/OFF | `False` | kért érték | `unavailable` |
| `False` | Online ON | `True` | változatlan | az Internal értéke |
| `False` | Online OFF | `False` | változatlan | `unavailable` |

Minden művelet idempotens. Egy tényleges változás pontosan egy mentést és egy
dispatcher-frissítést okoz; változatlan érték beállítása egyiket sem.

## 5. Perzisztencia

- Csak az `internal_state` és az `online` tárolódik config entrynként HA `Store`-ban.
- Újraindítás után mindkét érték visszaáll.
- Hiányzó tároló esetén a kezdőértékek használatosak.
- Sérült vagy nem boolean tároló esetén figyelmeztetés naplózandó és a kezdőértékek
  használatosak.
- Config entry törlésekor a saját Store törlendő.

## 6. UI és dashboard-kártya

- A config flow teljesen UI-alapú és a példány nevét kéri.
- Mindhárom entitás egy közös Device-hoz tartozik.
- A `custom:virtual-switch-card` megjelenik a grafikus kártyaválasztóban, YAML nélkül
  hozzáadható, és a grafikus szerkesztő a VirtualSwitch Main entitásaira szűr.
- Egy Main entity ID-ból automatikusan megtalálja az Internal és Online entitást.
- A kártya csak szabványos HA entity row-kat és service callokat használ; nincs benne
  állapotlogika.
- A resource automatikusan, verzióparaméterrel regisztrálódik.

## 7. TimedSwitch együttműködés

- A TimedSwitch a Main entitást szabványos switch célként használhatja.
- A két integráció között nincs privát állapot- vagy controllerkapcsolat.

## 8. Elfogadási tesztek

| Teszt | Kezdőállapot | Művelet | Elvárás |
|---|---|---|---|
| T1 | online, Internal OFF | Internal ON | Main `on`, Internal `on` |
| T2 | online, Internal ON | Online OFF | Main `unavailable`, Internal `on` |
| T3 | offline, Internal ON | Internal OFF | Main `unavailable`, Internal `off` |
| T4 | offline, Internal OFF | Internal ON | Main `unavailable`, Internal `on` |
| T5 | offline, Internal ON | Online ON | Main elérhető és `on` |
| T6 | offline, Internal OFF | Online ON | Main elérhető és `off` |
| T7 | online, Internal OFF | Main ON | Internal és Main `on` |
| T8 | offline, Internal OFF | Main ON service | Internal változatlan, Main `unavailable` |
| T9 | tetszőleges | azonos érték ismétlése | változatlan, nincs mentés/frissítési loop |
| T10 | offline, Internal ON | mentés és újratöltés | offline, Internal ON áll vissza |
