# Virtual Switch

A Virtual Switch egy állapottartó, szimulált Home Assistant kapcsoló. Külön
kezeli a belső kapcsolóállást és a szimulált eszköz elérhetőségét/állapotát,
ezért automatizálások, hibakezelés és más integrációk tesztelésére is alkalmas.

## Követelmények

- működő Home Assistant telepítés;
- hozzáférés a Home Assistant `config` könyvtárához;
- újraindítási jogosultság;
- a saját kártyához a `frontend` és `lovelace` integráció.

Külső Python-csomagot nem igényel.

## Telepítés

1. Másold a `custom_components/virtual_switch` könyvtárat a Home Assistant
   konfigurációs könyvtárába:

   ```text
   <config>/custom_components/virtual_switch/
   ```

2. Indítsd újra a Home Assistantot.
3. Nyisd meg a **Beállítások → Eszközök és szolgáltatások → Integráció
   hozzáadása** oldalt.
4. Keresd meg a **Virtual Switch** integrációt, majd add hozzá.

Frissítéskor cseréld le a teljes `virtual_switch` könyvtár tartalmát, majd indítsd
újra a Home Assistantot. A példányok mentett belső állapota megmarad.

## Konfiguráció

Az integráció a Home Assistant felületén konfigurálható; nem igényel
`configuration.yaml` bejegyzést.

Új példánynál add meg:

- **Név:** az eszköz és a létrejövő entitások neveinek alapja;
- **Egyedi állapotok:** opcionális, soronként egy állapot az alábbi formában:
  `<név>[:available][:is_on]`.

A név után megadható, hogy a főkapcsoló elérhető legyen-e, illetve milyen
kapcsolóállapotot mutasson. Az értékek `true`, `false` vagy az `is_on` mezőben
`none` lehetnek. Az üres mezők alapértéke: `available=true`, `is_on=none`.

```text
karbantartas:false
beragadt_be:true:true
hiba_jelzes:true:none
```

A `false` elérhetőség mindig `unavailable` főkapcsolót eredményez, ezért ilyenkor
az `is_on` értékét az integráció figyelmen kívül hagyja. A rögzített állapotnevek
(`online`, `unavailable`, `unknown`, `error`) nem használhatók egyedi névként, és
az állapotnevek kis- és nagybetűtől függetlenül egyediek.

Az egyedi állapotok később a **Beállítások → Eszközök és szolgáltatások → Virtual
Switch → Konfigurálás** útvonalon módosíthatók. A mentés után az integrációpéldány
újratöltődik.

## UI megjelenítés

Az integráció egy **Virtual Switch Card** nevű egyedi dashboard-kártyát tartalmaz.
Storage módban az erőforrás automatikusan regisztrálódik. Dashboard szerkesztésekor
válaszd a **Kártya hozzáadása → Virtual Switch Card** elemet, majd a példány
`switch.<név>_main` entitását.

YAML dashboard vagy YAML erőforrásmód esetén add hozzá kézzel:

```yaml
lovelace:
  resources:
    - url: /virtual_switch/virtual-switch-card.js
      type: module
```

A kártya YAML konfigurációja:

```yaml
type: custom:virtual-switch-card
entity: switch.teszt_kapcsolo_main
```

A kártyán a főkapcsoló, a belső kapcsoló és a választható eszközállapotok együtt
jelennek meg.

## Használat

Minden példány három entitást hoz létre:

| Entitás | Szerep |
|---|---|
| `switch.<név>_main` | A szimulált eszköz kívülről használt főkapcsolója |
| `switch.<név>_internal` | A ténylegesen megőrzött belső BE/KI állapot |
| `select.<név>_status` | Az elérhetőség és a kijelzett állapot szimulálása |

A rögzített státuszok viselkedése:

| Státusz | Főkapcsoló |
|---|---|
| `Online` | Elérhető, és a belső kapcsoló állapotát mutatja |
| `Unavailable` | `unavailable`, nem vezérelhető a főkapcsolón keresztül |
| `Unknown` | Elérhető, állapota `unknown` |
| `Error` | Elérhető, állapota `unknown`; külön tesztállapotként megkülönböztethető |

Online állapotban a főkapcsoló módosítása a belső kapcsolót is módosítja. Más
státuszban a főkapcsolón küldött BE/KI parancs nem változtatja meg a belső
állapotot. Az `Internal` kapcsoló viszont minden státuszban állítható, így előre
beállítható, milyen állapottal térjen vissza az eszköz, amikor ismét `Online` lesz.

A státusz és a belső kapcsolóállás újraindítás után visszaáll. Az entitások egy
közös Home Assistant-eszközhöz tartoznak, ezért automatizálásokban, scriptekben és
a fejlesztői eszközökben a szokásos `switch.turn_on`, `switch.turn_off` és
`select.select_option` szolgáltatásokkal használhatók.

## Példa automatizálás teszteléséhez

Az alábbi művelet elérhetetlenné teszi a szimulált eszközt:

```yaml
action: select.select_option
target:
  entity_id: select.teszt_kapcsolo_status
data:
  option: Unavailable
```

A visszaállításhoz válaszd az `Online` opciót. A rögzített státuszok a Select
entitásban nagy kezdőbetűvel jelennek meg.

## Eltávolítás

A **Beállítások → Eszközök és szolgáltatások → Virtual Switch** oldalon töröld az
összes példányt, indítsd újra a Home Assistantot, majd távolítsd el a
`<config>/custom_components/virtual_switch` könyvtárat. A példány törlése a hozzá
tartozó mentett állapotot is eltávolítja.
