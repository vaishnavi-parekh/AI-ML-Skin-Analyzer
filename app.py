"""
app.py - tiny web app.
  * Open http://127.0.0.1:5000  -> upload a photo, see the marked result + report
  * POST a photo to /analyze    -> JSON back (this is what a PHP site would call)

Start it:   python app.py
"""
import uuid
from pathlib import Path

from flask import Flask, jsonify, request, Response, render_template, send_from_directory
from flask_cors import CORS

from skin_analyzer import analyze_image

BASE = Path(__file__).parent
UPLOADS = BASE / "uploads"
GLOWRA = BASE / "glowra-ui"
UPLOADS.mkdir(exist_ok=True)

app = Flask(__name__, static_folder=str(BASE / "static"), static_url_path="/static")
CORS(app)


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Skin Analyzer</title>
 <style>
  :root{--ink:#17222d;--muted:#6f7d87;--teal:#168b83;--mint:#e9f7f3;--line:#dfe8e6;--card:#fff}
  *{box-sizing:border-box} body{margin:0;min-height:100vh;font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif;color:var(--ink);background:linear-gradient(135deg,#f4fbfa,#edf3f7)}
  .shell{max-width:1120px;margin:auto;padding:34px 20px 50px}.top{display:flex;align-items:center;justify-content:space-between;margin-bottom:30px}
  .brand{display:flex;align-items:center;gap:12px}.brand-mark{width:42px;height:42px;border-radius:14px;display:grid;place-items:center;background:var(--teal);color:white;font-size:22px;box-shadow:0 8px 20px #168b8340}.brand h1{font-size:21px;margin:0}.brand small{display:block;color:var(--muted);margin-top:3px}
  .badge{padding:8px 12px;border-radius:999px;background:#fff;color:var(--teal);font-size:12px;font-weight:700;border:1px solid var(--line)}
  .hero{display:grid;grid-template-columns:1.05fr .95fr;gap:24px;align-items:stretch}.card{background:var(--card);border:1px solid var(--line);border-radius:24px;box-shadow:0 18px 45px #203b4810}.intro{padding:34px}.intro h2{font-size:38px;line-height:1.08;margin:0 0 14px;letter-spacing:-1.5px}.intro h2 span{color:var(--teal)}.intro p{color:var(--muted);line-height:1.6;margin:0 0 24px}.tips{display:grid;gap:11px;color:#40515b;font-size:14px}.tips div{display:flex;gap:10px;align-items:center}.tick{width:24px;height:24px;border-radius:50%;display:grid;place-items:center;background:var(--mint);color:var(--teal);font-weight:800}
  .upload{padding:24px}.drop{min-height:280px;border:2px dashed #acd7d0;border-radius:19px;background:#f6fcfb;display:flex;align-items:center;justify-content:center;text-align:center;cursor:pointer;transition:.2s}.drop:hover,.drop.over{border-color:var(--teal);background:#eefaf7}.drop strong{display:block;font-size:17px;margin:12px 0 5px}.drop p{color:var(--muted);font-size:13px;margin:0}.upload-icon{font-size:38px;color:var(--teal)}#file{display:none}#preview{display:none;max-width:150px;max-height:155px;border-radius:14px;margin:auto;object-fit:cover}.actions{display:flex;gap:10px;margin-top:16px}.button{flex:1;border:0;border-radius:12px;padding:13px 18px;font-size:15px;font-weight:700;cursor:pointer}.primary{background:var(--teal);color:white;box-shadow:0 8px 18px #168b8330}.primary:disabled{background:#9cb9b5;cursor:wait}.secondary{background:#f1f5f4;color:#40515b}.err{color:#b42318;font-size:13px;margin:12px 0 0}.legend{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px;color:var(--muted);font-size:12px}.legend span{display:inline-flex;align-items:center;gap:5px}.dot{width:9px;height:9px;border-radius:50%;display:inline-block}
  #out{display:none;margin-top:24px;grid-template-columns:1.1fr .9fr;gap:24px}.result-card{padding:20px}.result-card h3{margin:0 0 14px;font-size:17px}.result-card img{display:block;width:100%;max-height:620px;object-fit:contain;border-radius:16px;background:#f2f5f4}.report{padding:20px}.report h3{margin:0 0 14px}.report table{width:100%;border-collapse:collapse}.report td{padding:12px 0;border-bottom:1px solid #edf1f0;vertical-align:top;font-size:14px}.report td:first-child{color:var(--muted);width:44%}.report td:last-child{font-weight:650}.note{font-size:12px;line-height:1.5;color:var(--muted);margin:18px 0 0;padding:12px;background:#f6f8f7;border-radius:10px}
  @media(max-width:800px){.hero,#out{grid-template-columns:1fr}.intro h2{font-size:32px}.top{margin-bottom:20px}.badge{display:none}}
 </style></head><body><main class="shell">
 <header class="top"><div class="brand"><div class="brand-mark">✦</div><div><h1>AI Skin Analyzer</h1><small>Visual skin insights, made simple</small></div></div><div class="badge">Prototype analysis</div></header>
 <section class="hero"><div class="card intro"><h2>Understand your skin <span>at a glance.</span></h2><p>Upload a clear, front-facing photo and get an easy-to-read visual report of visible skin markers.</p><div class="tips"><div><span class="tick">✓</span>Use even lighting</div><div><span class="tick">✓</span>Keep your face centered</div><div><span class="tick">✓</span>No filters or heavy makeup</div></div></div>
 <div class="card upload"><label class="drop" id="drop" for="file"><div id="dropContent"><div class="upload-icon">⇧</div><strong>Drop your photo here</strong><p>or click to browse · JPG, PNG</p></div><img id="preview" alt="selected preview"></label><input type="file" id="file" accept="image/*"><div class="actions"><button class="button secondary" id="clear" type="button">Clear</button><button class="button primary" id="go" type="button">Analyze photo</button></div><p id="msg"></p><div class="legend"><span><i class="dot" style="background:#e22"></i>Acne / redness</span><span><i class="dot" style="background:#1677d2"></i>Dark spots</span><span><i class="dot" style="background:#18a558"></i>Pigmentation</span></div></div></section>
 <section id="out"><div class="card result-card"><h3>Visual result</h3><img id="img" alt="skin analysis result"></div><div class="card report"><h3>Analysis summary</h3><table id="rep"></table><p class="note" id="note"></p></div></section>
 </main>
<script>
const $ = id => document.getElementById(id);
const showPreview = () => {
  const f = $("file").files[0];
  if (!f) return;
  $("preview").src = URL.createObjectURL(f);
  $("preview").style.display = "block";
  $("dropContent").style.display = "none";
};
$("file").onchange = showPreview;
$("drop").ondragover = e => { e.preventDefault(); $("drop").classList.add("over"); };
$("drop").ondragleave = () => $("drop").classList.remove("over");
$("drop").ondrop = e => {
  e.preventDefault(); $("drop").classList.remove("over");
  if (e.dataTransfer.files.length) { $("file").files = e.dataTransfer.files; showPreview(); }
};
$("clear").onclick = () => {
  $("file").value = ""; $("preview").style.display = "none";
  $("dropContent").style.display = "block"; $("out").style.display = "none"; $("msg").textContent = "";
};
$("go").onclick = async () => {
  const f = $("file").files[0];
  if (!f) { $("msg").textContent = "Choose a photo first."; return; }
  $("go").disabled = true; $("msg").className = ""; $("msg").textContent = "Analyzing... (first run is slower)";
  const fd = new FormData(); fd.append("image", f);
  try {
    const r = await (await fetch("/analyze", {method:"POST", body:fd})).json();
    if (!r.ok) { $("msg").className = "err"; $("msg").textContent = r.error; $("out").style.display="none"; }
    else {
      $("msg").textContent = "";
      $("img").src = r.result_url + "?t=" + Date.now();
      const st = r.skin_type;
      const rows = [
        ["Skin type", st.type + (st.maybe_sensitive ? " (may be sensitive)" : "")],
        ["Why", st.reasons.join("; ")],
        ["Acne spots (red)", r.acne.count],
        ["Dark spots (blue)", r.dark_spots.count + " (" + r.dark_spots.area_percent_of_skin + "% of skin)"],
        ["Pigmentation (green)", r.pigmentation.count + " (" + r.pigmentation.area_percent_of_skin + "% of skin)"],
        ["Acne method", r.acne.method]
      ];
      $("rep").innerHTML = rows.map(x => "<tr><td>"+x[0]+"</td><td>"+x[1]+"</td></tr>").join("");
      $("note").textContent = r.note;
      $("out").style.display = "grid";
    }
  } catch (e) { $("msg").className = "err"; $("msg").textContent = "Something went wrong: " + e; }
  $("go").disabled = false;
};
</script></body></html>"""


@app.get("/")
def home():
    # The original skin-analyzer prototype is the active application UI.
    return Response(PAGE, mimetype="text/html")


def _scan_page():
    scan = (GLOWRA / "scan.html").read_text(encoding="utf-8")
    scan = scan.replace(
        '</body>',
        '<script src="js/analyzer_bridge.js?v=4"></script></body>',
    )
    return Response(scan, mimetype="text/html")


@app.get("/<path:name>")
def glowra_page(name):
    """Serve the supplied Glowra site with its original relative structure."""
    if name in ("scan.html", "skin-analyzer.html"):
        return _scan_page()
    return send_from_directory(GLOWRA, name)


@app.get("/files/<path:name>")
def uploaded_file(name):
    return send_from_directory(UPLOADS, name)


@app.get("/health")
def health():
    return jsonify({"status": "running"})


@app.post("/analyze")
def analyze():
    # PHP must send the photo in a form field called "image"
    file = request.files.get("image")
    if file is None:
        return jsonify({"ok": False, "error": "Send a file in the 'image' field."}), 400

    name = f"{uuid.uuid4().hex}.jpg"
    saved = UPLOADS / name
    file.save(saved)

    result = analyze_image(saved)
    if result.get("ok"):
        result["result_url"] = f"/files/{Path(result.pop('result_image')).name}"
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
