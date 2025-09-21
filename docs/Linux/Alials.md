---
tags:
  - Linux
  - Debian
  - Manjaro (Arch)
---

# Аліаси (Термінал)

```bash
nano ~/.bashrc
```
```bash
nano ~/.zshrc
```

## Debian / Ubuntu (nala/apt)

- У цьому розділі наведені аліаси для швидкого керування пакетами через `nala` та `apt`:
```bash
alias nalai='sudo nala install'
alias apti='sudo apt install'
alias nalar='sudo nala remove'
alias aptr='sudo apt remove'
alias nalaar='sudo nala autoremove'
alias aptar='sudo apt autoremove'
alias nalaud='sudo nala update'
alias nalaug='sudo nala upgrade'
alias aptud='sudo apt update'
alias aptug='sudo apt upgrade'
alias c='clear'
alias wc='warp-cli connect'
alias wd='warp-cli disconnect'
alias ws='warp-cli status'
alias gps='globalprotect show --status'
alias gpc='globalprotect connect'
alias gpd='globalprotect disconnect'
alias p3='python3'
alias gita='git add .'
gitc() {
  read "msg?Введите название коммита: "
  GIT_EDITOR=true git commit -m "$msg"
}
alias gitp='git push origin main'
```

- Щоб зміни набули чинності:
```bash
source ~/.bashrc
```
```bash
source ~/.zshrc
```

## Pacman (Arch / Manjaro)
  - Аліаси та функції для Pacman і допоміжних інструментів:
  ```bash
  alias md='mkdir'
  alias pacmanr='sudo pacman -Rns'
  alias pacmans='pacman -Ss'
  alias pacmanug='sudo pacman -Syu'
  alias pacmani='sudo pacman -S'
  alias c='clear'
  alias wc='warp-cli connect'
  alias wd='warp-cli disconnect'
  alias ws='warp-cli status'
  alias gps='globalprotect show --status'
  alias gpc='globalprotect connect'
  alias gpd='globalprotect disconnect'
  alias p3='python3'
  pacmanar() {
    orphans=$(pacman -Qdtq)
    if [ -z "$orphans" ]; then
      echo "✅ Осиротілих пакетів немає."
    else
      sudo pacman -Rns $orphans
    fi
  }
  alias off='shutdown now'
  alias rb='reboot'
  alias counti='count=0; for f in *; do [[ -f $f && $f != *_* ]] && ((count++)); done; echo $count'
  alias gita='git add .'
  gitc() {
    read "msg?Введите название коммита: "
    GIT_EDITOR=true git commit -m "$msg"
  }
  alias gitp='git push origin main'
  ```
