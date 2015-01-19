scriptencoding utf-8

if exists('g:loaded_shadow') || !executable('git') || !has('signs') || &cp
  finish
endif
let g:loaded_shadow = 1

" Initialisation {{{

" Realtime updates require Vim 7.3.105+.
if v:version < 703 || (v:version == 703 && !has("patch105"))
  finish
endif

let g:shadow_enabled = 1

" Primary functions {{{

command ShadowDisable call shadow#disable()
command ShadowEnable  call shadow#enable()

" }}}

call shadow#enable()
