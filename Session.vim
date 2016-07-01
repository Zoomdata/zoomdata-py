let SessionLoad = 1
if &cp | set nocp | endif
let s:so_save = &so | let s:siso_save = &siso | set so=0 siso=0
let v:this_session=expand("<sfile>:p")
silent only
cd ~/Proyectos/AKTIUN/ZDvis
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +42 zdvis/src/zd.py
badd +1 zdvis/src/__init__.py
badd +3 zdvis/main.py
badd +3 zdvis/__init__.py
badd +8 zdvis/src/rest.py
badd +6 setup.py
badd +1 \'/home/eduardo/Proyectos/AKTIUN/ZDvis/zdvis/src/data_handler.py\'
badd +1 \'/home/eduardo/Proyectos/AKTIUN/ZDvis/zdvis/data_handler.py\'
badd +7 zdvis/data_handler.py
badd +10 zdvis/src/js/render/common_charts.js
badd +1 zdvis/MANIFEST.in
badd +1 \'/home/eduardo/Proyectos/AKTIUN/ZDvis/MANIFEST.in\'
badd +1 MANIFEST.in
silent! argdel *
edit zdvis/src/zd.py
set splitbelow splitright
wincmd t
set winheight=1 winwidth=1
argglobal
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 134 - ((12 * winheight(0) + 17) / 35)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
134
normal! 031|
tabnext 1
if exists('s:wipebuf')
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=filnxtToO
let s:sx = expand("<sfile>:p:r")."x.vim"
if file_readable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &so = s:so_save | let &siso = s:siso_save
let g:this_session = v:this_session
let g:this_obsession = v:this_session
let g:this_obsession_status = 2
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
