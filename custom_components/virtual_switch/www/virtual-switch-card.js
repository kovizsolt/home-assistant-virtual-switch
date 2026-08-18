const MAIN_SUFFIX = "_main";

class VirtualSwitchCard extends HTMLElement {
  static getStubConfig(hass, entities = [], entitiesFill = []) {
    const candidates = [...entities, ...entitiesFill, ...Object.keys(hass?.states || {})];
    return { entity: candidates.find((entityId) => this._isMain(hass, entityId)) || "" };
  }

  static getConfigForm() {
    return {
      schema: [{
        name: "entity",
        required: true,
        selector: { entity: { filter: { domain: "switch", integration: "virtual_switch" } } },
      }],
      computeLabel: () => "Virtual Switch instance (Main)",
      assertConfig: (config) => {
        if (!config.entity?.startsWith("switch.") || !config.entity.endsWith(MAIN_SUFFIX)) {
          throw new Error("Select the Main switch of a Virtual Switch device");
        }
      },
    };
  }

  static _isMain(hass, entityId) {
    return entityId?.startsWith("switch.")
      && entityId.endsWith(MAIN_SUFFIX)
      && hass?.states?.[entityId]?.attributes?.virtual_switch === true;
  }

  setConfig(config) {
    if (!config.entity?.startsWith("switch.") || !config.entity.endsWith(MAIN_SUFFIX)) {
      throw new Error("Select the Main switch of a Virtual Switch device");
    }
    this._config = { ...config };
    this._build();
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._card && this._config) this._build();
    this._render();
  }

  getCardSize() { return 4; }
  getGridOptions() { return { columns: 9, min_columns: 4 }; }

  _entityIds() {
    const objectId = this._config.entity.slice("switch.".length, -MAIN_SUFFIX.length);
    return {
      main: this._config.entity,
      internal: `switch.${objectId}_internal`,
      status: `select.${objectId}_status`,
    };
  }

  _build() {
    this.replaceChildren();
    const style = document.createElement("style");
    style.textContent = `
      .content { padding: 0 16px 16px; }
      .entity-row { display: flex; align-items: center; min-height: 48px; gap: 16px; }
      .entity-row ha-icon { color: var(--state-icon-color); flex: 0 0 24px; }
      .entity-info { min-width: 0; flex: 1; }
      .entity-name { color: var(--primary-text-color); }
      .entity-state { color: var(--secondary-text-color); font-size: 12px; }
      .status { border-top: 1px solid var(--divider-color); margin-top: 4px; padding-top: 14px; }
      .status-label { color: var(--primary-text-color); margin-bottom: 8px; }
      .status-options { display: flex; flex-direction: column; align-items: flex-start; gap: 8px; }
      .radio-option { display: inline-flex; align-items: center; min-height: 32px; gap: 7px;
        color: var(--primary-text-color); cursor: pointer; }
      .radio-option input { width: 18px; height: 18px; margin: 0; cursor: pointer;
        accent-color: var(--primary-color); }
    `;

    this._card = document.createElement("ha-card");
    this._content = document.createElement("div");
    this._content.className = "content";
    this._mainRow = this._buildSwitchRow("mdi:toggle-switch", "Main switch:");
    this._internalRow = this._buildSwitchRow("mdi:memory", "Internal switch:");

    const status = document.createElement("div");
    status.className = "status";
    const statusLabel = document.createElement("div");
    statusLabel.className = "status-label";
    statusLabel.textContent = "Device status:";
    this._statusOptions = document.createElement("div");
    this._statusOptions.className = "status-options";
    status.append(statusLabel, this._statusOptions);
    this._content.append(this._mainRow.row, this._internalRow.row, status);
    this._card.appendChild(this._content);
    this.replaceChildren(style, this._card);
    this._render();
  }

  _buildSwitchRow(iconName, labelText) {
    const row = document.createElement("div");
    row.className = "entity-row";
    const icon = document.createElement("ha-icon");
    icon.setAttribute("icon", iconName);
    const info = document.createElement("div");
    info.className = "entity-info";
    const name = document.createElement("div");
    name.className = "entity-name";
    name.textContent = labelText;
    const state = document.createElement("div");
    state.className = "entity-state";
    info.append(name, state);
    const toggle = document.createElement("ha-switch");
    row.append(icon, info, toggle);
    return { row, state, toggle };
  }

  _renderSwitch(row, entityId) {
    const entity = this._hass?.states?.[entityId];
    row.row.style.display = entity ? "flex" : "none";
    if (!entity) return;
    row.state.textContent = this._hass.formatEntityState?.(entity) || entity.state;
    row.toggle.checked = entity.state === "on";
    row.toggle.disabled = entity.state === "unavailable" || entity.state === "unknown";
    row.toggle.onchange = (event) => {
      const service = event.target.checked ? "turn_on" : "turn_off";
      this._hass.callService("switch", service, { entity_id: entityId });
    };
  }

  _renderStatus(entityId) {
    const entity = this._hass?.states?.[entityId];
    const options = entity?.attributes?.options || [];
    this._statusOptions.replaceChildren();
    for (const option of options) {
      const radio = document.createElement("input");
      radio.type = "radio";
      radio.name = entityId;
      radio.value = option;
      radio.checked = option === entity.state;
      radio.addEventListener("change", () => {
        if (radio.checked) {
          this._hass.callService("select", "select_option", { entity_id: entityId, option });
        }
      });
      const label = document.createElement("label");
      label.className = "radio-option";
      const text = document.createElement("span");
      text.textContent = ["Online", "Unavailable", "Unknown", "Error"].includes(option)
        ? option.toLowerCase() : option;
      label.append(radio, text);
      this._statusOptions.appendChild(label);
    }
  }

  _render() {
    if (!this._hass || !this._config || !this._card) return;
    const ids = this._entityIds();
    const main = this._hass.states[ids.main];
    this._card.header = this._config.name
      || main?.attributes?.friendly_name?.replace(/ Main$/, "")
      || "Virtual Switch";
    this._renderSwitch(this._mainRow, ids.main);
    this._renderSwitch(this._internalRow, ids.internal);
    this._renderStatus(ids.status);
  }
}

if (!customElements.get("virtual-switch-card")) {
  customElements.define("virtual-switch-card", VirtualSwitchCard);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "virtual-switch-card")) {
  window.customCards.push({
    type: "virtual-switch-card",
    name: "Virtual Switch Card",
    description: "Main, internal and device status controls for one Virtual Switch",
    preview: true,
    getEntitySuggestion: (hass, entityId) => {
      if (!VirtualSwitchCard._isMain(hass, entityId)) return null;
      return { config: { type: "custom:virtual-switch-card", entity: entityId } };
    },
  });
}
