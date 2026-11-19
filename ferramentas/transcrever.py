import wave,numpy as np,json
from faster_whisper import WhisperModel
w=wave.open('audio.wav');a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
m=WhisperModel('medium',device='cpu',compute_type='int8')
segs,_=m.transcribe(a,language='pt',word_timestamps=True,vad_filter=True,beam_size=1)
out=[]
for s in segs:
    out.append({'s':s.start,'e':s.end,'t':s.text,'w':[(x.word,x.start,x.end) for x in s.words]})
    json.dump(out,open('words.json','w'),ensure_ascii=False)
open('tr.done','w').write('ok')
