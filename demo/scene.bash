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
    *) _scene_add ;;
  esac
  return 0
}

# Scene: the agent writes code, takes one shortcut, debt-ops catches it at write-time.
_scene_add() {
  printf '\n'
  # Claude is working — the agent loader before the edit lands.
  local frames=('✻' '✶' '✷' '✸' '✺' '✹') n=6 i
  for ((i = 0; i < 11; i++)); do
    printf '\r  %s%s%s %sWorking…%s %s(0s · esc to interrupt)%s' \
      "$P" "${frames[i % n]}" "$R" "$T" "$R" "$DD" "$R"
    sleep 0.1
  done
  printf '\r\e[K'
  sleep 0.1
  printf '  %s✓%s edited %sapi/checkout.ts%s\n' "$G" "$R" "$T" "$R"
  sleep 0.3
  printf '      %spayload.userId = session.user %sas any%s%s   %s# cast to clear the type error%s\n' "$D" "$Y" "$R" "$D" "$DD" "$R"
  sleep 0.4
  printf '  %s✓%s +1 entry: %sas-any-checkout-payload%s %s(A)%s   %s# loosened type silences the compiler%s\n\n' "$G" "$R" "$B" "$R" "$D" "$R" "$DD" "$R"
}
