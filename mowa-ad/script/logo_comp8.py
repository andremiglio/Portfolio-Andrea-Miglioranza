import cv2, numpy as np, subprocess, sys, json
S=1284/1000.0   # displayed(1000-wide) -> native
SRC='clips/aerial_final.mp4'; OUT=sys.argv[1]; MODE=sys.argv[2] if len(sys.argv)>2 else 'light'
cap=cv2.VideoCapture(SRC); frames=[]
while True:
    ok,f=cap.read()
    if not ok: break
    frames.append(f)
N=len(frames); h,w=frames[0].shape[:2]; print(N,w,h)
# logo alpha
lg=cv2.imread('../images/28.webp') if False else None
from PIL import Image
_I=Image.open('../images/28.webp').convert('RGBA'); _B=Image.new('RGBA',_I.size,(255,255,255,255)); _B.alpha_composite(_I); im=np.array(_B.convert('RGB')).astype(np.float32)
mn=im.min(axis=2); a=np.clip((215-mn)/110.0,0,1)
a[:300,1672:]=0
a=a[235:425,265:1700]
lh,lw=a.shape
# ground mask on frame0 (lawn polygon, native coords)
poly0=(np.array([[120,330],[330,120],[560,150],[800,330],[700,520],[200,560]])*1.0).astype(np.float32)
poly0=(np.array([[60,330],[300,60],[560,90],[760,260],[760,420],[600,520],[150,560]])*S/1.0).astype(np.float32)
# logo quad on frame0 (disp coords -> native)
quad0=(np.array([[150,205],[705,198],[735,292],[115,300]])*S).astype(np.float32)
src_rect=np.array([[0,0],[lw,0],[lw,lh],[0,lh]],np.float32)
Cs_d=np.load('logo/Cs_direct.npy')
Qend=np.array([[60,185],[990,182],[1018,312],[28,316]],np.float32)
Hh=[cv2.getPerspectiveTransform(quad0,Cs_d[t].astype(np.float32)) for t in range(N)]
Q0=cv2.perspectiveTransform(Qend.reshape(-1,1,2),np.linalg.inv(Hh[-1])).reshape(-1,2)
Cs=np.array([cv2.perspectiveTransform(Q0.reshape(-1,1,2).astype(np.float32),Hh[t]).reshape(-1,2) for t in range(N)])
print('quad t0',Cs[0].round(0).tolist(),'end',Cs[-1].round(0).tolist())
P0=cv2.getPerspectiveTransform(src_rect,quad0)

fps=24; t0,t1=-2.0,-1.0
out=[]
fps=24; t0,t1=-2.0,-1.0
for t in range(N):
    Wt=cv2.getPerspectiveTransform(src_rect,Cs[t].astype(np.float32))
    al=cv2.warpPerspective(a,Wt,(w,h),flags=cv2.INTER_LINEAR)
    # reveal left->right in logo space via warped x-ramp
    xs=np.tile(np.arange(lw,dtype=np.float32),(lh,1))
    xr=cv2.warpPerspective(xs,Wt,(w,h),flags=cv2.INTER_LINEAR,borderValue=-1)
    p=np.clip(((t/fps)-t0)/(t1-t0),0,1); p=p*p*(3-2*p)
    edge=p*(lw+120)-60
    rev=np.clip((edge-xr)/60.0,0,1)
    al=al*rev
    al=cv2.GaussianBlur(al,(0,0),1.1)
    f=frames[t].astype(np.float32)/255
    hsv=cv2.cvtColor(frames[t],cv2.COLOR_BGR2HSV).astype(np.float32)
    if MODE=='light':
        v2=np.clip(hsv[...,2]*1.42+24,0,255); s2=hsv[...,1]*0.78; hh=hsv[...,0]-1.5
    else:
        v2=hsv[...,2]*0.66; s2=hsv[...,1]*1.05; hh=hsv[...,0]
    hsv2=np.dstack([hh,s2,v2]); alt=cv2.cvtColor(np.clip(hsv2,0,255).astype(np.uint8),cv2.COLOR_HSV2BGR).astype(np.float32)/255
    o=f*(1-al[...,None])+alt*al[...,None]
    hs=cv2.cvtColor(frames[t],cv2.COLOR_BGR2HSV)
    wm=((hs[...,1]<45)&(hs[...,2]>170)).astype(np.uint8)
    wm=cv2.morphologyEx(wm,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    nc,lab,st,_=cv2.connectedComponentsWithStats(wm)
    rm=np.zeros((h,w),np.float32)
    for i in range(1,nc):
        if st[i,4]>400: rm[lab==i]=1
    rm=cv2.GaussianBlur(cv2.dilate(rm,np.ones((7,7),np.uint8)),(0,0),1.5)
    o=o*(1-rm[...,None])+f*rm[...,None]
    out.append((np.clip(o,0,1)*255).astype(np.uint8))
cv2.imwrite(OUT.replace('.mp4','_f0.png'),out[0]); cv2.imwrite(OUT.replace('.mp4','_fmid.png'),out[int(3.2*fps)]); cv2.imwrite(OUT.replace('.mp4','_fend.png'),out[-1])
raw=OUT.replace('.mp4','_raw.avi'); vw=cv2.VideoWriter(raw,cv2.VideoWriter_fourcc(*'FFV1'),fps,(w,h))
for o in out: vw.write(o)
vw.release()
subprocess.run(['ffmpeg','-y','-v','error','-i',raw,'-c:v','libx264','-crf','15','-preset','slow','-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709',OUT],check=True)
print('done')


