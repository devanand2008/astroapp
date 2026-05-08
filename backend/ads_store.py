import json
import os
import shutil
import uuid
from datetime import datetime


ADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads", "ads")
MANIFEST_PATH = os.path.join(ADS_DIR, "ads_manifest.json")
AD_TYPES = {"web", "pdf", "banner", "video"}



def _ensure_dir():
    os.makedirs(ADS_DIR, exist_ok=True)


def _public_path(filename):
    return f"/uploads/ads/{filename}"


def _safe_ext(filename):
    ext = os.path.splitext(filename or "")[1].lower().strip(".")
    return ext or "bin"


def _normalize_ad(ad):
    if not isinstance(ad, dict):
        return None
    ad_type = ad.get("type")
    path = ad.get("path")
    if ad_type not in AD_TYPES or not path:
        return None
    ad_id = str(ad.get("id") or uuid.uuid4().hex[:10])
    return {
        "id": ad_id,
        "type": ad_type,
        "path": path,
        "filename": ad.get("filename") or os.path.basename(path),
        "original_name": ad.get("original_name") or ad.get("filename") or os.path.basename(path),
        "mime_type": ad.get("mime_type") or "",
        "size": int(ad.get("size") or 0),
        "enabled": ad.get("enabled") is not False,
        "non_skippable": True,
        "created_at": ad.get("created_at") or datetime.utcnow().isoformat() + "Z",
    }


def _legacy_ads():
    _ensure_dir()
    found = []
    for filename in os.listdir(ADS_DIR):
        if filename == os.path.basename(MANIFEST_PATH):
            continue
        for ad_type in AD_TYPES:
            if filename.startswith(f"{ad_type}_ad."):
                found.append({
                    "id": f"legacy-{ad_type}-{os.path.splitext(filename)[1].lstrip('.') or 'file'}",
                    "type": ad_type,
                    "path": _public_path(filename),
                    "filename": filename,
                    "original_name": filename,
                    "mime_type": "",
                    "size": os.path.getsize(os.path.join(ADS_DIR, filename)),
                    "enabled": True,
                    "non_skippable": True,
                    "created_at": datetime.utcfromtimestamp(
                        os.path.getmtime(os.path.join(ADS_DIR, filename))
                    ).isoformat() + "Z",
                })
    return found


def read_ads(include_disabled=False):
    _ensure_dir()
    ads = []
    if os.path.isfile(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
            source = raw.get("ads", raw if isinstance(raw, list) else [])
            ads = [_normalize_ad(ad) for ad in source]
            ads = [ad for ad in ads if ad]
        except Exception:
            ads = []

    known_paths = {ad["path"] for ad in ads}
    for ad in _legacy_ads():
        if ad["path"] not in known_paths:
            ads.append(ad)

    ads.sort(key=lambda ad: ad.get("created_at", ""), reverse=True)
    if include_disabled:
        return ads
    return [ad for ad in ads if ad.get("enabled", True)]


def write_ads(ads):
    _ensure_dir()
    normalized = [_normalize_ad(ad) for ad in ads]
    normalized = [ad for ad in normalized if ad]
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump({"ads": normalized}, f, indent=2)
    return normalized


def add_uploaded_ad(ad_type, upload_file):
    if ad_type not in AD_TYPES:
        raise ValueError("Invalid ad type")
    _ensure_dir()
    ext = _safe_ext(upload_file.filename)
    ad_id = uuid.uuid4().hex[:10]
    filename = f"{ad_type}_{ad_id}.{ext}"
    path = os.path.join(ADS_DIR, filename)
    size = 0
    with open(path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    try:
        size = os.path.getsize(path)
    except OSError:
        size = 0

    ad = {
        "id": ad_id,
        "type": ad_type,
        "path": _public_path(filename),
        "filename": filename,
        "original_name": upload_file.filename or filename,
        "mime_type": upload_file.content_type or "",
        "size": size,
        "enabled": True,
        "non_skippable": True,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    ads = read_ads(include_disabled=True)
    ads.append(ad)
    write_ads(ads)
    return ad


def remove_ads(ad_type=None, ad_id=None):
    ads = read_ads(include_disabled=True)
    kept = []
    removed = []
    for ad in ads:
        match_id = ad_id and str(ad.get("id")) == str(ad_id)
        match_type = ad_type and ad.get("type") == ad_type
        if match_id or (not ad_id and match_type):
            removed.append(ad)
        else:
            kept.append(ad)

    write_ads(kept)
    for ad in removed:
        filename = os.path.basename(ad.get("path", ""))
        if not filename:
            continue
        file_path = os.path.join(ADS_DIR, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
    return removed


def set_ad_enabled(ad_id, enabled):
    ads = read_ads(include_disabled=True)
    updated = None
    for ad in ads:
        if str(ad.get("id")) == str(ad_id):
            ad["enabled"] = bool(enabled)
            updated = ad
            break
    if updated:
        write_ads(ads)
    return updated


def grouped_ads(include_disabled=False):
    ads = read_ads(include_disabled=include_disabled)
    grouped = {ad_type: [] for ad_type in AD_TYPES}
    for ad in ads:
        grouped.setdefault(ad["type"], []).append(ad)
    return grouped
