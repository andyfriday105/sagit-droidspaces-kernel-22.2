#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mkboot.py - dependency-free Android traditional boot image (header v0) tool.
Commands: info <img> | unpack <img> <dir> | repack --orig <stock> --kernel <Image.gz-dtb> --out <new> [--ramdisk <f>]
Keeps every header field of the ORIGINAL image and only swaps the kernel (+ id).
"""
import sys, os, struct, hashlib, json
MAGIC = b"ANDROID!"
HDR_FMT = struct.Struct("<8s" + "I" * 10 + "16s" + "512s" + "32s" + "1024s")
FIELDS = ["magic","kernel_size","kernel_addr","ramdisk_size","ramdisk_addr","second_size","second_addr","tags_addr","page_size","header_version","os_version","name","cmdline","id","extra_cmdline"]
def align(n,p): return (n+p-1)//p*p
def read_header(data):
    vals=list(HDR_FMT.unpack_from(data,0)); h=dict(zip(FIELDS,vals))
    if h["magic"]!=MAGIC: raise SystemExit("bad magic %r"%h["magic"])
    if h["page_size"]==0: h["page_size"]=4096
    for k in ("name","cmdline","extra_cmdline"): h[k]=h[k].split(b"\x00",1)[0].decode("latin1")
    return h
def sections(data,h):
    p=h["page_size"]; ko=p; ro=ko+align(h["kernel_size"],p); so=ro+align(h["ramdisk_size"],p)
    return data[ko:ko+h["kernel_size"]], data[ro:ro+h["ramdisk_size"]], data[so:so+h["second_size"]]
def cmd_info(path):
    h=read_header(open(path,"rb").read())
    print("header_version:",h["header_version"],"page_size:",h["page_size"])
    print("kernel size=%d addr=0x%08x"%(h["kernel_size"],h["kernel_addr"]))
    print("ramdisk size=%d addr=0x%08x"%(h["ramdisk_size"],h["ramdisk_addr"]))
    print("second size=%d tags=0x%08x os=0x%08x"%(h["second_size"],h["tags_addr"],h["os_version"]))
    print("cmdline:",repr(h["cmdline"]))
def cmd_unpack(path,outdir):
    data=open(path,"rb").read(); h=read_header(data); k,r,s=sections(data,h)
    os.makedirs(outdir,exist_ok=True)
    open(os.path.join(outdir,"kernel"),"wb").write(k); open(os.path.join(outdir,"ramdisk"),"wb").write(r); open(os.path.join(outdir,"second"),"wb").write(s)
    print("unpacked kernel=%d ramdisk=%d second=%d"%(len(k),len(r),len(s)))
def cmd_repack(orig,kp,out,rp=None):
    data=open(orig,"rb").read(); h=read_header(data); _k,r0,s0=sections(data,h)
    k=open(kp,"rb").read(); r=open(rp,"rb").read() if rp else r0; s=s0; p=h["page_size"]
    hdr=bytearray(align(HDR_FMT.size,p)); hdr[0:HDR_FMT.size]=data[0:HDR_FMT.size]
    struct.pack_into("<I",hdr,8,len(k)); struct.pack_into("<I",hdr,16,len(r)); struct.pack_into("<I",hdr,24,len(s))
    sha=hashlib.sha1(k+r+s).digest(); hdr[576:608]=sha+b"\x00"*(32-len(sha))
    buf=bytes(hdr)+k+b"\x00"*(align(len(k),p)-len(k))+r+b"\x00"*(align(len(r),p)-len(r))+s+b"\x00"*(align(len(s),p)-len(s))
    open(out,"wb").write(buf); print("repacked -> %s (%d bytes) kernel=%d ramdisk=%d page=%d"%(out,len(buf),len(k),len(r),p))
def main(a):
    if len(a)<2: print(__doc__); return 1
    c=a[1]
    if c=="info" and len(a)==3: cmd_info(a[2])
    elif c=="unpack" and len(a)==4: cmd_unpack(a[2],a[3])
    elif c=="repack":
        d=dict(zip(a[2::2],a[3::2]))
        if not all(x in d for x in ("--orig","--kernel","--out")): raise SystemExit("missing args")
        cmd_repack(d["--orig"],d["--kernel"],d["--out"],d.get("--ramdisk"))
    else: print(__doc__); return 1
    return 0
if __name__=="__main__": sys.exit(main(sys.argv))
