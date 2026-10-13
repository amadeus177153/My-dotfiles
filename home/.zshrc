# Activar autocompletado avanzado
autoload -Uz compinit
compinit

# Cargar los plugins de color y sugerencias
source /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
source /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh

# Mostrar el logo y la información del sistema al iniciar
fastfetch

# if command -v pokemon-colorscripts >/dev/null 2>&1; then
#     pokemon-colorscripts --no-title -s -r
# fi
/usr/bin/fastfetch
export PATH=~/.npm-global/bin:$PATH
