# Virtual Switch elfogadási forgatókönyvek

## Offline állapotváltozás

```text
[online=ON, internal=OFF, main=OFF]
  --online OFF-->
[online=OFF, internal=OFF, main=unavailable]
  --internal ON-->
[online=OFF, internal=ON, main=unavailable]
  --online ON-->
[online=ON, internal=ON, main=ON]
```

## Online állapotváltozás

```text
[online=ON, internal=OFF, main=OFF]
  --internal ON-->
[online=ON, internal=ON, main=ON]
  --main OFF-->
[online=ON, internal=OFF, main=OFF]
```

## UI-vezérelt kártya-hozzáadás

```text
Dashboard szerkesztése
  -> Kártya hozzáadása
  -> Virtual Switch Card
  -> Virtual Switch Main kiválasztása
  -> Mentés
  -> Main + Online + Internal egyetlen kártyán
```

A folyamat nem igényel YAML-szerkesztést, frontend fájlmásolást vagy kézi resource-bejegyzést.
