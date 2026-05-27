# Fabricated debt-ops session for the VHS demo (see debt-ops.tape).
# This is NOT real command output — it's scripted so the README GIF is
# deterministic and re-runnable in CI. Sourced by the tape before recording.

# Catppuccin Mocha palette (truecolor) so the text matches the VHS theme.
G=$'\e[38;2;166;227;161m'   # green
B=$'\e[38;2;137;180;250m'   # blue
M=$'\e[38;2;203;166;247m'   # mauve
Y=$'\e[38;2;249;226;175m'   # yellow
P=$'\e[38;2;250;179;135m'   # peach
T=$'\e[38;2;205;214;244m'   # text
D=$'\e[38;2;127;132;156m'   # dim
DD=$'\e[38;2;108;112;134m'  # dimmer
BO=$'\e[1m'
R=$'\e[0m'

# Claude Code-style prompt: a bold mauve chevron.
PS1='\[\e[1m\e[38;2;203;166;247m\]>\[\e[0m\] '

# Natural-language turns have no slash, so an unknown command lands here.
command_not_found_handle() {
  case "$*" in
    add\ *)  _scene_add ;;
    drop\ *) _scene_drop ;;
    *) printf '%scommand not found: %s%s\n' "$DD" "$1" "$R" ;;
  esac
  return 0
}

# Scene 1: gates run inside the edit loop, then shortcuts are logged.
# Over-capture is the intended posture — log freely, prune in a word.
_scene_add() {
  printf '\n'
  # Claude is working — the agent loader before any results land.
  local frames=('✻' '✶' '✷' '✸' '✺' '✹') n=6 i
  for ((i = 0; i < 14; i++)); do
    printf '\r  %s%s%s %sWorking…%s %s(%ds · esc to interrupt)%s' \
      "$P" "${frames[i % n]}" "$R" "$T" "$R" "$DD" "$((i / 10))" "$R"
    sleep 0.1
  done
  printf '\r\e[K'
  sleep 0.15
  printf '  %s✓%s edited %sclients/http.py%s\n' "$G" "$R" "$T" "$R"
  sleep 0.35
  printf '  %s⠋%s ruff · mypy · pytest' "$DD" "$R"
  sleep 0.7
  printf '\r  %s✓%s ruff · mypy · pytest passed %s(1.8s)%s   %s# your gates, in the edit loop%s\n' "$G" "$R" "$D" "$R" "$DD" "$R"
  sleep 0.4
  printf '  %s✓%s +2 entries: %sretry-swallows-error%s %s(A)%s   %s# the last retry drops the error silently%s\n' "$G" "$R" "$B" "$R" "$D" "$R" "$DD" "$R"
  sleep 0.2
  printf '              %s·%s %slog-format-nit%s %s(B)%s\n\n' "$DD" "$R" "$B" "$R" "$D" "$R"
}

# Scene 2: one word prunes what wasn't worth tracking — the kept entry (A) stays.
_scene_drop() {
  printf '\n'
  sleep 0.2
  printf '  %s–%s dropped %slog-format-nit%s   %s# over-captured — gone in one word%s\n\n' "$P" "$R" "$D" "$R" "$DD" "$R"
}

# Scene 3: the slash command — a function whose name carries the slash.
_review_row() {  # $1 slug  $2 file  $3 reason  $4 tag (optional)
  printf '    %s•%s %s%-21s%s %s%-17s%s %s%s%s' "$B" "$R" "$T" "$1" "$R" "$D" "$2" "$R" "$D" "$3" "$R"
  [ -n "$4" ] && printf ' %s%s%s%s' "$M" "$BO" "$4" "$R"
  printf '\n'
}

function /debt-ops:review {
  printf '\n'
  sleep 0.2
  printf '  %s%sdebt-ops review%s %s— 11 entries%s\n\n' "$BO" "$T" "$R" "$D" "$R"
  sleep 0.25
  printf '  %s%stop 3 to pay down%s\n' "$BO" "$Y" "$R"
  sleep 0.15; _review_row "legacy-auth-shim"     "auth/session.py" "· came up later · 9 edits since logged ·" "AI"
  sleep 0.15; _review_row "unbatched-email-send" "jobs/mailer.py"  "· planned tradeoff · 6 edits since logged"
  sleep 0.15; _review_row "n-plus-one-query"     "api/feed.py"     "· shortcut you knew about · 4 edits since logged"
  sleep 0.25
  printf '\n  %scold (4)%s %s— deprioritize; revisit on next hot edit%s\n' "$D" "$R" "$DD" "$R"
  printf '    %s·%s %s%-21s%s %s(unchanged in 142d)%s\n\n' "$DD" "$R" "$DD" "config-loader-todo" "$R" "$DD" "$R"
}
