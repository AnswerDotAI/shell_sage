# shell_sage non-destructive clear: scroll the screen into tmux history, record a
# context mark for ssage, and home the cursor. Nothing is destroyed: your scrollback
# stays intact, but ssage captures never reach past the most recent clear.
#
# Bash setup (readline bindings are only active at the prompt, so full-screen
# apps still receive a plain ctrl-L):
#
#   source /path/to/ssage_clear.sh
#   bind -x '"\C-l": ssage_clear'
#
# Zsh:
#
#   source /path/to/ssage_clear.sh
#   zle -N ssage_clear && bindkey '^L' ssage_clear
ssage_clear() {
  if [ -n "$TMUX_PANE" ]; then
    printf '\n%.0s' $(seq 1 "$(tput lines)")  # scroll contents into history, teleprint-style
    printf '\033[H'
    mkdir -p ~/.cache/shell_sage
    tmux display-message -p -t "$TMUX_PANE" '#{history_size}' > ~/.cache/shell_sage/mark-"${TMUX_PANE#%}"
  else
    printf '\033[H\033[2J'
  fi

  [[ -n $ZSH_VERSION && -o zle ]] && zle reset-prompt
}
