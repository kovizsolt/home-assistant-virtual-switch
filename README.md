# Virtual Switch

[Magyar dokumentáció](README.hu.md) · [Changelog](CHANGELOG.md)

Virtual Switch is a stateful, simulated switch for Home Assistant. It keeps its internal ON/OFF state separate from the simulated device status and availability, making it useful for testing automations, failure handling, and other integrations.

## Requirements

- Home Assistant 2025.9.4 or newer;
- access to the Home Assistant `config` directory;
- permission to restart Home Assistant;
- the `frontend` and `lovelace` integrations for the custom dashboard card.

No external Python package is required.

## Installation

### HACS (recommended)

1. Open HACS and select **Custom repositories** from the top-right menu.
2. Add `https://github.com/kovizsolt/home-assistant-virtual-switch` as an **Integration** repository.
3. Find **Virtual Switch** in HACS and download it.
4. Restart Home Assistant.
5. Open **Settings → Devices & services → Add integration**.
6. Search for **Virtual Switch** and add it.

### Manual installation

1. Copy `custom_components/virtual_switch` into the Home Assistant configuration directory so that the resulting path is:

   ```text
   <config>/custom_components/virtual_switch/
   ```

2. Restart Home Assistant.
3. Open **Settings → Devices & services → Add integration**.
4. Search for **Virtual Switch** and add it.

To update, replace the complete `virtual_switch` directory and restart Home Assistant. Saved internal states are retained.

### Local validation

Before publishing, run every local check from the repository root:

```bash
./scripts/validate.sh all
```

Individual modes are `static`, `tests`, and `hassfest`. Add `--no-pull` to the Hassfest or `all` mode to use the locally cached Docker image.

## Configuration

The integration is configured through the Home Assistant UI and requires no `configuration.yaml` entry.

For each new instance, enter:

- **Name:** base name for the device and its entities;
- **Custom statuses:** optional, one status per line in the format `<name>[:available][:is_on]`.

After the name, specify whether the main switch is available and which switch state it reports. Values may be `true` or `false`; the `is_on` field also accepts `none`. Empty fields default to `available=true` and `is_on=none`.

```text
maintenance:false
stuck_on:true:true
fault_signal:true:none
```

When availability is `false`, the main switch is always `unavailable`, so `is_on` is ignored. Reserved status names (`online`, `unavailable`, `unknown`, and `error`) cannot be used for custom statuses. Names must be unique regardless of letter case.

Custom statuses can later be changed under **Settings → Devices & services → Virtual Switch → Configure**. Saving the options reloads the integration instance.

## Dashboard display

The integration includes a custom **Virtual Switch Card**. In Lovelace storage mode, the resource is registered automatically. While editing a dashboard, select **Add card → Virtual Switch Card**, then select the instance's `switch.<name>_main` entity.

In YAML dashboard or YAML resource mode, add the resource manually:

```yaml
lovelace:
  resources:
    - url: /virtual_switch/virtual-switch-card.js
      type: module
```

Card configuration in YAML:

```yaml
type: custom:virtual-switch-card
entity: switch.test_switch_main
```

The card displays the main switch, internal switch, and selectable simulated device statuses together.

## Usage

Each instance creates three entities:

| Entity | Purpose |
|---|---|
| `switch.<name>_main` | Main switch exposed by the simulated device |
| `switch.<name>_internal` | Persisted internal ON/OFF state |
| `select.<name>_status` | Simulates availability and reported state |

Built-in status behavior:

| Status | Main switch behavior |
|---|---|
| `Online` | Available and reports the internal switch state |
| `Unavailable` | `unavailable`; cannot be controlled through the main switch |
| `Unknown` | Available with an `unknown` state |
| `Error` | Available with an `unknown` state; remains a distinct test status |

While Online, changing the main switch also changes the internal switch. In any other status, ON/OFF commands sent to the main switch do not change the internal state. The `Internal` switch remains controllable in every status, allowing you to prepare the state that will be reported when the device returns Online.

Status and internal switch state are restored after a restart. All entities belong to one Home Assistant device and can be used in automations, scripts, and developer tools through the standard `switch.turn_on`, `switch.turn_off`, and `select.select_option` actions.

## Automation test example

This action makes the simulated device unavailable:

```yaml
action: select.select_option
target:
  entity_id: select.test_switch_status
data:
  option: Unavailable
```

Select `Online` to restore availability. Built-in statuses appear title-cased in the Select entity.

## Removal

Remove every instance under **Settings → Devices & services → Virtual Switch**, restart Home Assistant, and then remove `<config>/custom_components/virtual_switch`. Removing an instance also removes its stored state.
