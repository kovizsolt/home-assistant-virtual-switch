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
    this._nativeCard = undefined;
    this._buildPromise = undefined;
    this.replaceChildren();
    this._ensureCard();
  }

  set hass(hass) {
    this._hass = hass;
    if (this._nativeCard) this._nativeCard.hass = hass;
    else this._ensureCard();
  }

  getCardSize() { return 3; }
  getGridOptions() { return { columns: 6, min_columns: 4 }; }

  _configForNativeCard() {
    const main = this._config.entity;
    const objectId = main.slice("switch.".length, -MAIN_SUFFIX.length);
    const internal = `switch.${objectId}_internal`;
    const online = `switch.${objectId}_online`;
    const mainState = this._hass.states[main];
    const rows = [
      this._hass.states[main] ? { entity: main, name: "Main" } : undefined,
      this._hass.states[online] ? { entity: online, name: "Online" } : undefined,
      this._hass.states[internal] ? { entity: internal, name: "Internal device state" } : undefined,
    ].filter(Boolean);
    return {
      type: "entities",
      title: this._config.name || mainState?.attributes?.friendly_name?.replace(/ Main$/, "") || "Virtual Switch",
      icon: "mdi:toggle-switch-variant",
      show_header_toggle: false,
      state_color: true,
      entities: rows,
    };
  }

  _ensureCard() {
    if (!this._config || !this._hass || this._nativeCard || this._buildPromise) return;
    this._buildPromise = window.loadCardHelpers()
      .then((helpers) => {
        const card = helpers.createCardElement(this._configForNativeCard());
        card.hass = this._hass;
        this._nativeCard = card;
        this.replaceChildren(card);
      })
      .catch((error) => {
        const alert = document.createElement("ha-alert");
        alert.setAttribute("alert-type", "error");
        alert.textContent = `Virtual Switch card: ${error.message}`;
        this.replaceChildren(alert);
      })
      .finally(() => { this._buildPromise = undefined; });
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
    description: "Main, internal and connectivity controls for one Virtual Switch",
    preview: true,
    getEntitySuggestion: (hass, entityId) => {
      if (!VirtualSwitchCard._isMain(hass, entityId)) return null;
      return { config: { type: "custom:virtual-switch-card", entity: entityId } };
    },
  });
}
