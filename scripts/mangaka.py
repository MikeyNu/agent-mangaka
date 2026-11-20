#!/usr/bin/env python3
"""Validate story continuity, compile panel packets, and draw planning maps.

This is a consistency checker, not a visual-quality classifier. It never calls
an image provider, uploads a reference, or marks artwork accepted.
"""
from __future__ import annotations

import argparse
import collections
import copy
import hashlib
import html
import json
import math
from pathlib import Path
import sys


class InvalidProject(ValueError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def file_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text_value(value):
    return isinstance(value, str) and bool(value.strip())


def finite_number(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def vector(value, length=3):
    return (isinstance(value, list) and len(value) == length and
            all(finite_number(x) for x in value))


def subtract(a, b):
    return [x-y for x, y in zip(a, b)]


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def cross(a, b):
    return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]


def unit(v):
    norm = math.hypot(*v)
    if not math.isfinite(norm) or norm < 1e-8:
        raise ValueError("zero-length vector")
    return [x/norm for x in v]


def camera_basis(camera):
    """Roll rotates the view basis only. It never rotates world gravity."""
    forward = unit(subtract(camera["target"], camera["position"]))
    right = unit(cross(forward, camera.get("up", [0, 0, 1])))
    up = unit(cross(right, forward))
    angle = math.radians(camera.get("roll_degrees", 0) % 360)
    cosine, sine = math.cos(angle), math.sin(angle)
    # Positive roll rotates the camera's right basis toward its unrolled up.
    return (forward, [cosine*r+sine*u for r, u in zip(right, up)],
            [cosine*u-sine*r for r, u in zip(right, up)])


def projection(camera, point):
    forward, right, up = camera_basis(camera)
    relative = subtract(point, camera["position"])
    depth = dot(relative, forward)
    if not math.isfinite(depth) or depth <= 1e-8:
        raise ValueError("subject is on or behind the camera plane")
    projected = [dot(relative, right)/depth, dot(relative, up)/depth, depth]
    if not all(finite_number(v) for v in projected):
        raise ValueError("projection exceeds finite numeric range")
    return projected


def axis_side(axis, camera):
    a, b = axis["a"], axis["b"]
    area = (b[0]-a[0])*(camera[1]-a[1]) - (b[1]-a[1])*(camera[0]-a[0])
    if not finite_number(area):
        raise ValueError("interaction-axis computation exceeds finite numeric range")
    return 0 if abs(area) < 1e-7 else (1 if area > 0 else -1)


def resolve_character(project, name):
    """Names can be ambiguous. Return one stable ID or fail without guessing."""
    if not text_value(name) or not isinstance(project, dict) or not isinstance(project.get("characters"), list):
        raise InvalidProject("Character resolution needs a nonempty name and character records")
    characters = project["characters"]
    for char in characters:
        if (not isinstance(char, dict) or not text_value(char.get("id")) or
                not text_value(char.get("name")) or not isinstance(char.get("aliases", []), list) or
                not all(text_value(a) for a in char.get("aliases", []))):
            raise InvalidProject("Malformed character name, ID, or alias list")
    exact = [c["id"] for c in characters if c["id"] == name]
    if len(exact) == 1:
        return exact[0]
    needle = name.casefold().strip()
    matches = [c["id"] for c in characters if needle in
               {s.casefold().strip() for s in [c["id"], c["name"], *c.get("aliases", [])]}]
    if len(matches) != 1:
        raise InvalidProject(f"Character name {name!r} resolves to {len(matches)} identities: {matches}")
    return matches[0]


def panel_dependency_digest(project, panel):
    """Hash canon plus earlier causal context, never a claim of visual fidelity.

    All earlier panels in the same scene are conservative dependencies. Explicit
    depends_on links add earlier panels from other scenes and their ancestors.
    Changing a dependency's approved artwork also invalidates later review.
    """
    panels = project["panels"]
    indices = {p["id"]: i for i, p in enumerate(panels)}
    if panel["id"] not in indices:
        raise InvalidProject("Dependency panel is not in the project")
    included, pending = set(), [panel["id"]]
    while pending:
        pid = pending.pop()
        if pid in included:
            continue
        if pid not in indices:
            raise InvalidProject(f"Unknown panel dependency {pid}")
        current = panels[indices[pid]]
        included.add(pid)
        links = list(current.get("depends_on", []))
        links.extend(p["id"] for p in panels[:indices[pid]] if p["scene_id"] == current["scene_id"])
        if any(link not in indices or indices[link] >= indices[pid] for link in links):
            raise InvalidProject("Panel dependencies must point to earlier panels")
        pending.extend(links)
    selected = [p for p in panels if p["id"] in included]
    needed = {rid for p in selected for rid in p.get("reference_ids", [])}
    line_ids = {did for p in selected for did in p.get("dialogue_ids", [])}
    scene_ids = {p["scene_id"] for p in selected}
    scenes = [s for s in project["scenes"] if s["id"] in scene_ids]
    env_ids = {s["environment_id"] for s in scenes}
    direction = [{k: v for k, v in p.items() if k not in {"qa", "status", "art"}} for p in selected]
    approved_art = {p["id"]: p.get("qa", {}).get("art_sha256") for p in selected
                    if p["id"] != panel["id"] and p.get("status") == "accepted"}
    return digest({"project": project["project"], "causal_direction": direction,
                   "approved_dependency_art": approved_art, "scenes": scenes,
                   "environments": [e for e in project["environments"] if e["id"] in env_ids],
                   "characters": project["characters"],
                   "references": [r for r in project["references"] if r["id"] in needed],
                   "dialogue": [d for d in project["dialogue"] if d["id"] in line_ids]})


HELD_MODES = ("symbolic", "portrait", "imagined", "replay")
REPRESENTATION_MODES = ("normal", "chibi", "temporal_montage", *HELD_MODES)


def represented_characters(panel):
    """Canonical identities visible in any form, separate from physical bodies."""
    return list(dict.fromkeys(panel.get("participants", []) + panel.get("represented_characters", []) +
                              [i["character_id"] for i in panel.get("instances", [])]))


def _shape_errors(project, tables):
    """Validate consumed field types before semantic comparisons or hashing.

    Extra project-specific metadata may be finite JSON. It is retained, but its
    visual or narrative truth is never established by this validator.
    """
    errors = []
    chars = tables["characters"]

    def error(code, location, message):
        errors.append({"code": code, "location": location, "message": message})

    def strings(value, location, code, unique=False, nonempty=False):
        if not isinstance(value, list) or not all(text_value(x) for x in value):
            error(code, location, "Expected an array of nonempty strings")
            return False
        if nonempty and not value:
            error(code, location, "At least one value is required")
        if unique and len(value) != len(set(value)):
            error(code, location, "Duplicate entries are not allowed")
        return True

    def text_fields(record, names, location, code, required=False):
        for name in names:
            if (required or name in record) and not text_value(record.get(name)):
                error(code, location+"."+name, "Expected a nonempty string")

    def axis(value, location):
        if (not isinstance(value, dict) or not vector(value.get("a"), 2) or
                not vector(value.get("b"), 2) or value["a"] == value["b"]):
            error("AXIS", location, "Axis requires distinct finite XY endpoints")

    def provenance(value, location):
        if not isinstance(value, dict):
            error("PROVENANCE", location, "Narrative provenance must be an object")
            return
        if value.get("source_kind") not in ("script", "narration", "in_world_document", "character_account",
                                            "memory", "dream", "vision", "symbolic"):
            error("PROVENANCE", location, "Declare the narrative source kind")
        if value.get("truth_status") not in ("confirmed", "reported", "contested", "unreliable", "imagined", "unknown"):
            error("PROVENANCE", location, "Declare the account's truth status, separate from its appearance")
        text_fields(value, ("source_id",), location, "PROVENANCE", required=True)
        text_fields(value, ("notes",), location, "PROVENANCE")
        if (value.get("source_kind") == "character_account" and
                (not isinstance(value.get("source_id"), str) or value["source_id"] not in chars)):
            error("PROVENANCE_SOURCE", location, "Character account source_id must be a canonical character ID")

    def state(value, location):
        if not isinstance(value, dict):
            error("STATE_SHAPE", location, "Tracked state must be an object keyed by canonical character IDs")
            return
        for cid, item in value.items():
            loc = location+"."+str(cid)
            if cid not in chars:
                error("STATE_ENTITY", loc, "Unknown character in physical state")
            if not isinstance(item, dict):
                error("STATE_SHAPE", loc, "Every character state must be an object")
                continue
            if not vector(item.get("position")):
                error("POSITION", loc, "Physical state needs a finite XYZ position")
            if "facing" in item and not (vector(item["facing"], 2) or vector(item["facing"], 3)):
                error("STATE_SHAPE", loc, "Facing must be a finite XY or XYZ vector")
            if "facing" in item and isinstance(item["facing"], list) and not any(item["facing"]):
                error("STATE_SHAPE", loc, "Facing cannot be a zero vector")
            text_fields(item, ("costume",), loc, "STATE_SHAPE")
            if "held" in item and (not isinstance(item["held"], dict) or
                                   not all(text_value(k) and (v is None or text_value(v)) for k, v in item["held"].items())):
                error("STATE_SHAPE", loc, "Held items map named slots to prop IDs or null")
            if "injuries" in item:
                strings(item["injuries"], loc+".injuries", "STATE_SHAPE")

    def lights(value, location, require_domain=False):
        if not isinstance(value, list) or not value:
            error("LIGHTING", location, "Use a nonempty lighting array, including an explicit unlit record if appropriate")
            return
        seen = set()
        for item in value:
            if not isinstance(item, dict):
                error("LIGHTING", location, "Each light must be an object")
                continue
            text_fields(item, ("id", "kind"), location, "LIGHTING", required=True)
            if text_value(item.get("id")):
                if item["id"] in seen:
                    error("LIGHTING", location, "Duplicate light ID")
                seen.add(item["id"])
            domain = item.get("domain", None if require_domain else "environmental")
            if domain not in ("environmental", "event", "expressive"):
                error("LIGHTING_DOMAIN", location, "Declare environmental, event, or expressive lighting")
            if domain == "event" and not text_value(item.get("cause")):
                error("LIGHTING_EVENT", location, "Event lighting needs a causal event")
            if domain == "expressive" and not text_value(item.get("purpose")):
                error("LIGHTING_EXPRESSION", location, "Expressive lighting needs a graphic purpose, not an invented physical source")
            for key in ("position", "direction_from"):
                if key in item and not vector(item[key]):
                    error("LIGHTING", location+"."+key, "Expected finite XYZ coordinates")
            for key in ("quality", "color", "cause", "purpose"):
                text_fields(item, (key,), location, "LIGHTING")
            if "intensity" in item and (not finite_number(item["intensity"]) or item["intensity"] < 0):
                error("LIGHTING", location, "Intensity must be finite and nonnegative")

    meta = project["project"]
    text_fields(meta, ("id", "setting", "style"), "project", "PROJECT_CONTRACT", required=True)
    text_fields(meta, ("title",), "project", "PROJECT_CONTRACT")
    if "excluded_motifs" in meta:
        strings(meta["excluded_motifs"], "project.excluded_motifs", "PROJECT_CONTRACT")
    for rid, ref in tables["references"].items():
        text_fields(ref, ("path", "description", "role"), rid, "REFERENCE_BINDING", required=True)
        text_fields(ref, ("entity_id", "inspection"), rid, "REFERENCE_BINDING")
        if "sha256" in ref and (not isinstance(ref["sha256"], str) or len(ref["sha256"]) != 64 or
                                any(c not in "0123456789abcdef" for c in ref["sha256"])):
            error("REFERENCE_HASH", rid, "sha256 must be a lowercase 64-character hexadecimal digest")
    for cid, char in chars.items():
        text_fields(char, ("name",), cid, "CHARACTER_CANON", required=True)
        strings(char.get("aliases", []), cid+".aliases", "CHARACTER_CANON")
        depiction = char.get("depiction", "visual")
        if depiction not in ("visual", "voice_only"):
            error("CHARACTER_DEPICTION", cid, "Choose visual or voice_only")
        strings(char.get("invariants", []), cid+".invariants", "CHARACTER_CANON",
                nonempty=depiction != "voice_only")
    for eid, env in tables["environments"].items():
        landmarks = env.get("landmarks", [])
        if not isinstance(landmarks, list):
            error("LANDMARK", eid, "Landmarks must be an array")
        else:
            for item in landmarks:
                if not isinstance(item, dict) or not text_value(item.get("id")) or not vector(item.get("position")):
                    error("LANDMARK", eid, "Landmarks need string IDs and finite XYZ positions")
                elif "label" in item and not isinstance(item["label"], str):
                    error("LANDMARK", eid, "Landmark label must be a string")
        lights(env.get("lighting"), eid+".lighting")
    for sid, scene in tables["scenes"].items():
        text_fields(scene, ("environment_id",), sid, "SCENE_ENVIRONMENT", required=True)
        state(scene.get("initial_state"), sid+".initial_state")
        if "axis" in scene:
            axis(scene["axis"], sid+".axis")
        if "gravity" in scene and not vector(scene["gravity"]):
            error("GRAVITY", sid, "World gravity is a finite XYZ vector, separate from camera roll")
        if "narrative_provenance" in scene:
            provenance(scene["narrative_provenance"], sid+".narrative_provenance")
    for did, line in tables["dialogue"].items():
        text_fields(line, ("kind", "scene_id"), did, "DIALOGUE_STRUCTURE", required=True)
        text_fields(line, ("speaker_id", "narrator_id", "source_id"), did, "DIALOGUE_STRUCTURE")
        if "narrative_provenance" in line:
            provenance(line["narrative_provenance"], did+".narrative_provenance")
    for pid, panel in tables["panels"].items():
        text_fields(panel, ("scene_id", "beat", "moment", "story_intent"), pid, "PANEL_DIRECTION", required=True)
        text_fields(panel, ("orientation_bridge", "visual_constraints", "art"), pid, "PANEL_DIRECTION")
        for key, code in (("participants", "PARTICIPANTS"), ("offscreen_speakers", "OFFSCREEN_SOURCE"),
                          ("represented_characters", "REPRESENTED_CHARACTERS"), ("reference_ids", "PANEL_REFERENCES"),
                          ("visible_landmarks", "LANDMARK_ID"), ("screen_order", "SCREEN_ORDER"), ("depends_on", "DEPENDENCY")):
            strings(panel.get(key, []), pid+"."+key, code, unique=True)
        # Duplicate utterances remain a LINE_COVERAGE error in the semantic pass.
        strings(panel.get("dialogue_ids", []), pid+".dialogue_ids", "DIALOGUE_STRUCTURE")
        mode = panel.get("representation_mode", "normal")
        if mode not in REPRESENTATION_MODES:
            error("REPRESENTATION_MODE", pid, "Use normal, chibi, temporal_montage, symbolic, portrait, imagined, or replay")
        if panel.get("continuity_mode", "hold" if mode in HELD_MODES else "advance") not in ("hold", "advance"):
            error("CONTINUITY_MODE", pid, "Choose hold or advance")
        if panel.get("status", "planned") not in ("planned", "candidate", "in_review", "accepted", "rejected", "invalidated"):
            error("PANEL_STATUS", pid, "Unknown panel lifecycle status")
        composition = panel.get("composition")
        if not isinstance(composition, dict):
            error("PANEL_DIRECTION", pid+".composition", "Composition must be an object")
        else:
            text_fields(composition, ("aspect_ratio", "focal_point", "crop_safety"), pid+".composition", "COMPOSITION")
            zones = composition.get("lettering_zones", [])
            if not isinstance(zones, list) or any(not vector(z, 4) or z[0] < 0 or z[1] < 0 or
                   z[2] <= 0 or z[3] <= 0 or z[0]+z[2] > 1 or z[1]+z[3] > 1 for z in zones):
                error("COMPOSITION", pid, "Lettering zones are normalized [x,y,width,height] rectangles inside the panel")
        acting = panel.get("acting")
        if not isinstance(acting, dict):
            error("ACTING", pid, "Acting must be keyed by canonical character IDs")
        else:
            for cid, direction in acting.items():
                if cid not in chars or not isinstance(direction, dict):
                    error("ACTING", pid, "Acting entry needs a known character and an object")
                    continue
                text_fields(direction, ("internal_emotion", "display", "intention", "pose"),
                            pid+".acting."+cid, "ACTING", required=True)
        state(panel.get("state"), pid+".state")
        changes = panel.get("changes", [])
        if not isinstance(changes, list):
            error("CHANGE_STRUCTURE", pid, "Changes must be an array")
        else:
            for change in changes:
                if not isinstance(change, dict):
                    error("CHANGE_STRUCTURE", pid, "Each change must be an object")
                    continue
                text_fields(change, ("entity_id", "field", "cause"), pid, "CHANGE_STRUCTURE", required=True)
                if "before" not in change or "after" not in change:
                    error("CHANGE_STRUCTURE", pid, "A transition requires explicit before and after values")
        camera = panel.get("camera")
        if (not isinstance(camera, dict) or not vector(camera.get("position")) or not vector(camera.get("target"))):
            error("CAMERA", pid, "Camera requires finite XYZ position and target")
        else:
            if "up" in camera and not vector(camera["up"]):
                error("CAMERA", pid, "Camera up must be a finite XYZ vector")
            if "roll_degrees" in camera and not finite_number(camera["roll_degrees"]):
                error("CAMERA", pid, "Camera roll_degrees must be finite")
            if "fov_degrees" in camera and (not finite_number(camera["fov_degrees"]) or not 0 < camera["fov_degrees"] < 180):
                error("CAMERA", pid, "Field of view must be between zero and 180 degrees")
            if "focal_length_mm" in camera and (not finite_number(camera["focal_length_mm"]) or camera["focal_length_mm"] <= 0):
                error("CAMERA", pid, "Focal-length cue must be finite and positive")
        if "axis" in panel:
            axis(panel["axis"], pid+".axis")
        if "lighting" in panel:
            lights(panel["lighting"], pid+".lighting", require_domain=True)
        if "narrative_provenance" in panel:
            provenance(panel["narrative_provenance"], pid+".narrative_provenance")
        instances = panel.get("instances", [])
        if not isinstance(instances, list):
            error("INSTANCE_STRUCTURE", pid, "Rendered instances must be an array")
        else:
            for item in instances:
                if not isinstance(item, dict):
                    error("INSTANCE_STRUCTURE", pid, "Rendered instances must be objects")
                    continue
                text_fields(item, ("id", "character_id", "kind"), pid, "INSTANCE_STRUCTURE", required=True)
                text_fields(item, ("purpose",), pid, "INSTANCE_STRUCTURE")
        qa = panel.get("qa", {})
        if not isinstance(qa, dict) or not isinstance(qa.get("checks", {}), dict):
            error("QA_STRUCTURE", pid, "QA and QA checks must be objects")
        else:
            text_fields(qa, ("reviewer", "dependency_sha256", "art_sha256"), pid+".qa", "QA_STRUCTURE")
            for key in ("dependency_sha256", "art_sha256"):
                if key in qa and (not isinstance(qa[key], str) or len(qa[key]) != 64 or
                                  any(c not in "0123456789abcdef" for c in qa[key])):
                    error("QA_STRUCTURE", pid+".qa."+key, "Expected a lowercase SHA-256 digest")
            if "evidence" in qa:
                evidence = qa["evidence"]
                if not (text_value(evidence) or (isinstance(evidence, list) and evidence and all(text_value(v) for v in evidence)) or
                        (isinstance(evidence, dict) and evidence and all(text_value(k) and text_value(v) for k, v in evidence.items()))):
                    error("QA_EVIDENCE", pid, "Evidence must contain specific written observations")
    try:
        json.dumps(project, allow_nan=False, sort_keys=True)
    except (ValueError, TypeError, OverflowError, RecursionError) as exc:
        error("JSON_VALUE", "$", "Manifest must contain finite JSON values: "+str(exc))
    return errors


def validate(project, root=None, check_files=False):
    errors = []

    def error(code, location, message):
        errors.append({"code": code, "location": location, "message": message})

    if not isinstance(project, dict):
        return [{"code": "STRUCTURE", "location": "$", "message": "Project must be an object"}]
    required = {"project": dict, "references": list, "characters": list,
                "environments": list, "scenes": list, "dialogue": list, "panels": list}
    for key, kind in required.items():
        if not isinstance(project.get(key), kind):
            error("STRUCTURE", key, f"Expected {kind.__name__}")
    if type(project.get("version")) is not int or project["version"] != 1:
        error("VERSION", "version", "Supported manifest version is 1")
    if errors:
        return errors

    tables = {}
    for key in required:
        if key == "project":
            continue
        table = {}
        for index, item in enumerate(project[key]):
            if not isinstance(item, dict) or not text_value(item.get("id")):
                error("ID", f"{key}[{index}]", "Every record needs a nonempty stable string ID")
                continue
            if item["id"] in table:
                error("DUPLICATE_ID", key, item["id"])
            table[item["id"]] = item
        tables[key] = table
    if errors:
        return errors

    errors.extend(_shape_errors(project, tables))
    if errors:
        return errors

    meta = project["project"]
    if meta.get("format") not in ("page", "scroll"):
        error("FORMAT", "project.format", "Choose page or scroll")
    if meta.get("reading_direction") not in ("ltr", "rtl"):
        error("READING_DIRECTION", "project.reading_direction", "Choose ltr or rtl explicitly")
    for key in ("id", "setting", "style"):
        if not meta.get(key):
            error("PROJECT_CONTRACT", "project."+key, "Record this before panel generation")
    chars, refs, envs, scenes, dialogue = [tables[k] for k in
                                         ("characters", "references", "environments", "scenes", "dialogue")]
    for rid, ref in refs.items():
        if ref.get("role") not in {"character", "environment", "style", "blocking", "balloon", "prop"}:
            error("REFERENCE_ROLE", rid, "Declare what this image is evidence for")
        if not ref.get("path") or not ref.get("description"):
            error("REFERENCE_BINDING", rid, "Reference needs path and description")
        if ref.get("role") == "character" and ref.get("entity_id") not in chars:
            error("REFERENCE_ENTITY", rid, "Unknown character for identity reference")
        if ref.get("role") == "environment" and ref.get("entity_id") not in envs:
            error("REFERENCE_ENTITY", rid, "Unknown environment for reference")
        if check_files and ref.get("path"):
            path = Path(root or ".") / ref["path"]
            if not path.is_file():
                error("REFERENCE_MISSING", rid, str(path))
            elif not ref.get("sha256") or file_digest(path) != ref["sha256"]:
                error("REFERENCE_CHANGED", rid, "Record and inspect the current asset hash")
            if ref.get("inspection") != "reviewed":
                error("REFERENCE_UNINSPECTED", rid, "Visual inspection must be recorded")
    for cid, char in chars.items():
        voice_only = char.get("depiction") == "voice_only"
        if not char.get("name") or (not voice_only and not char.get("invariants")):
            error("CHARACTER_CANON", cid, "Name and identifying invariants are required")
        if not voice_only and not any(r.get("role") == "character" and r.get("entity_id") == cid for r in refs.values()):
            error("CHARACTER_REFERENCE", cid, "No bound character sheet")
    for eid, env in envs.items():
        landmarks = env.get("landmarks", [])
        seen = set()
        for landmark in landmarks:
            if not isinstance(landmark, dict) or not landmark.get("id") or not vector(landmark.get("position")):
                error("LANDMARK", eid, "Landmarks need stable IDs and finite XYZ positions")
                continue
            if landmark["id"] in seen:
                error("DUPLICATE_LANDMARK", eid, landmark["id"])
            seen.add(landmark["id"])
        if not env.get("lighting"):
            error("LIGHTING", eid, "Record world-space sources or an explicit unlit setup")
    for sid, scene in scenes.items():
        if scene.get("environment_id") not in envs:
            error("SCENE_ENVIRONMENT", sid, "Unknown environment")
        if not isinstance(scene.get("initial_state"), dict):
            error("SCENE_STATE", sid, "Initial tracked state is required")
    for did, line in dialogue.items():
        if not isinstance(line.get("text"), str) or not line["text"]:
            error("DIALOGUE_TEXT", did, "Store exact nonempty script text")
        if line.get("kind") not in {"speech", "thought", "caption", "offscreen", "sfx"}:
            error("DIALOGUE_KIND", did, "Unknown delivery kind")
        if line.get("kind") in {"speech", "thought", "offscreen"} and line.get("speaker_id") not in chars:
            error("SPEAKER", did, "Resolve the speaker to a canonical character ID")
        if line.get("kind") in {"caption", "sfx"} and "speaker_id" in line:
            error("DIALOGUE_ATTRIBUTION", did, "Use narrator_id for captions or source_id for SFX, without fabricating a speaker")
        if line.get("kind") != "caption" and "narrator_id" in line:
            error("DIALOGUE_ATTRIBUTION", did, "narrator_id belongs only to caption records")
        if line.get("kind") not in {"sfx", "offscreen"} and "source_id" in line:
            error("DIALOGUE_ATTRIBUTION", did, "source_id belongs to SFX or offscreen device/source records")
        if line.get("scene_id") not in scenes:
            error("DIALOGUE_SCENE", did, "Dialogue needs a valid scene")

    if errors:
        return errors
    assignments = collections.Counter()
    previous = {}
    orientations = {}
    panel_indices = {p["id"]: n for n, p in enumerate(project["panels"])}
    for panel in project["panels"]:
        pid = panel["id"]
        sid = panel.get("scene_id")
        if sid not in scenes:
            error("PANEL_SCENE", pid, "Unknown scene")
            continue
        scene, env = scenes[sid], envs[scenes[sid]["environment_id"]]
        participants = panel.get("participants", [])
        offscreen = panel.get("offscreen_speakers", [])
        represented = represented_characters(panel)
        if not isinstance(participants, list) or len(set(participants)) != len(participants):
            error("PARTICIPANTS", pid, "List each physical participant once")
            continue
        if any(c not in chars for c in represented + offscreen):
            error("PANEL_CHARACTER", pid, "Unknown physical, represented, or offscreen character")
        for dependency in panel.get("depends_on", []):
            if dependency not in panel_indices or panel_indices[dependency] >= panel_indices[pid]:
                error("DEPENDENCY", pid, "Explicit dependencies must name earlier panels; future links and cycles are invalid")
        for key in ("beat", "moment", "story_intent", "composition", "acting"):
            if key not in panel or panel[key] in (None, ""):
                error("PANEL_DIRECTION", pid, f"Missing {key}")
        reference_ids = panel.get("reference_ids", [])
        if not isinstance(reference_ids, list) or any(r not in refs for r in reference_ids):
            error("PANEL_REFERENCES", pid, "Unknown or invalid reference list")
            continue
        for cid in represented:
            if cid in chars and chars[cid].get("depiction") == "voice_only":
                error("VOICE_ONLY_VISUAL", pid, f"{cid} needs a visual design and depiction revision before being drawn")
            if not any(refs[r].get("role") == "character" and refs[r].get("entity_id") == cid for r in reference_ids):
                error("IDENTITY_ANCHOR", pid, f"Missing original identity reference for {cid}")
        for cid in participants:
            if cid not in panel.get("acting", {}):
                error("ACTING", pid, f"Missing acting direction for {cid}")
        if not any(refs[r].get("role") == "environment" and refs[r].get("entity_id") == env["id"] for r in reference_ids):
            error("ENVIRONMENT_ANCHOR", pid, "Include this scene's environment reference")
        if not any(refs[r].get("role") == "style" for r in reference_ids):
            error("STYLE_ANCHOR", pid, "Include an approved drawing-style anchor")
        for did in panel.get("dialogue_ids", []):
            assignments[did] += 1
            if did not in dialogue:
                error("UNKNOWN_LINE", pid, did)
                continue
            line = dialogue[did]
            if line["scene_id"] != sid:
                error("LINE_SCENE", pid, f"{did} belongs to another scene")
            if line["kind"] in {"speech", "thought"} and line["speaker_id"] not in represented:
                error("SPEAKER_NOT_PRESENT", pid, f"{did}: speaker is not a represented participant")
            if line["kind"] == "offscreen" and line["speaker_id"] not in offscreen:
                error("OFFSCREEN_SOURCE", pid, f"{did}: declare the offscreen speaker")

        state = panel.get("state")
        if not isinstance(state, dict):
            error("PANEL_STATE", pid, "Full tracked state required")
            continue
        prior_panel = previous.get(sid)
        before = prior_panel["state"] if prior_panel else scene["initial_state"]
        changes = panel.get("changes", [])
        observed = []
        if any(cid not in state for cid in participants):
            error("STATE_TRACKING", pid, "Every physical participant must be present in the complete physical state")
        for cid in set(before) | set(state):
            if cid not in chars:
                error("STATE_ENTITY", pid, f"Unknown character {cid}")
                continue
            if cid not in state or cid not in before:
                error("STATE_TRACKING", pid, f"Keep {cid} in the scene's full state, including when offscreen")
                continue
            if not isinstance(state[cid], dict) or not vector(state[cid].get("position")):
                error("POSITION", pid, f"{cid} needs a finite XYZ position")
                continue
            for field in set(before[cid]) | set(state[cid]):
                old, new = before[cid].get(field), state[cid].get(field)
                if field in before[cid] and field in state[cid] and old == new:
                    continue
                observed.append((cid, field, old, new))
                if not any(c.get("entity_id") == cid and c.get("field") == field and
                           c.get("before") == old and c.get("after") == new and
                           isinstance(c.get("cause"), str) and c["cause"].strip() for c in changes):
                    error("UNEXPLAINED_CHANGE", pid, f"{cid}.{field} changed without a matching causal transition")
        for c in changes:
            if (c.get("entity_id"), c.get("field"), c.get("before"), c.get("after")) not in observed:
                error("STALE_CHANGE", pid, "Transition does not match the previous and current state")
        changed_keys = [(c["entity_id"], c["field"]) for c in changes]
        if len(changed_keys) != len(set(changed_keys)):
            error("DUPLICATE_CHANGE", pid, "Record each field transition once; split intermediate actions into separate beats")
        mode = panel.get("representation_mode", "normal")
        held = mode in HELD_MODES or panel.get("continuity_mode", "advance") == "hold"
        if mode in HELD_MODES and panel.get("continuity_mode") == "advance":
            error("SYMBOLIC_STATE_CHANGE", pid, "Symbolic, portrait, imagined, and replay panels must hold the scene's physical state")
        if held and observed:
            error("SYMBOLIC_STATE_CHANGE", pid, "A held or imagined insert cannot mutate physical state")

        camera = panel.get("camera", {})
        if not isinstance(camera, dict) or not vector(camera.get("position")) or not vector(camera.get("target")):
            error("CAMERA", pid, "Camera needs finite XYZ position and target")
        else:
            try:
                camera_basis(camera)
                if participants and mode not in HELD_MODES:
                    locations = {c: projection(camera, state[c]["position"])[0] for c in participants}
                    expected = sorted(participants, key=lambda c: locations[c])
                    order = panel.get("screen_order")
                    if not isinstance(order, list) or set(order) != set(participants):
                        error("SCREEN_ORDER", pid, "Screen order must contain every physical participant once")
                    # An exact overlap has no uniquely determined left-right order.
                    separated = all(abs(locations[a]-locations[b]) > 1e-5 for a, b in zip(expected, expected[1:]))
                    if separated and order != expected:
                        error("SCREEN_ORDER", pid, f"Projected screen-left to right order is {expected}")
                axis = panel.get("axis", scene.get("axis"))
                if len(participants) > 1 and not axis and mode not in HELD_MODES:
                    error("AXIS", pid, "Multi-character blocking needs an interaction axis")
                if axis and mode not in HELD_MODES:
                    if not vector(axis.get("a"), 2) or not vector(axis.get("b"), 2) or axis["a"] == axis["b"]:
                        raise ValueError("invalid interaction axis")
                    # Endpoint reversal is the same physical line, not an axis crossing.
                    endpoints = sorted((axis["a"], axis["b"]))
                    normalized_axis = {"a": endpoints[0], "b": endpoints[1]}
                    side = axis_side(normalized_axis, camera["position"])
                    if sid in orientations:
                        old_axis, old_side = orientations[sid]
                        if (normalized_axis != old_axis or side*old_side == -1) and not panel.get("orientation_bridge"):
                            error("AXIS_CROSSING", pid, "Record the visible reorientation device")
                    # An unannotated on-axis shot must not erase the preceding side.
                    if side or panel.get("orientation_bridge") or sid not in orientations:
                        orientations[sid] = (normalized_axis, side)
                valid_landmarks = {l["id"] for l in env.get("landmarks", [])}
                if any(l not in valid_landmarks for l in panel.get("visible_landmarks", [])):
                    error("LANDMARK_ID", pid, "Unknown background landmark")
            except (ValueError, KeyError, TypeError) as exc:
                error("GEOMETRY", pid, str(exc))

        instances = panel.get("instances", [])
        instance_ids = [i.get("id") for i in instances]
        if len(instance_ids) != len(set(instance_ids)):
            error("INSTANCE_ID", pid, "Rendered instance IDs must be unique")
        for instance in instances:
            if instance.get("character_id") not in chars:
                error("INSTANCE_CHARACTER", pid, "Rendered instance must bind to a canonical character")
            if instance.get("kind") == "physical" and instance["character_id"] not in participants:
                error("INSTANCE_CHARACTER", pid, "Physical instances must bind to physical participants")
            if instance.get("kind") not in {"physical", "temporal", "imagined", "chibi", "portrait", "symbolic"}:
                error("INSTANCE_KIND", pid, "Declare physical, temporal, imagined, chibi, portrait, or symbolic")
            if instance.get("kind") != "physical" and not instance.get("purpose"):
                error("INSTANCE_PURPOSE", pid, "Explain the temporal or symbolic depiction")
        for cid in participants:
            if sum(i.get("character_id") == cid and i.get("kind") == "physical" for i in instances) > 1:
                error("DUPLICATED_BODY", pid, f"{cid} has more than one physical body")

        if panel.get("status") == "accepted":
            qa = panel.get("qa", {})
            gates = ("identity", "narrative", "space", "acting", "anatomy", "style", "composition")
            if any(qa.get("checks", {}).get(g) != "pass" for g in gates):
                error("QA_GATE", pid, "Every required visual gate needs an explicit pass")
            if not qa.get("reviewer") or not qa.get("evidence") or not qa.get("art_sha256") or not panel.get("art"):
                error("QA_EVIDENCE", pid, "Record the artifact path and hash, reviewer, inspected views/crops, and observations")
            try:
                current_digest = panel_dependency_digest(project, panel)
            except (InvalidProject, KeyError, TypeError) as exc:
                error("DEPENDENCY", pid, str(exc))
                current_digest = None
            if current_digest is None or qa.get("dependency_sha256") != current_digest:
                error("STALE_ACCEPTANCE", pid, "Canon, script, or direction changed after review")
            if check_files:
                art = Path(root or ".") / panel.get("art", "")
                if not art.is_file() or file_digest(art) != qa.get("art_sha256"):
                    error("ART_CHANGED", pid, "Accepted artwork is missing or its bytes changed")
        previous[sid] = panel

    for did in dialogue:
        if assignments[did] != 1:
            error("LINE_COVERAGE", did, f"Expected one panel assignment, found {assignments[did]}")
    return errors


def packet(project, panel_id):
    errors = validate(project)
    if errors:
        raise InvalidProject(json.dumps(errors, ensure_ascii=False, indent=2))
    panel = next((p for p in project["panels"] if p["id"] == panel_id), None)
    if panel is None:
        raise InvalidProject(f"Unknown panel {panel_id}")
    refs = {r["id"]: r for r in project["references"]}
    lines = {d["id"]: d for d in project["dialogue"]}
    scene = next(s for s in project["scenes"] if s["id"] == panel["scene_id"])
    env = next(e for e in project["environments"] if e["id"] == scene["environment_id"])
    characters = {c["id"]: c for c in project["characters"]}
    reference_map = [{**refs[r], "input": n+1} for n, r in enumerate(panel["reference_ids"])]
    chunks = ["OUTPUT\nOne unlettered hand-drawn 2D comic panel. No page grid or baked-in lettering.",
              "PROJECT\n"+json.dumps(project["project"], ensure_ascii=False),
              "REFERENCE BINDING\n"+"\n".join(f"Image {r['input']}: {r['id']}, {r['role']}, {r.get('entity_id', 'project')}. {r['description']}" for r in reference_map),
              f"STORY MOMENT\n{panel['moment']}\nReader purpose: {panel['story_intent']}\nBeat: {panel['beat']}",
              "CHARACTER LOCKS\n"+json.dumps([characters[c] for c in represented_characters(panel)], ensure_ascii=False),
              "WORLD STATE\n"+json.dumps(panel["state"], ensure_ascii=False),
              "ENVIRONMENT AND LIGHT\n"+json.dumps({"environment": env, "panel_lighting": panel.get("lighting", []),
                  "world_gravity": scene.get("gravity", [0, 0, -1])}, ensure_ascii=False),
              "NARRATIVE PROVENANCE\n"+json.dumps(panel.get("narrative_provenance", scene.get("narrative_provenance", {})), ensure_ascii=False),
              "CAMERA AND VISIBLE PROJECTION\n"+json.dumps({k: panel.get(k) for k in ["camera", "screen_order", "visible_landmarks", "composition"]}, ensure_ascii=False),
              "ACTING\n"+json.dumps(panel["acting"], ensure_ascii=False),
              "REPRESENTATION\n"+json.dumps({"mode": panel.get("representation_mode", "normal"),
                  "physical_participants": panel.get("participants", []),
                  "represented_characters": represented_characters(panel),
                  "continuity_mode": panel.get("continuity_mode", "hold" if panel.get("representation_mode") in HELD_MODES else "advance"),
                  "instances": panel.get("instances", [])}, ensure_ascii=False),
              "VISIBLE CONSTRAINTS\n"+panel.get("visual_constraints", "Translate the map into the declared screen order and visible landmarks. Do not relocate people to preserve a background."),
              "EXCLUSIONS\nNo readable text, speech balloons, captions, panel borders, photographic or 3D-render finish. Preserve anatomical sides. Do not merge identities or transfer costumes. " + "; ".join(project["project"].get("excluded_motifs", [])),
              "ACCEPTANCE\nVerify identity, story event, world positions, eyelines, expression and body language, anatomy, style parity, and crop/lettering safety against the original references."]
    return {"panel_id": panel_id, "dependency_sha256": panel_dependency_digest(project, panel),
            "reference_map": reference_map, "prompt": "\n\n".join(chunks),
            "lettering_only": [copy.deepcopy(lines[d]) for d in panel["dialogue_ids"]],
            "notice": "Never submit lettering_only as instructions to paint text. Adapt fields to the live provider schema. This packet does not authorize a paid call or certify visual quality."}


def scene_map(project, panel_id):
    panel = next((p for p in project["panels"] if p["id"] == panel_id), None)
    if panel is None:
        raise InvalidProject(f"Unknown panel {panel_id}")
    scene = next(s for s in project["scenes"] if s["id"] == panel["scene_id"])
    env = next(e for e in project["environments"] if e["id"] == scene["environment_id"])
    camera = panel["camera"]
    points = [v["position"] for v in panel["state"].values()] + [l["position"] for l in env.get("landmarks", [])] + [camera["position"], camera["target"]]
    xmin, xmax = min(p[0] for p in points)-2, max(p[0] for p in points)+2
    ymin, ymax = min(p[1] for p in points)-2, max(p[1] for p in points)+2
    scale = min(660/(xmax-xmin), 540/(ymax-ymin))
    def xy(p):
        return 70+(p[0]-xmin)*scale, 610-(p[1]-ymin)*scale
    def label(p, text, color, radius):
        x, y = xy(p)
        return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius}" fill="{color}"/><text x="{x+12:.2f}" y="{y-26:.2f}" font-size="14">{html.escape(text)}</text>'
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="700" viewBox="0 0 800 700">', '<rect width="800" height="700" fill="white"/>', f'<text x="30" y="28" font-size="20">{html.escape(panel_id)}: top-down blocking (X east, Y north, Z up)</text>']
    axis = panel.get("axis", scene.get("axis"))
    if axis:
        a, b = xy(axis["a"]), xy(axis["b"])
        parts.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="#777" stroke-dasharray="6 4"/>')
    a, b = xy(camera["position"]), xy(camera["target"])
    parts.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="#b42d1b" stroke-width="3"/>')
    for l in env.get("landmarks", []):
        parts.append(label(l["position"], l["id"]+": "+l.get("label", ""), "#888888", 8))
    for cid, state in panel["state"].items():
        parts.append(label(state["position"], cid, "#1967b0", 8))
    parts.append(label(camera["position"], "CAMERA z="+str(camera["position"][2]), "#b42d1b", 10))
    parts += ['<text x="30" y="675" font-size="14">Planning diagram only. Generate the final artwork as a 2D drawing.</text>', '</svg>']
    return "\n".join(parts)


