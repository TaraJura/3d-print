#!/usr/bin/env python3
"""Export exact embedded UI with a clearly marked offline fetch simulation."""
from pathlib import Path
import hashlib
import re

HERE = Path(__file__).resolve().parent
source = HERE.parent / 'prvni-motor.ino'
html = re.search(r'R"HTML\(([\s\S]*?)\)HTML"', source.read_text()).group(1)
assert html.count('@TOKEN@') == 1
html = html.replace('@TOKEN@', '0123456789abcdef0123456789abcdef')
simulation = '''<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'none'">
<script>
// Preview-only simulator. No request is sent to any network or real device.
let previewSequence=10;
window.fetch=async(path,options)=>{
  if(options.signal.aborted)throw new DOMException('Aborted','AbortError');
  const prefix={'/arm':'ARM_OK:','/hold':'HOLD_OK:','/session':'SESSION_OK:'}[path];
  if(path!=='/stop' && !prefix)throw new Error('Preview blocks unknown network requests');
  const value=path==='/stop'?'STOP_OK':prefix+(++previewSequence).toString(16).padStart(32,'0');
  return {ok:true,text:async()=>value};
};
</script>'''
html = html.replace('<meta name="viewport"', simulation + '\n<meta name="viewport"', 1)
html = html.replace('<h1>', '<aside role="note" style="padding:.7rem;background:#fff2cf;border:1px solid #c49834;border-radius:8px;margin-bottom:1rem">'
                    '<strong>Offline náhled · pouze simulace</strong><br>Tato stránka neovládá Arduino, motor ani servo. Síťové požadavky jsou zakázané.</aside>\n<h1>', 1)
html += '\n<!-- Firmware source SHA256: ' + hashlib.sha256(source.read_bytes()).hexdigest() + ' -->\n'
output = HERE.parents[4] / 'elektronika/auticko/nahled-ovladani-v3.html'
output.write_text(html)
print(output)
