import json
import os
import urllib.request

URL = "https://api.alquran.cloud/v1/quran/quran-uthmani"
OUT = "/opt/estekhare/quran_pages.json"

req = urllib.request.Request(
    URL,
    headers={"User-Agent": "EstekhareLocal/1.0"}
)

print("در حال دریافت متن قرآن...")
with urllib.request.urlopen(req, timeout=60) as response:
    payload = json.loads(response.read().decode("utf-8"))

if payload.get("code") != 200:
    raise SystemExit("منبع قرآن پاسخ معتبر نداد؛ فایل فعلی سایت تغییر نکرد.")

pages = {}

for surah in payload["data"]["surahs"]:
    for ayah in surah["ayahs"]:
        page = int(ayah["page"])
        if 1 <= page <= 603:
            pages.setdefault(str(page), {
                "page": page,
                "surah": surah["name"],
                "ayah": ayah["numberInSurah"],
                "text": ayah["text"],
                "global_ayah": ayah["number"]
            })

missing = [p for p in range(1, 604) if str(p) not in pages]
if missing:
    raise SystemExit(
        f"اطلاعات بعضی صفحات ناقص است؛ تعداد صفحات موجود: {len(pages)}. "
        "تغییری در سایت اعمال نشد."
    )

tmp = OUT + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(
        {"source": URL, "pages": pages},
        f, ensure_ascii=False, separators=(",", ":")
    )
os.replace(tmp, OUT)

print(f"ذخیره شد: {len(pages)} صفحه در {OUT}")
print("نمونه صفحه 165:", pages["165"])