def scene_map_png(project, panel_id, path):
    """Raster planning diagram from recorded coordinates, never generated art."""
    from PIL import Image, ImageDraw, ImageFont
    panel = next((p for p in project["panels"] if p["id"] == panel_id), None)
    if panel is None:
        raise InvalidProject(f"Unknown panel {panel_id}")
    scene = next(s for s in project["scenes"] if s["id"] == panel["scene_id"])
    env = next(e for e in project["environments"] if e["id"] == scene["environment_id"])
    camera = panel["camera"]
    points = [v["position"] for v in panel["state"].values()] + [l["position"] for l in env.get("landmarks", [])] + [camera["position"], camera["target"]]
    xmin, xmax = min(p[0] for p in points)-2, max(p[0] for p in points)+2
    ymin, ymax = min(p[1] for p in points)-2, max(p[1] for p in points)+2
    scale = min(680/(xmax-xmin), 540/(ymax-ymin))
    def xy(p):
        return 50+(p[0]-xmin)*scale, 610-(p[1]-ymin)*scale
    im = Image.new("RGB", (1000, 700), "white")
    draw = ImageDraw.Draw(im)
    font = ImageFont.load_default(size=17)
    draw.text((25, 20), panel_id+": top-down blocking; X east, Y north, Z up", fill="black", font=font)
    draw.text((25, 660), "Planning only. Labels and markers must not appear in final drawn art.", fill="black", font=font)
    axis = panel.get("axis", scene.get("axis"))
    if axis:
        draw.line([xy(axis["a"]), xy(axis["b"])], fill="#aaaaaa", width=2)
    draw.line([xy(camera["position"]), xy(camera["target"])], fill="#b42d1b", width=3)
    for landmark in env.get("landmarks", []):
        x, y = xy(landmark["position"])
        draw.rectangle((x-9, y-9, x+9, y+9), fill="#888888")
        draw.text((x+15, y-26), landmark["id"]+": "+landmark.get("label", ""), fill="black", font=font)
    for cid, state in panel["state"].items():
        x, y = xy(state["position"])
        draw.ellipse((x-9, y-9, x+9, y+9), fill="#1967b0")
        draw.text((x+15, y-10), cid, fill="#1967b0", font=font)
    x, y = xy(camera["position"])
    draw.ellipse((x-10, y-10, x+10, y+10), fill="#b42d1b")
    draw.text((x+15,y-10), "CAMERA z="+str(camera["position"][2]), fill="#b42d1b", font=font)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    im.save(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=["validate", "packet", "map"])
    ap.add_argument("project", type=Path)
    ap.add_argument("panel", nargs="?")
    ap.add_argument("--files", action="store_true", help="Verify reference hashes and accepted art bytes")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    try:
        def unique_object(pairs):
            value = {}
            for key, item in pairs:
                if key in value:
                    raise InvalidProject(f"Duplicate JSON object key: {key}")
                value[key] = item
            return value
        project = json.loads(args.project.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
        errors = validate(project, args.project.parent, args.files)
        if errors:
            print(json.dumps({"ok": False, "errors": errors}, indent=2, ensure_ascii=False))
            return 2
        if args.command == "validate":
            result = json.dumps({"ok": True, "scope": "record consistency only; visual inspection remains required", "files_checked": args.files}, indent=2)
        elif not args.panel:
            raise InvalidProject("packet and map require a panel ID")
        elif args.command == "packet":
            result = json.dumps(packet(project, args.panel), indent=2, ensure_ascii=False)
        elif args.out and args.out.suffix.lower() == ".png":
            scene_map_png(project, args.panel, args.out)
            print(str(args.out))
            return 0
        else:
            result = scene_map(project, args.panel)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(result+"\n", encoding="utf-8")
            print(str(args.out))
        else:
            print(result)
        return 0
    except (OSError, ValueError, KeyError, TypeError, OverflowError, RecursionError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
