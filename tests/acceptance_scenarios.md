# Virtual Switch elfogadási forgatókönyvek

## Elérhetőségi állapotváltozás

```text
[status=online, internal=OFF, main=OFF]
  --status unavailable-->
[status=unavailable, internal=OFF, main=unavailable]
  --internal ON-->
[status=unavailable, internal=ON, main=unavailable]
  --status error-->
[status=error, internal=ON, main=unknown]
  --status online-->
[status=online, internal=ON, main=ON]
```

## Online állapotváltozás

```text
[status=online, internal=OFF, main=OFF]
  --internal ON-->
[status=online, internal=ON, main=ON]
  --main OFF-->
[status=online, internal=OFF, main=OFF]
```

## UI-vezérelt kártya-hozzáadás

```text
Dashboard szerkesztése
  -> Kártya hozzáadása
  -> Virtual Switch Card
  -> Virtual Switch Main kiválasztása
  -> Mentés
  -> Main + Internal + dinamikus státuszgombok egyetlen kártyán
```

A folyamat nem igényel YAML-szerkesztést, frontend fájlmásolást vagy kézi resource-bejegyzést.
