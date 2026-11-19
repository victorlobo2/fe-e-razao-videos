import json, subprocess, re
from PIL import ImageFont, Image, ImageDraw
import os
os.makedirs("tpl",exist_ok=True); os.makedirs("out2",exist_ok=True)
SRC=os.environ.get("SRC","video.mp4"); CROPX=int(os.environ.get("CROPX","558"))
BG="#12100E"; GOLD="#C9A24B"; CREAM="#EFE6D2"
D="/usr/share/fonts/truetype/google-fonts/ofl/crimsontext/"
FR=lambda s:ImageFont.truetype(D+"CrimsonText-Regular.ttf",s)
FI=lambda s:ImageFont.truetype(D+"CrimsonText-Italic.ttf",s)

import sys
_d=json.load(open(os.environ.get("WORDS","words.json")))
W=[]
for sg in _d:
    for w,a_,b_ in sg["w"]:
        W.append((a_,b_,w.strip()))
W=[x for x in W if x[2]]
CUTS=json.load(open(os.environ.get("CUTS","cuts.json")))
ONLY=sys.argv[1:]
CLIPS=[]
for c in CUTS:
    if ONLY and c["id"] not in ONLY: continue
    ws=[x for x in W if x[0]>=c["s"]-0.05]
    st=ws[0][0]
    we=[x for x in W if x[1]<=c["e"]+0.05]
    en=we[-1][1]
    CLIPS.append(dict(id=c["id"],s=st,e=en,title=c["title"],first=ws[0][2],last=we[-1][2]))
# ---------- layout (1080x1920) ----------
VX,VY,VW,VH=64,600,952,1190      # vídeo emoldurado
TS,LEAD=118,124                    # título: corpo e entrelinha
MAXW=VW

def wrap(title,size):
    toks=re.findall(r"\[\[.*?\]\]\S*|\S+",title)
    items=[]
    for t in toks:
        g=t.startswith("[[")
        if g:
            m2=re.match(r"\[\[(.*?)\]\](\S*)",t); items.append((m2.group(1),True,m2.group(2)))
        else: items.append((t,False,""))
    lines=[[]]; 
    def width(line):
        tot=0
        for k,(w,g,p) in enumerate(line):
            f=FI(size) if g else FR(size)
            tot+=f.getlength(w)+FR(size).getlength(p)+(FR(size).getlength(" ") if k<len(line)-1 else 0)
        return tot
    for it in items:
        if lines[-1] and width(lines[-1]+[it])>MAXW: lines.append([])
        lines[-1].append(it)
    return lines,width

def overlay(title,path):
    lines,width=wrap(title,TS)
    capH=FR(TS).getbbox("F")[3]-FR(TS).getbbox("F")[1]
    n=len(lines); blockH=capH+(n-1)*LEAD
    # cabeçalho (logo)
    s=54; f=FR(s); capL=f.getbbox("F")[3]-f.getbbox("F")[1]; lead=s*0.86; Hc=capL+lead; wc=Hc*0.56; stem=s*0.1
    gap_hdr=56
    group=Hc+gap_hdr+blockH
    top=(0+VY-group)/2+0          # centraliza o grupo na faixa acima do vídeo
    hy=top; 
    base1=hy+capL; base2=base1+lead; cx=64+wc/2; xt=64+wc+s*0.34
    sp=f.getlength(" ")
    o=[]
    o.append(f'<path d="M{cx:.1f} {hy:.1f} V{base2:.1f}" stroke="{GOLD}" stroke-width="{stem:.1f}"/>')
    o.append(f'<path d="M64 {hy+Hc*0.3:.1f} H{64+wc:.1f}" stroke="{GOLD}" stroke-width="{stem:.1f}"/>')
    fe=f.getlength("Fé")+sp*0.6
    o.append(f'<text x="{xt:.1f}" y="{base1:.1f}" font-family="Crimson Text" font-size="{s}" fill="{CREAM}">Fé</text>')
    o.append(f'<text x="{xt+fe:.1f}" y="{base1:.1f}" font-family="Crimson Text" font-style="italic" font-size="{s}" fill="{GOLD}">&amp;</text>')
    o.append(f'<text x="{xt:.1f}" y="{base2:.1f}" font-family="Crimson Text" font-size="{s}" fill="{CREAM}">Razão</text>')
    # título
    ty=base2+gap_hdr+capH
    for li,line in enumerate(lines):
        x=64
        for k,(w,g,p) in enumerate(line):
            fo=FI(TS) if g else FR(TS)
            st=' font-style="italic"' if g else ''
            col=GOLD if g else CREAM
            o.append(f'<text x="{x:.1f}" y="{ty+li*LEAD:.1f}" font-family="Crimson Text"{st} font-size="{TS}" fill="{col}">{w}</text>')
            x+=fo.getlength(w)
            if p:
                o.append(f'<text x="{x:.1f}" y="{ty+li*LEAD:.1f}" font-family="Crimson Text" font-size="{TS}" fill="{CREAM}">{p}</text>')
                x+=FR(TS).getlength(p)
            x+=FR(TS).getlength(" ")
    # moldura do vídeo
    o.append(f'<rect x="{VX+1.5}" y="{VY+1.5}" width="{VW-3}" height="{VH-3}" rx="28" ry="28" fill="none" stroke="{GOLD}" stroke-width="3"/>')
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920">{"".join(o)}</svg>'
    open(path+".svg","w").write(svg)
    subprocess.run(["rsvg-convert","-w","1080",path+".svg","-o",path],check=True)
    return dict(lines=len(lines),hdr_top=hy,title_first_cap_top=ty-capH,title_last_base=ty+(n-1)*LEAD,gap_to_video=VY-(ty+(n-1)*LEAD),top_margin=hy)

