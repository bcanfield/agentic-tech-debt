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

# Load the fabricated scene handlers, hidden from the recording.
Hide
Type "source demo/scene.bash && clear"
Enter
Show

Sleep 800ms

# Scene 1: Claude works, the edit logs the shortcuts it took, gates run in the loop.
Type "add retry logic to the API client"
Sleep 500ms
Enter
Sleep 4s

# Scene 2: prune the over-capture — keep the real one (A), drop the nit (B).
Sleep 600ms
Type "drop B"
Sleep 400ms
Enter
Sleep 1.4s

# Scene 3: review ranks what's left.
Sleep 700ms
Type "/debt-ops:review"
Sleep 400ms
Enter
Sleep 2.5s

# Hold the final frame so visitors can actually read the ranking.
Sleep 6s
