import sys,json,base64,subprocess,time,io
from PIL import Image
# usage: clipdraft.py out.mp4 endpoint "prompt" start end duration resolution
out,EP,prompt,start,end,dur,res=sys.argv[1:8]
def uri(p):
    im=Image.open(p).convert("RGB"); im.thumbnail((1920,1080)); b=io.BytesIO(); im.save(b,"JPEG",quality=92)
    return "data:image/jpeg;base64,"+base64.b64encode(b.getvalue()).decode()
req={"prompt":prompt,"image_url":uri(start),"duration":dur,"resolution":res,"aspect_ratio":"16:9","generate_audio":True}
if end!="none": req["end_image_url"]=uri(end)
open(out+".req.json","w").write(json.dumps(req))
def curl(*a): return subprocess.run(["curl","-sS","-m","120",*a],capture_output=True,text=True).stdout
sub=json.loads(curl("-X","POST",f"https://queue.fal.run/{EP}","-H","Content-Type: application/json","-d","@"+out+".req.json"))
if "request_id" not in sub: print("SUBMIT FAILED",sub); sys.exit(1)
open(out+".job","w").write(json.dumps(sub)); print("submitted",sub["request_id"],flush=True)
for _ in range(100):
    st=json.loads(curl(sub["status_url"])).get("status")
    if st=="COMPLETED": break
    time.sleep(10)
r=json.loads(curl(sub["response_url"])); open(out+".res.json","w").write(json.dumps(r))
subprocess.run(["curl","-sS","-m","180","-A","Mozilla/5.0","-o",out,r["video"]["url"]],check=True); print("saved",out)
