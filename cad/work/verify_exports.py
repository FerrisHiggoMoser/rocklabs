import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pydeps"))
from cadquery import importers
from OCP.StlAPI import StlAPI_Reader
from OCP.TopoDS import TopoDS_Shape

out=os.path.abspath(os.path.join(os.path.dirname(__file__),"..","outputs","centered_two_versions"))
prefixes=("centered_rounded_bezel","centered_borderless")
for prefix in prefixes:
    for suffix in ("top.step","bottom.step","assembly.step"):
        fn=f"{prefix}_{suffix}"
        obj=importers.importStep(os.path.join(out,fn))
        bb=obj.val().BoundingBox()
        print(fn,"solids",obj.solids().size(),"valid",obj.val().isValid(),
              "bbox",tuple(round(v,2) for v in (bb.xlen,bb.ylen,bb.zlen)))
    for suffix in ("top.stl","bottom.stl"):
        fn=f"{prefix}_{suffix}"; shape=TopoDS_Shape()
        ok=StlAPI_Reader().Read(shape,os.path.join(out,fn))
        print(fn,"read",bool(ok),"null",shape.IsNull(),"bytes",os.path.getsize(os.path.join(out,fn)))
