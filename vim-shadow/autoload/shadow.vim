function! shadow#write_shadow()
    " Pass filepath and buffer contents to git-shadow
python << EOF
import vim, subprocess, pickle
filepath = vim.current.buffer.name
if filepath:
    buf = vim.current.buffer.range(0, len(vim.current.buffer))
    subprocess.call(["git", "shadow", "shadow-buf", filepath, pickle.dumps(buf[:])])
EOF
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
