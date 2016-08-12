let SessionLoad = 1
if &cp | set nocp | endif
let s:so_save = &so | let s:siso_save = &siso | set so=0 siso=0
let v:this_session=expand("<sfile>:p")
silent only
cd ~/Documents/Pincha/AKTIUN/Repos/ZDvis
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +689 zdvis/src/zd.py
badd +1 zdvis/src/__init__.py
badd +3 zdvis/main.py
badd +3 zdvis/__init__.py
badd +183 zdvis/src/rest.py
badd +6 setup.py
badd +1 \'/home/eduardo/Proyectos/AKTIUN/ZDvis/zdvis/src/data_handler.py\'
badd +1 \'/home/eduardo/Proyectos/AKTIUN/ZDvis/zdvis/data_handler.py\'
badd +25 zdvis/data_handler.py
badd +121 zdvis/src/js/render/common_charts.js
badd +1 zdvis/MANIFEST.in
badd +1 \'/home/eduardo/Proyectos/AKTIUN/ZDvis/MANIFEST.in\'
badd +1 MANIFEST.in
badd +252 ~/Documents/Pincha/AKTIUN/Jupyter/websocket_calls.json
badd +135 ~/Documents/Pincha/AKTIUN/Jupyter/websocket_vis_response.json
badd +137 ~/Documents/Scripts/web_parser.py
badd +23 ~/Documents/Pincha/AKTIUN/Jupyter/sources_key.json
badd +116 zdvis/src/js/render/line_bars_trend.js
badd +129 zdvis/src/js/render/line_trend_attrs.js
badd +66 zdvis/src/visrender.py
badd +24 zdvis/src/js/tools.js
badd +5 ~/Documents/Pincha/AKTIUN/Jupyter/zdvis/js/tools.js
badd +508 zdvis/src/static/js/render/chart.js
badd +3 README.md
badd +20 zdvis/src/static/js/tools.js
badd +64 zdvis/src/static/css/style.css
argglobal
silent! argdel *
edit zdvis/src/zd.py
set splitbelow splitright
wincmd t
set winheight=1 winwidth=1
argglobal
setlocal fdm=indent
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=2
setlocal fml=1
setlocal fdn=10
setlocal nofen
let s:l = 663 - ((24 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
663
normal! 0
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
