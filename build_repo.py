#!/usr/bin/env python3
"""Build isolated Kodi Dailymotion test repository. No other addons modified."""
from pathlib import Path
import hashlib, io, re, urllib.request, zipfile, xml.etree.ElementTree as ET
root=Path(".")
url="https://softlibre.unizar.es/kodi/addons/omega/plugin.video.dailymotion_com/plugin.video.dailymotion_com-2.4.5.zip"
data=urllib.request.urlopen(url,timeout=40).read()
expected="952085f320df8f7d2b1f31af52b1ce73197cf62bc01a9c150ea178906b21ad79"
assert hashlib.sha256(data).hexdigest()==expected, "Upstream ZIP differs from inspected source; refusing to publish"
source=zipfile.ZipFile(io.BytesIO(data))
files={i.filename:source.read(i) for i in source.infolist() if not i.is_dir()}
prefix="plugin.video.dailymotion_com/"
addon=prefix+"addon.xml"
files[addon]=files[addon].replace(b'version="2.4.5"',b'version="2.4.5.3"',1)
key=prefix+"resources/lib/dailymotion.py"
s=files[key].decode("utf-8")
# Replace the full legacy resolver; the old patch only masked IndexError.
start=s.index('def getStreamUrl(')
end=s.index('def queueVideo(', start)
replacement=(root/"playback_patch.py.txt").read_text()
s=s[:start]+replacement+s[end:]
compile(s,key,"exec")
files[key]=s.encode("utf-8")
out=root/"plugin.video.dailymotion_com"
out.mkdir(exist_ok=True)
with zipfile.ZipFile(out/"plugin.video.dailymotion_com-2.4.5.3.zip","w",zipfile.ZIP_DEFLATED) as z:
    for name,body in files.items(): z.writestr(name,body)
repoid="repository.genomesteve.dailymotion.test"
repo_xml='''<addon id="repository.genomesteve.dailymotion.test" name="GenomeSteve Dailymotion Test Repository" version="1.0.0" provider-name="GenomeSteve"><extension point="xbmc.addon.repository" name="GenomeSteve Dailymotion Test Repository"><dir><info compressed="false">https://raw.githubusercontent.com/GenomeSteve/kodi-dailymotion-test/main/addons.xml</info><checksum>https://raw.githubusercontent.com/GenomeSteve/kodi-dailymotion-test/main/addons.xml.md5</checksum><datadir zip="true">https://raw.githubusercontent.com/GenomeSteve/kodi-dailymotion-test/main/</datadir></dir></extension><extension point="xbmc.addon.metadata"><summary lang="en_GB">Isolated Dailymotion test feed</summary><description lang="en_GB">Experimental Kodi Omega Dailymotion playback patch.</description><platform>all</platform></extension></addon>'''
repo_dir=root/repoid
repo_dir.mkdir(exist_ok=True)
with zipfile.ZipFile(repo_dir/(repoid+"-1.0.0.zip"),"w",zipfile.ZIP_DEFLATED) as z: z.writestr(repoid+"/addon.xml",repo_xml)
catalog='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n'+repo_xml+"\n"+files[addon].decode("utf-8").replace('<?xml version="1.0" encoding="UTF-8"?>','').strip()+"\n</addons>\n"
ET.fromstring(catalog)
(root/"addons.xml").write_text(catalog)
(root/"addons.xml.md5").write_text(hashlib.md5(catalog.encode()).hexdigest())
# Put the installer at the website root so Kodi sees a direct ZIP link.
import shutil
installer_name=repoid+"-1.0.0.zip"
shutil.copyfile(repo_dir/installer_name, root/installer_name)
(root/"index.html").write_text('''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<html><head><title>Index of /kodi-dailymotion-test/</title></head><body>
<h1>Index of /kodi-dailymotion-test/</h1><hr><pre>
<a href="../">../</a>
<a href="repository.genomesteve.dailymotion.test-1.0.0.zip">repository.genomesteve.dailymotion.test-1.0.0.zip</a>
</pre><hr></body></html>
''')
print("Built isolated Kodi repository successfully")
