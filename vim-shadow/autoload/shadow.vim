function! shadow#write_shadow()
    " Pass filepath and buffer contents to git-shadow
python << EOF
import vim, subprocess, tempfile
filepath = vim.current.buffer.name
if filepath:
    buf = vim.current.buffer.range(1, len(vim.current.buffer))
    with tempfile.NamedTemporaryFile() as tf:
        tf.write("\n".join([l for l in buf]))
        tf.flush()
        subprocess.call(["git", "shadow", "shadow-file", filepath, tf.name])
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
