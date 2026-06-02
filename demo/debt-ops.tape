# debt-ops README demo — "terminal GIFs as code" via VHS (charmbracelet/vhs).
# Regenerate from the repo root:  vhs demo/debt-ops.tape
# The fabricated session it drives lives in demo/scene.bash.

Output demo/debt-ops.gif

Set Shell bash
Set FontFamily "JetBrains Mono"
Set FontSize 18
Set Width 1280
Set Height 720
Set Padding 24
Set Margin 40
Set MarginFill "#181825"
Set Theme "Catppuccin Mocha"
Set WindowBar Colorful
Set BorderRadius 10
Set TypingSpeed 45ms
Set Framerate 60

# Load the fabricated scene handler, hidden from the recording.
Hide
Type "source demo/scene.bash && clear"
Enter
Show

Sleep 600ms

# One real catch: the agent casts to `as any`, debt-ops registers it at write-time.
Type "wire session.user into the checkout payload"
Sleep 300ms
Enter
Sleep 2.5s

# Hold so the catch is readable.
Sleep 4s
