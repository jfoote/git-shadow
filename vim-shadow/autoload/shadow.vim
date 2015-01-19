" Primary functions {{{
"

let g:shadow_cmd = fnamemodify(resolve(expand('<sfile>:p')), ':h') . "/git_shadow.py"

function! shadow#system(cmd, ...)
  let output = call('system', [a:cmd] + a:000)
  if v:shell_error != 0
      call shadow#disable()
      throw 'cmd error'
  endif
  return output
endfunction

function! shadow#write_shadow()
    let l:filepath = expand('%:p')
    if empty(l:filepath)
        return
    endif
    let l:path = l:filepath . ".shadow." . strftime("%Y-%m-%d_%H:%M:%S") 
    call writefile(getline(1, '$'), l:path)
    call shadow#system(g:shadow_cmd . ' ' . l:path) 
endfunction

function! shadow#disable()
    augroup shadow
        autocmd!
    augroup END
    
    let g:shadow_enabled = 0
endfunction


function! shadow#enable()
    augroup shadow
      autocmd!
    
      autocmd FileChangedShellPost * call shadow#write_shadow()
      autocmd CursorHold,CursorHoldI * call shadow#write_shadow()
      autocmd BufLeave * call shadow#write_shadow()
      
      autocmd VimLeavePre * call shadow#write_shadow()

      autocmd BufWritePost * call shadow#write_shadow()
      autocmd BufWritePost * call shadow#write_shadow()
    
      " Disable during :vimgrep
      "autocmd QuickFixCmdPre  *vimgrep* let g:shadow_enabled = 0
      "autocmd QuickFixCmdPost *vimgrep* let g:shadow_enabled = 1
    augroup END

    let g:shadow_enabled = 1
endfunction

" }}}
