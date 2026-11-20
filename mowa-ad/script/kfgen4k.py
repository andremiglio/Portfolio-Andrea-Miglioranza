import sys,json,base64,subprocess,time,io
from PIL import Image
# usage: kfgen.py out.png "prompt" ref1 [ref2...]
out,prompt,*refs=sys.argv[1:]
def uri(p):
    im=Image.open(p).convert("RGB"); im.thumbnail((2000,2000)); b=io.BytesIO(); im.save(b,"JPEG",quality=90)
    return "data:image/jpeg;base64,"+base64.b64encode(b.getvalue()).decode()
req={"prompt":prompt,"image_urls":[uri(r) for r in refs],"aspect_ratio":"16:9","resolution":"4K","num_images":1,"output_format":"png"}
open(out+".req.json","w").write(json.dumps(req))
def curl(*a): return subprocess.run(["curl","-sS","-m","90",*a],capture_output=True,text=True).stdout
sub=json.loads(curl("-X","POST","https://queue.fal.run/fal-ai/nano-banana-pro/edit","-H","Content-Type: application/json","-d","@"+out+".req.json"))
rid=sub["request_id"]; open(out+".job","w").write(rid)
for _ in range(60):
    st=json.loads(curl(f"https://queue.fal.run/fal-ai/nano-banana-pro/requests/{rid}/status")).get("status")
    if st=="COMPLETED": break
    time.sleep(5)
res=json.loads(curl(f"https://queue.fal.run/fal-ai/nano-banana-pro/requests/{rid}"))
url=res["images"][0]["url"]
subprocess.run(["curl","-sS","-m","90","-A","Mozilla/5.0","-o",out,url],check=True)
im=Image.open(out); im.thumbnail((1400,800)); im.convert("RGB").save(out.replace(".png","_prev.jpg"),quality=88)
print(out,"ok")