# máscara arredondada do vídeo
m=Image.new("L",(VW,VH),0); ImageDraw.Draw(m).rounded_rectangle((0,0,VW-1,VH-1),radius=28,fill=255); m.save("tpl/mask.png")

def ts(t):
    h=int(t//3600);mi=int(t%3600//60);s=t%60
    return f"{h}:{mi:02d}:{s:05.2f}"
HDR="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Cap,Poppins,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,5,2,2,120,120,330,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
def clean(t): return re.sub(r"[,.;:]+$","",t)
def chunks(ws):
    out,cur=[],[]
    for wd in ws:
        cur.append(wd); txt=" ".join(clean(x[2]) for x in cur)
        if len(cur)>=3 or len(txt)>=18 or wd[2][-1:] in ".?!,;":
            out.append(cur);cur=[]
    if cur: out.append(cur)
    return out

report={}
for c in CLIPS:
    st,en=c["s"],c["e"]
    ws=[(a-st,b-st,t) for a,b,t in W if a>=st-0.05 and b<=en+0.1]
    L=[]
    CH=chunks(ws)
    for ci,ch in enumerate(CH):
        nxt=CH[ci+1][0][0] if ci+1<len(CH) else 1e9
        for i,wd in enumerate(ch):
            a=max(wd[0],0); b=ch[i+1][0] if i+1<len(ch) else min(wd[1]+0.15,nxt)
            txt=" ".join((r"{\c&H3FD2FF&}"+clean(x[2])+r"{\c&HFFFFFF&}") if j==i else clean(x[2]) for j,x in enumerate(ch))
            L.append(f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{txt}")
    open(f"tpl/{c['id']}.ass","w").write(HDR+"\n".join(L)+"\n")
    report[c["id"]]=overlay(c["title"],f"tpl/{c['id']}_ov.png")
    dur=en-st+0.3
    fc=(f"color=c={BG}:s=1080x1920:r=30:d={dur:.2f}[bg];"
        f"[0:v]crop=864:1080:{CROPX}:0,scale={VW}:{VH}:flags=lanczos,format=rgba[v];"
        f"[1:v]format=gray[m];[v][m]alphamerge[vm];"
        f"[bg][vm]overlay={VX}:{VY}[a];"
        f"[a][2:v]overlay=0:0[b];"
        f"[b]ass=tpl/{c['id']}.ass[out]")
    subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{st-0.1:.2f}","-t",f"{dur:.2f}","-i",SRC,
        "-loop","1","-i","tpl/mask.png","-loop","1","-i",f"tpl/{c['id']}_ov.png",
        "-filter_complex",fc,"-map","[out]","-map","0:a","-t",f"{dur:.2f}",
        "-af",f"afade=t=in:d=0.08,afade=t=out:st={dur-0.25:.2f}:d=0.25",
        "-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p","-r","30",
        "-c:a","aac","-b:a","192k","-movflags","+faststart",f"out2/fe_{c['id']}.mp4"],check=True)
    print("ok",c["id"],round(en-st,1),c["first"],"...",c["last"],flush=True)
print(json.dumps(report,indent=1))
