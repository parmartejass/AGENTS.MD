#!/usr/bin/env bash
# Shared library for Nia API scripts
# Source this file: source "$(dirname "$0")/lib.sh"

BASE_URL="${NIA_BASE_URL:-https://apigcp.trynia.ai/v2}"

nia_auth() {
  if [ -n "${NIA_API_KEY:-}" ]; then
    NIA_KEY="$NIA_API_KEY"
  else
    NIA_KEY=$(cat ~/.config/nia/api_key 2>/dev/null || echo "")
  fi
  if [ -z "$NIA_KEY" ]; then
    echo "Error: No API key found. Set NIA_API_KEY env variable or run: echo 'your-key' > ~/.config/nia/api_key"
    exit 1
  fi
}

urlencode() {
  jq -nr --arg value "$1" '$value|@uri'
}

# Generic curl wrapper: nia_curl METHOD URL [DATA]
# Captures HTTP status code and returns JSON. Non-JSON errors (e.g. rate limits) are wrapped.
nia_curl() {
  local method="$1" url="$2" data="${3:-}"
  local args=(
    -sS
    --connect-timeout 10
    --max-time "${NIA_MAX_TIME:-60}"
    --retry "${NIA_RETRY_COUNT:-2}"
    --retry-delay 1
    -w '\n__HTTP_STATUS:%{http_code}'
    -X "$method"
    "$url"
    -H "Authorization: Bearer $NIA_KEY"
  )
  if [ -n "$data" ]; then
    args+=(-H "Content-Type: application/json" -d "$data")
  fi
  local response curl_status
  if ! response=$(curl "${args[@]}" 2>&1); then
    curl_status=$?
    jq -n --arg msg "$response" --argjson code "$curl_status" '{error: $msg, transport_status: $code}'
    return "$curl_status"
  fi
  local http_status="${response##*__HTTP_STATUS:}"
  local body="${response%__HTTP_STATUS:*}"
  http_status="${http_status//[!0-9]/}"
  : "${http_status:=0}"
  if echo "$body" | jq '.' >/dev/null 2>&1; then
    echo "$body"
  else
    jq -n --arg msg "$body" --argjson code "$http_status" '{error: $msg, http_status: $code}' 2>/dev/null \
      || printf '{"error":"request failed","http_status":%d}\n' "$http_status"
  fi
  if [ "$http_status" -ge 400 ]; then
    return 22
  fi
}

nia_get() {
  local payload
  payload=$(nia_curl GET "$1") || { echo "$payload" | jq '.'; return 1; }
  echo "$payload" | jq '.'
}
nia_post() {
  local payload
  payload=$(nia_curl POST "$1" "$2") || { echo "$payload" | jq '.'; return 1; }
  echo "$payload" | jq '.'
}
nia_put() {
  local payload
  payload=$(nia_curl PUT "$1" "$2") || { echo "$payload" | jq '.'; return 1; }
  echo "$payload" | jq '.'
}
nia_patch() {
  local payload
  payload=$(nia_curl PATCH "$1" "$2") || { echo "$payload" | jq '.'; return 1; }
  echo "$payload" | jq '.'
}
nia_delete() {
  local payload
  payload=$(nia_curl DELETE "$1") || { echo "$payload" | jq '.'; return 1; }
  echo "$payload" | jq '.'
}

# Raw get with custom jq filter: nia_get_raw URL | jq ...
nia_get_raw() { nia_curl GET "$1"; }
nia_post_raw() { nia_curl POST "$1" "$2"; }

# Stream (SSE) — no buffering, no jq
nia_stream() { curl -sS -N --connect-timeout 10 --max-time "${NIA_STREAM_MAX_TIME:-300}" -X POST "$1" -H "Authorization: Bearer $NIA_KEY" -H "Content-Type: application/json" -d "$2"; }

# Form upload: nia_upload URL field1=val1 field2=val2 file=@path
nia_upload() {
  local url="$1"; shift
  local args=(-s -X POST "$url" -H "Authorization: Bearer $NIA_KEY")
  for f in "$@"; do args+=(-F "$f"); done
  curl -sS --connect-timeout 10 --max-time "${NIA_MAX_TIME:-60}" "${args[@]}" | jq '.'
}

# Resolve a human-friendly identifier (owner/repo, URL, display name) to a source ID.
# Returns the resolved ID, or the original value if it's already a UUID/ObjectId.
resolve_source_id() {
  local identifier="$1" type="${2:-}"
  if [[ "$identifier" =~ ^[0-9a-fA-F]{24}$ ]] || [[ "$identifier" =~ ^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$ ]]; then
    echo "$identifier"
    return 0
  fi
  local encoded=$(urlencode "$identifier")
  local url="$BASE_URL/sources/resolve?identifier=${encoded}"
  if [ -n "$type" ]; then url="${url}&type=${type}"; fi
  local result
  result=$(nia_curl GET "$url")
  local resolved_id=$(echo "$result" | jq -r '.id // empty' 2>/dev/null)
  if [ -n "$resolved_id" ]; then
    echo "$resolved_id"
    return 0
  fi
  echo "$identifier"
  return 1
}

# Helper: build grep JSON body with all common options
build_grep_json() {
  local pattern="$1" path_prefix="${2:-}"
  jq -n \
    --arg p "$pattern" \
    --arg pp "$path_prefix" \
    --arg cs "${CASE_SENSITIVE:-}" \
    --arg ww "${WHOLE_WORD:-}" \
    --arg fs "${FIXED_STRING:-}" \
    --arg om "${OUTPUT_MODE:-}" \
    --arg hl "${HIGHLIGHT:-}" \
    --arg ex "${EXHAUSTIVE:-}" \
    --arg la "${LINES_AFTER:-}" \
    --arg lb "${LINES_BEFORE:-}" \
    --arg mpf "${MAX_PER_FILE:-}" \
    --arg mt "${MAX_TOTAL:-50}" \
    '{pattern: $p, context_lines: 3, max_total_matches: ($mt | tonumber)}
    + (if $pp != "" then {path: $pp} else {} end)
    + (if $cs != "" then {case_sensitive: ($cs == "true")} else {} end)
    + (if $ww != "" then {whole_word: ($ww == "true")} else {} end)
    + (if $fs != "" then {fixed_string: ($fs == "true")} else {} end)
    + (if $om != "" then {output_mode: $om} else {} end)
    + (if $hl != "" then {highlight: ($hl == "true")} else {} end)
    + (if $ex != "" then {exhaustive: ($ex == "true")} else {} end)
    + (if $la != "" then {A: ($la | tonumber)} else {} end)
    + (if $lb != "" then {B: ($lb | tonumber)} else {} end)
    + (if $mpf != "" then {max_matches_per_file: ($mpf | tonumber)} else {} end)'
}

# Auto-init auth on source
nia_auth
