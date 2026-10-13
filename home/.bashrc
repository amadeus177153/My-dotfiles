#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls --color=auto'
alias grep='grep --color=auto'
PS1='[\u@\h \W]\$ '

# Added by LM Studio CLI (lms)
export PATH="$PATH:/home/amadeus177153/.lmstudio/bin"
# End of LM Studio CLI section

#Added by User
alias modrinth='flatpak run --nosocket=wayland --env=WEBKIT_DISABLE_COMPOSITING_MODE=1 --env=LIBGL_ALWAYS_SOFTWARE=1 com.modrinth.ModrinthApp'

# Created by `pipx` on 2026-08-06 03:20:35
export PATH="$PATH:/home/amadeus177153/.local/bin"
