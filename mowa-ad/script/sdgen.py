import sys,json,base64,subprocess,time,io
from PIL import Image
# usage: sdgen.py endpoint out.png "prompt" ref1 [ref2...]
EP,out,prompt,*refs=sys.argv[1:]
def uri(p):
    im=Image.open(p).convert("RGB"); im.thumbnail((2000,2000)); b=io.BytesIO(); im.save(b,"JPEG",quality=92)
    return "data:image/jpeg;base64,"+base64.b64encode(b.getvalue()).decode()
req={"prompt":prompt,"image_urls":[uri(r) for r in refs],"image_size":{"width":2560,"height":1440},"num_images":1,"enable_safety_checker":True}
open(out+".req.json","w").write(json.dumps(req))
def curl(*a): return subprocess.run(["curl","-sS","-m","120",*a],capture_output=True,text=True).stdout
sub=json.loads(curl("-X","POST",f"https://queue.fal.run/{EP}","-H","Content-Type: application/json","-d","@"+out+".req.json"))
if "request_id" not in sub: print("SUBMIT FAILED",str(sub)[:400]); sys.exit(1)
print("submitted",sub["request_id"],flush=True)
for _ in range(60):
    st=json.loads(curl(sub["status_url"])).get("status")
    if st=="COMPLETED": break
    time.sleep(5)
r=json.loads(curl(sub["response_url"]))
if "images" not in r: print("NO IMAGES",str(r)[:400]); sys.exit(1)
subprocess.run(["curl","-sS","-m","120","-A","Mozilla/5.0","-o",out,r["images"][0]["url"]],check=True); print("saved",out,Image.open(out).size)
