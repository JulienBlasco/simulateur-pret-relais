// Champs de saisie : espaces des milliers insérés à la frappe (non éditables), réinitialisation par Échap ou par l'icône ↺
// (affichée quand la valeur diffère du défaut), boutons −/+ pour les champs qui ont un pas.
const doc = window.parent.document, defauts = __DEFAUTS__, pas = __PAS__;
const champs = () => [...doc.querySelectorAll("input[aria-label]")].filter((c) => c.getAttribute("aria-label") in defauts);

// Écrit une valeur comme si elle était saisie, puis valide (la perte de focus déclenche le recalcul).
function ecrire(champ, texte) {
  champ.focus();
  fixer(champ, texte);
  champ.dispatchEvent(new Event("input", { bubbles: true }));
  champ.blur();
}

const reinitialiser = (champ) => ecrire(champ, defauts[champ.getAttribute("aria-label")]);

function incrementer(champ, signe) {
  const libelle = champ.getAttribute("aria-label"), decimales = (defauts[libelle].split(",")[1] || "").length;
  const courant = parseFloat(champ.value.replace(/\s/g, "").replace(",", ".")) || 0;
  const [entier, dec] = Math.max(0, courant + signe * pas[libelle]).toFixed(decimales).split(".");
  ecrire(champ, entier.replace(/\B(?=(\d{3})+$)/g, " ") + (dec ? "," + dec : ""));
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

function bouton(texte, titre, action) {
  const b = doc.createElement("span");
  b.textContent = texte;
  b.title = titre;
  b.style.cssText = "cursor:pointer;color:#9aa0a6;font-size:16px;line-height:1;padding:0 3px;user-select:none";
  b.addEventListener("mousedown", (e) => { e.preventDefault(); action(); });
  return b;
}

function actualiser() {
  for (const champ of champs()) {
    const boite = champ.parentElement, libelle = champ.getAttribute("aria-label");
    let outils = boite.querySelector(".outils-champ");
    if (!outils) {
      outils = doc.createElement("span");
      outils.className = "outils-champ";
      outils.style.cssText = "position:absolute;right:6px;top:50%;transform:translateY(-50%);display:flex;align-items:center";
      // Le champ est retrouvé au clic (React peut remplacer l'élément <input> après la création des boutons).
      const courant = () => champs().find((c) => c.getAttribute("aria-label") === libelle);
      const icone = bouton("↺", "Valeur par défaut", () => reinitialiser(courant()));
      icone.className = "reset-defaut";
      outils.appendChild(icone);
      if (libelle in pas) {
        outils.appendChild(bouton("−", "Diminuer", () => incrementer(courant(), -1)));
        outils.appendChild(bouton("+", "Augmenter", () => incrementer(courant(), 1)));
      }
      boite.style.position = "relative";
      boite.appendChild(outils);
    }
    champ.style.paddingRight = libelle in pas ? "64px" : "30px";
    outils.style.display = doc.activeElement === champ ? "none" : "flex";
    outils.querySelector(".reset-defaut").style.display = champ.value !== defauts[libelle] ? "" : "none";
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
// Les boutons laissés par une exécution précédente ont des écouteurs morts (iframe rechargée) : on les recrée.
doc.querySelectorAll(".outils-champ").forEach((i) => i.remove());
let attente;
w.__resetObs = new MutationObserver(() => { cancelAnimationFrame(attente); attente = requestAnimationFrame(actualiser); });
w.__resetObs.observe(doc.body, { childList: true, subtree: true });
for (const evt of ["input", "focusin", "focusout"]) doc.addEventListener(evt, () => setTimeout(actualiser, 0), true);
actualiser();
