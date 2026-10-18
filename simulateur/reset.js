// Réinitialisation des champs : touche Échap, et icône ↺ affichée dans le champ quand la valeur diffère du défaut.
const doc = window.parent.document, defauts = __DEFAUTS__;
const champs = () => [...doc.querySelectorAll("input[aria-label]")].filter((c) => c.getAttribute("aria-label") in defauts);

function reinitialiser(champ) {
  champ.focus();
  Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set.call(champ, defauts[champ.getAttribute("aria-label")]);
  champ.dispatchEvent(new Event("input", { bubbles: true }));
  champ.blur();
}

function actualiser() {
  for (const champ of champs()) {
    const boite = champ.parentElement;
    let icone = boite.querySelector(".reset-defaut");
    if (!icone) {
      icone = doc.createElement("span");
      icone.className = "reset-defaut";
      icone.textContent = "↺";
      icone.title = "Valeur par défaut";
      icone.style.cssText = "position:absolute;right:10px;top:50%;transform:translateY(-50%);cursor:pointer;color:#9aa0a6;font-size:16px;line-height:1;user-select:none";
      icone.addEventListener("mousedown", (e) => { e.preventDefault(); reinitialiser(champ); });
      boite.style.position = "relative";
      boite.appendChild(icone);
    }
    const modifie = champ.value !== defauts[champ.getAttribute("aria-label")];
    icone.style.display = modifie && doc.activeElement !== champ ? "" : "none";
  }
}

const w = window.parent;
if (w.__resetEcoute) { doc.removeEventListener("keydown", w.__resetEcoute, true); w.__resetObs.disconnect(); }
w.__resetEcoute = (e) => {
  if (e.key === "Escape" && champs().includes(e.target)) reinitialiser(e.target);
};
doc.addEventListener("keydown", w.__resetEcoute, true);
let attente;
w.__resetObs = new MutationObserver(() => { cancelAnimationFrame(attente); attente = requestAnimationFrame(actualiser); });
w.__resetObs.observe(doc.body, { childList: true, subtree: true });
for (const evt of ["input", "focusin", "focusout"]) doc.addEventListener(evt, () => setTimeout(actualiser, 0), true);
actualiser();
