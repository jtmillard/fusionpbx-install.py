# ~/.bashrc: executed by bash(1) for non-login shells.

# Note: PS1 and umask are already set in /etc/profile. You should not
# need this unless you want different defaults for root.
# PS1='${debian_chroot:+($debian_chroot)}\h:\w\$ '
# umask 022

export LS_OPTIONS='--color=auto'
eval "`dircolors`"
alias ls='ls $LS_OPTIONS'
alias la='ls $LS_OPTIONS -a'
alias ll='ls $LS_OPTIONS -l'
alias l='ls $LS_OPTIONS -lA'
#
# Some more alias to avoid making mistakes:
# alias rm='rm -i'
# alias cp='cp -i'
# alias mv='mv -i'
alias a='alias'
alias dap='sudo -u postgres'
alias gop='cd /var/lib/postgresql;su postgres'
alias q='exit'
alias h='history'
alias aptf='sudo apt-get -f install'
alias aptg='~/bin/pkgstat'
alias apts='apt-cache search '
alias apti='apt-get install '

# Aliases for ease of trouble shooting 
alias fup='systemctl start freeswitch'
alias fdown='systemctl stop freeswitch'
alias frest='systemctl restart freeswitch'
alias fstat='systemctl status freeswitch'
alias jnl='journalctl -xn'
alias sdr='systemctl daemon-reload'

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
force_color_prompt=yes

if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
        # We have color support; assume it's compliant with Ecma-48
        # (ISO/IEC-6429). (Lack of such support is extremely rare, and such
        # a case would tend to support setf rather than setaf.)
        color_prompt=yes
    else
        color_prompt=
    fi
fi
export PATH=".:/root:/root/bin:${PATH}"
