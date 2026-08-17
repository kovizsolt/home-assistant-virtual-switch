# Virtual Switch elfogadási forgatókönyvek

Ezek a SPEC.md 5. szakaszának emberileg ellenőrizhető, implementáció előtti
elfogadási tesztjei.

## Rejtett bekapcsolás

```text
[ONLINE, internal=OFF, reported=OFF]
  --go_offline-->
[OFFLINE, internal=OFF, reported=OFF]
  --internal_on-->
[OFFLINE, internal=ON, reported=OFF]
  --go_online-->
[ONLINE, internal=ON, reported=ON]
```

## Rejtett kikapcsolás

```text
[ONLINE, internal=ON, reported=ON]
  --go_offline-->
[OFFLINE, internal=ON, reported=ON]
  --internal_off-->
[OFFLINE, internal=OFF, reported=ON]
  --go_online-->
[ONLINE, internal=OFF, reported=OFF]
```

## Főkapcsoló vezérlése offline állapotban

```text
[OFFLINE, internal=OFF, reported=OFF]
  --main_on-->
[OFFLINE, internal=ON, reported=OFF]
```

A főkapcsoló parancsa eljut a szimulált eszközhöz, de a visszajelzés offline állapotban
nem jut vissza a főkapcsoló HA-állapotába.

## Teljesen UI-vezérelt kártya-hozzáadás

```text
Dashboard szerkesztése
  -> Kártya hozzáadása
  -> Virtual Switch Card
  -> Virtual Switch főkapcsoló kiválasztása
  -> Mentés
  -> main + internal + online egyetlen kártyán
```

A folyamat nem igényel YAML-szerkesztést, frontend fájlmásolást vagy kézi dashboard
resource-bejegyzést.

## Timed Switch együttműködés

```text
Új Timed Switch
  -> Cél típusa: új Virtual Switch
  -> Virtual Switch saját UI config flow
  -> új önálló Virtual Switch Device
  -> annak main kapcsolója a Timed Switch target_entity_id értéke
```

Meglévő Virtual Switch esetén a felhasználó közvetlenül annak `main` kapcsolóját választja
ki. A két integráció ezután csak a Home Assistant szabványos switch interfészén keresztül
kommunikál.
