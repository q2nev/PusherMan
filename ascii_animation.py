import moving_ascii
import time
import os

ims= dict()


with open("moving_ascii.xml") as f:
        xml_file = f.read()

success, ascii  = moving_ascii.obj_wrapper(xml_file)

if not success:
    print "NO SUCCESS!"
    exit()

for i in ascii.im:
    nomen = i.attrs["nomen"]
    ims[nomen] = i

def print_animation(im_name):
    ct =0
    i = ims[im_name]
    pts = dict()
    for pt in i.part:
        pts[ct]=pt
        ct+=1
    ct=0
    while ct in pts:
        print pts[ct].value
        time.sleep(.2)
        ct+=1
        os.system('cls')


print_animation('die')