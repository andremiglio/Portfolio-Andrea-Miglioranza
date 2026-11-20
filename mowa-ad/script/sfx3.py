import numpy as np, wave
SR=44100; D=18.28; N=int(SR*D)
rng=np.random.default_rng(7)
out=np.zeros((N,2),np.float32)
def t(d): return np.arange(int(SR*d))/SR
def lp(x,fc):  # one-pole lowpass
    a=np.exp(-2*np.pi*fc/SR); y=np.zeros_like(x); s=0.0
    for i,v in enumerate(x): s=a*s+(1-a)*v; y[i]=s
    return y
def hp(x,fc): return x-lp(x,fc)
def env(n,a,r):
    e=np.ones(n); na=int(a*SR); nr=int(r*SR)
    if na>0: e[:na]=np.linspace(0,1,na)
    if nr>0: e[-nr:]*=np.linspace(1,0,nr)
    return e
def add(x,at,gain=1.0,pan=0.0):
    i=int(at*SR); x=x[:max(0,N-i)]; 
    if len(x)==0: return
    out[i:i+len(x),0]+=x*gain*(1-0.5*max(0,pan)); out[i:i+len(x),1]+=x*gain*(1+0.5*min(0,pan)) if False else x*gain*(1-0.5*max(0,-pan))
def noise(d): return rng.standard_normal(int(SR*d)).astype(np.float32)
def whoosh(d=0.45):
    n=noise(d); tt=t(d); x=hp(lp(n,3500),300)
    return x*np.sin(np.pi*tt/d)**2*0.9
def bip(f=1800,d=0.09):
    tt=t(d); return np.sin(2*np.pi*f*tt)*env(len(tt),0.003,0.03)
def chirp(f0,f1,d):
    tt=t(d); f=f0+(f1-f0)*tt/d; ph=2*np.pi*np.cumsum(f)/SR; return np.sin(ph)*env(len(tt),0.01,d*0.4)
def thump(d=0.35):
    tt=t(d); f=95*np.exp(-tt*9)+38; return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*10)+0.25*lp(noise(d),400)*np.exp(-tt*25)
# ---- ambient bed (outdoor wind) whole video
wind=lp(noise(D),500)*0.10; wind=wind*(0.7+0.3*np.sin(2*np.pi*t(D)*0.15)); add(wind,0,0.5)
# birds in first part and robot part
for at,f in [(1.0,3300),(1.15,3700),(2.6,3000),(2.75,3500),(5.2,3600),(8.0,3200),(8.12,3600),(12.2,3400),(15.2,3300)]:
    add(chirp(f,f*1.25,0.09)*0.05,at,1.0)
# ---- van: 0 - 4.41
d=1.4; eng=lp(noise(d),220)*4; eng*=np.linspace(0.15,1,len(eng))**1.5; eng+=0.5*np.sin(2*np.pi*(52+22*np.linspace(0,1,len(eng)))*t(d)); add(eng*0.45*env(len(eng),0.05,0.1),0.05)
sq=hp(lp(noise(0.55),5200),2800)*np.linspace(1,0.2,int(SR*0.55)); sq+=0.4*chirp(3800,2600,0.5)[:len(sq)] if False else 0; add(sq*0.35*env(len(sq),0.04,0.15),1.0)
d=1.8; idle=lp(noise(d),160)*4+0.35*np.sin(2*np.pi*46*t(d)); idle*=1+0.12*np.sin(2*np.pi*t(d)*9); add(idle*0.30*env(len(idle),0.15,0.25),1.5)
d=1.45; pa=lp(noise(d),260)*4*np.linspace(0.6,1,int(SR*d))+0.5*np.sin(2*np.pi*(48+30*np.linspace(0,1,int(SR*d)))*t(d)); add(pa*0.42*env(len(pa),0.1,0.6),3.0)
# ---- box opens (starts 4.41)
add(thump()*0.8,4.46)
add(whoosh(0.35)*0.5,5.05)                 # flaps lift
nz=hp(lp(noise(0.5),4000),800)*np.exp(-t(0.5)*7); add(nz*0.25,5.05)  # cardboard rustle
add(bip(1800,0.11)*0.55,5.85); add(bip(2400,0.14)*0.45,6.0)           # bip
sw=chirp(300,1500,0.8)*0.18; add(sw,5.8)                              # power-up rise
# ---- robot section hum 6.81 -> 16.81
d=6.6; tt=t(d); hum=(np.sin(2*np.pi*118*tt)+0.5*np.sin(2*np.pi*236*tt)+0.25*np.sin(2*np.pi*354*tt))*(1+0.06*np.sin(2*np.pi*tt*4.5))
hum=lp(hum,900)*0.10; hum+=lp(noise(d),600)*0.06
add(hum*env(len(hum),0.6,0.9),6.85)
add(bip(1800,0.1)*0.5,6.9)
# cut whooshes
for c,g in [(8.81,0.45),(10.31,0.4),(11.81,0.4),(13.31,0.55)]:
    add(whoosh(0.4)*g,c-0.2)
# grass-cut hiss during r3/r4
gh=hp(lp(noise(3.0),7000),2500)*0.05; add(gh*env(len(gh),0.3,0.3),10.3)
# ---- aerial pad 16.81 -> end
d=D-13.31; tt=t(d); pad=sum(np.sin(2*np.pi*f*tt)*a for f,a in [(131,0.5),(196,0.35),(262,0.3),(330,0.25),(392,0.2)]); pad*=np.linspace(0.2,1,len(tt))**0.8*0.10
add(pad*env(len(pad),1.2,1.6),13.31)
for f,at in [(1568,13.5),(2093,13.68),(2637,13.86)]: add(bip(f,0.35)*np.exp(-t(0.35)*7)*0.18,at)
# master: soft limiter + fade out
out=np.tanh(out*1.1); out*=np.minimum(1,(D-t(D))/1.2)[:,None] if False else 1
fade=np.minimum(1.0,(D-np.arange(N)/SR)/1.2); out*=fade[:,None]
pk=np.abs(out).max(); print('peak',pk); out=out/max(pk,1e-6)*0.89
w=wave.open('sfx3.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype('<i2').tobytes()); w.close()
