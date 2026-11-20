import sys,json,base64,subprocess,time,io
from PIL import Image
# usage: refvid.py out.mp4 endpoint "prompt" duration resolution ref1 [ref2...]
out,EP,prompt,dur,res,*refs=sys.argv[1:]
def uri(p):
    im=Image.open(p).convert("RGB"); im.thumbnail((1920,1920)); b=io.BytesIO(); im.save(b,"JPEG",quality=92)
    return "data:image/jpeg;base64,"+base64.b64encode(b.getvalue()).decode()
req={"prompt":prompt,"image_urls":[uri(r) for r in refs],"duration":dur,"resolution":res,"aspect_ratio":"16:9","generate_audio":True,"draft":True}
open(out+".req.json","w").write(json.dumps(req))
def curl(*a): return subprocess.run(["curl","-sS","-m","120",*a],capture_output=True,text=True).stdout
sub=json.loads(curl("-X","POST",f"https://queue.fal.run/{EP}","-H","Content-Type: application/json","-d","@"+out+".req.json"))
if "request_id" not in sub: print("SUBMIT FAILED",str(sub)[:500]); sys.exit(1)
open(out+".job","w").write(json.dumps(sub)); print("submitted",sub["request_id"],flush=True)
for _ in range(100):
    st=json.loads(curl(sub["status_url"])).get("status")
    if st=="COMPLETED": break
    time.sleep(8)
r=json.loads(curl(sub["response_url"])); open(out+".res.json","w").write(json.dumps(r))
if "video" not in r: print("NO VIDEO",str(r)[:600]); sys.exit(1)
subprocess.run(["curl","-sS","-m","180","-A","Mozilla/5.0","-o",out,r["video"]["url"]],check=True); print("saved",out,{k:v for k,v in r.items() if k!="video"})
