// Champs de saisie : espaces des milliers insérés à la frappe (non éditables), réinitialisation par Échap ou par l'icône ↺
// (affichée dans le champ quand la valeur diffère du défaut).
const doc = window.parent.document, defauts = __DEFAUTS__;
const champs = () => [...doc.querySelectorAll("input[aria-label]")].filter((c) => c.getAttribute("aria-label") in defauts);

function reinitialiser(champ) {
  champ.focus();
  fixer(champ, defauts[champ.getAttribute("aria-label")]);
  champ.dispatchEvent(new Event("input", { bubbles: true }));
  champ.blur();
}

const fixer = (champ, valeur) => Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set.call(champ, valeur);

// Reformate pendant la frappe : chiffres groupés par 3, une seule virgule ; le curseur reste sur le même caractère utile.
function formater(champ) {
  const v = champ.value, utiles = (t) => t.replace(/[^\d,.]/g, "").length;
  const n = utiles(v.slice(0, champ.selectionStart));
  let brut = v.replace(/\./g, ",").replace(/[^\d,]/g, "");
  const i = brut.indexOf(",");
  if (i >= 0) brut = brut.slice(0, i + 1) + brut.slice(i + 1).replace(/,/g, "");
  const [entier, decimales] = brut.split(",");
  const res = entier.replace(/\B(?=(\d{3})+(?!\d))/g, " ") + (decimales === undefined ? "" : "," + decimales);
  if (res === v) return;
  fixer(champ, res);
  let pos = 0, vus = 0;
  while (pos < res.length && vus < n) if (/[\d,]/.test(res[pos++])) vus++;
  champ.setSelectionRange(pos, pos);
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
      icone.addEventListener("mousedown", (e) => { e.preventDefault(); reinitialiser(boite.querySelector("input")); });
      boite.style.position = "relative";
      boite.appendChild(icone);
    }
    const modifie = champ.value !== defauts[champ.getAttribute("aria-label")];
    icone.style.display = modifie && doc.activeElement !== champ ? "" : "none";
  }
}

const w = window.parent;
if (w.__resetEcoute) {
  doc.removeEventListener("keydown", w.__resetEcoute, true);
  doc.removeEventListener("input", w.__resetFormat, true);
  w.__resetObs.disconnect();
}
w.__resetEcoute = (e) => {
  const champ = e.target;
  if (!champs().includes(champ)) return;
  if (e.key === "Escape") return reinitialiser(champ);
  // L'espace des milliers n'est pas éditable : Retour arrière / Suppr le saute.
  const pos = champ.selectionStart;
  if (pos !== champ.selectionEnd) return;
  if (e.key === "Backspace" && champ.value[pos - 1] === " ") champ.setSelectionRange(pos - 1, pos - 1);
  if (e.key === "Delete" && champ.value[pos] === " ") champ.setSelectionRange(pos + 1, pos + 1);
};
w.__resetFormat = (e) => { if (champs().includes(e.target)) formater(e.target); };
doc.addEventListener("keydown", w.__resetEcoute, true);
doc.addEventListener("input", w.__resetFormat, true);
let attente;
w.__resetObs = new MutationObserver(() => { cancelAnimationFrame(attente); attente = requestAnimationFrame(actualiser); });
w.__resetObs.observe(doc.body, { childList: true, subtree: true });
for (const evt of ["input", "focusin", "focusout"]) doc.addEventListener(evt, () => setTimeout(actualiser, 0), true);
actualiser();
