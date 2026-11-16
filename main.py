import math
import os
import struct
import zlib

# Draw at twice the delivery resolution for precise, gently antialiased edges.
S = 2
W = H = 1024
N = W * S
pixels = bytearray(N * N * 3)
rider_transform = False

def rider_point(x, y):
    # Enlarge around the saddle and rotate forward into the leap.
    dx, dy = (x-550)*1.25, (y-436)*1.25
    angle = .25
    return (550+dx*math.cos(angle)-dy*math.sin(angle),
            436+dx*math.sin(angle)+dy*math.cos(angle))

def rgb(c):
    return tuple(bytes.fromhex(c)) if isinstance(c, str) else c

def span(y, x0, x1, c):
    if 0 <= y < N:
        a, b = max(0, x0), min(N, x1)
        if b > a:
            pixels[(y*N+a)*3:(y*N+b)*3] = bytes(rgb(c)) * (b-a)

def polygon(points, color):
    if rider_transform:
        points = [rider_point(x,y) for x,y in points]
    pts = [(x*S, y*S) for x,y in points]
    low = max(0, int(min(y for x,y in pts)))
    high = min(N, math.ceil(max(y for x,y in pts)))
    for y in range(low, high):
        yy = y + .5
        crossings = []
        for i, (a,b) in enumerate(pts):
            c,d = pts[(i+1)%len(pts)]
            if (b <= yy < d) or (d <= yy < b):
                crossings.append(a+(yy-b)*(c-a)/(d-b))
        crossings.sort()
        for i in range(0,len(crossings)-1,2):
            span(y, math.ceil(crossings[i]-.5), math.ceil(crossings[i+1]-.5), color)

def ellipse(x,y,rx,ry,c):
    if rider_transform:
        x,y = rider_point(x,y)
        rx *= 1.25
        ry *= 1.25
    for j in range(max(0,int((y-ry)*S)), min(N,math.ceil((y+ry)*S))):
        v = ((j+.5)/S-y)/ry
        d = rx*math.sqrt(max(0,1-v*v))
        span(j,math.ceil((x-d)*S-.5),math.ceil((x+d)*S-.5),c)

def circle(x,y,r,c):
    ellipse(x,y,r,r,c)

def cubic(a,b,c,d,steps=40):
    result=[]
    for i in range(steps+1):
        t=i/steps; u=1-t
        result.append((u*u*u*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t*t*t*d[0],
                       u*u*u*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t*t*t*d[1]))
    return result

def shape(start,segments,c):
    p=[start]; a=start
    for b,cc,d in segments:
        p += cubic(a,b,cc,d)[1:]; a=d
    polygon(p,c)

def stroke(points,width,c):
    r=width/2
    for a,b in zip(points,points[1:]):
        dx=b[0]-a[0]; dy=b[1]-a[1]; length=math.hypot(dx,dy)
        if length:
            nx=-dy*r/length; ny=dx*r/length
            polygon([(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),(b[0]-nx,b[1]-ny),(a[0]-nx,a[1]-ny)],c)
        circle(*a,r,c)
    circle(*points[-1],r,c)

def curve(a,b,c,d,width,color):
    stroke(cubic(a,b,c,d),width,color)

def radial(cx,cy,r,color,strength):
    col=rgb(color)
    for j in range(max(0,int((cy-r)*S)),min(N,int((cy+r)*S)+1)):
        yy=(j+.5)/S-cy
        for i in range(max(0,int((cx-r)*S)),min(N,int((cx+r)*S)+1)):
            dd=math.hypot((i+.5)/S-cx,yy)/r
            if dd < 1:
                a=(1-dd)**2*strength; k=(j*N+i)*3
                for q in range(3): pixels[k+q]=int(pixels[k+q]*(1-a)+col[q]*a)

# Indigo atmosphere, brightening to deep petrol at the sea.
for y in range(N):
    t=y/(N-1)
    c=tuple(int(a+(b-a)*t) for a,b in zip((12,17,49),(9,66,78)))
    span(y,0,N,c)
radial(793,239,290,'ffce64',.27)
radial(426,660,340,'16b7b4',.13)
# Deliberately placed constellation points, with larger four-point stars.
for x,y,r in [(67,90,2),(177,151,2),(305,68,2),(407,164,2),(531,57,2),(631,109,2),(945,79,2),(963,371,2),(851,505,2),(83,403,2),(175,299,2),(323,253,2),(454,306,2),(721,47,2),(73,619,2),(913,603,2),(356,392,1.5),(235,489,1.5),(893,423,1.5),(504,215,1.5),(118,218,1.5),(961,219,1.5)]:
    circle(x,y,r,'c2e9df')
for x,y,r in [(245,102,10),(93,316,8),(443,91,7),(578,233,10),(947,492,9),(359,187,6)]:
    polygon([(x,y-r),(x+2,y-2),(x+r,y),(x+2,y+2),(x,y+r),(x-2,y+2),(x-r,y),(x-2,y-2)],'ffe6a2')
# Monumental moon: an unbroken, readable disc with restrained graphic craters.
for radius, strength in [(350,.035),(290,.055),(235,.09)]:
    radial(794,237,radius,'ffd579',strength)
circle(794,237,174,'ffd36d')
circle(784,225,160,'ffda7c')
shape((674,135),[((720,76),(831,65),(892,133)),((836,108),(751,113),(674,135))],'ffe7a1')
ellipse(861,256,34,46,'f4c260')
ellipse(814,333,23,12,'f3c061')
ellipse(708,218,16,25,'ffe49a')
circle(884,184,12,'f5c363')
# Ocean rolling in long, clean bands.
shape((0,810),[((149,772),(250,862),(397,815)),((602,748),(800,786),(1024,745)),((1024,850),(1024,950),(1024,1024)),((650,1024),(300,1024),(0,1024)),((0,960),(0,880),(0,810))],'075366')
shape((0,888),[((183,821),(311,949),(507,873)),((686,808),(847,854),(1024,828)),((1024,902),(1024,966),(1024,1024)),((650,1024),(300,1024),(0,1024)),((0,980),(0,930),(0,888))],'083b52')
for a,b,c,d in [((0,833),(100,803),(165,841),(210,841)),((564,839),(697,795),(797,817),(863,801)),((751,902),(859,870),(929,888),(1028,864)),((25,971),(156,924),(239,973),(322,946))]:
    curve(a,b,c,d,3,'168293')
# Splash and launch plume behind the fish.
shape((119,870),[((197,806),(245,752),(228,660)),((289,717),(255,790),(307,812)),((353,776),(372,735),(393,710)),((363,793),(417,804),(470,832)),((356,820),(322,863),(291,881)),((245,844),(204,877),(119,870))],'149f a7'.replace(' ',''))
shape((153,861),[((233,813),(253,783),(250,728)),((279,797),(265,837),(309,838)),((339,807),(355,797),(369,784)),((343,837),(340,850),(384,851)),((295,871),(220,879),(153,861))],'75e4d0')
# Sweeping forked tail.
shape((329,721),[((255,688),(193,698),(143,635)),((141,715),(177,770),(257,784)),((218,809),(198,858),(213,897)),((264,853),(328,842),(359,764)),((353,747),(340,733),(329,721))],'ff9c57')
shape((309,749),[((241,734),(193,703),(162,667)),((189,731),(225,759),(290,772)),((282,814),(248,858),(230,872)),((285,845),(325,796),(309,749))],'ffe4a1')
curve((167,669),(197,729),(251,741),(308,758),3,'e66a46')
curve((234,863),(261,832),(282,810),(294,783),3,'e66a46')
# Far fin and dorsal sail.
shape((414,568),[((401,511),(431,443),(470,413)),((472,462),(499,476),(531,483)),((497,510),(459,541),(414,568))],'fa9b50')
curve((436,532),(437,480),(453,451),(465,431),3,'ffe4a0')
# Body silhouette: enormous curved ivory koi with a luminous rim.
body=[((338,658),(419,498),(567,438)),((619,409),(697,409),(714,444)),((739,490),(675,536),(596,579)),((496,635),(434,712),(340,771)),((305,790),(282,779),(285,751)),((289,721),(307,687),(318,677))]
shape((318,677),body,'65e0c7')
body2=[((355,650),(427,510),(571,450)),((626,424),(686,423),(702,449)),((721,484),(660,526),(589,566)),((484,626),(426,703),(336,759)),((313,772),(298,772),(299,750)),((304,720),(319,691),(330,676))]
shape((330,676),body2,'fff0bd')
# Warm underside follows the rising arc.
shape((300,750),[((387,716),(449,618),(571,563)),((628,537),(675,509),(705,471)),((696,519),(625,548),(589,570)),((476,639),(429,711),(336,759)),((314,773),(298,770),(300,750))],'efb76a')
# Distinct koi vermilion patches, designed as broad flowing islands.
shape((344,651),[((362,589),(410,544),(440,526)),((419,576),(466,571),(452,611)),((439,645),(388,639),(377,679)),((363,701),(334,704),(322,718)),((328,690),(334,670),(344,651))],'ef6945')
shape((518,478),[((558,456),(610,429),(654,434)),((632,452),(651,470),(625,485)),((602,499),(579,477),(560,499)),((543,511),(529,501),(518,478))],'f17b47')
shape((474,603),[((489,570),(522,553),(551,548)),((540,570),(551,582),(525,597)),((501,607),(485,619),(474,603))],'ec7545')
# A few curved scales give craft without disrupting the silhouette.
for x,y in [(405,637),(424,615),(447,593),(466,570),(485,548),(504,528),(428,654),(448,631),(468,611)]:
    curve((x-7,y-3),(x-2,y+7),(x+7,y+5),(x+11,y-3),1.6,'dca969')
# Near pectoral fin streams backward in the current.
shape((579,536),[((561,568),(560,628),(519,665)),((577,657),(625,610),(628,561)),((616,543),(600,536),(579,536))],'ff9c58')
shape((592,551),[((588,588),(566,629),(540,649)),((585,625),(608,591),(611,557)),((605,552),(599,550),(592,551))],'ffd58e')
curve((601,555),(601,587),(573,626),(548,641),2,'e77747')
# Face: one dark expressive eye, gill, lips, two streaming whiskers.
curve((635,478),(619,494),(616,511),(622,521),3,'bd874f')
circle(671,454,10,'133b49')
circle(674,451,3.5,'ffffff')
curve((697,479),(705,479),(709,470),(711,466),3,'9b6d43')
curve((702,481),(746,497),(773,476),(785,456),3,'ffe4a0')
curve((695,490),(734,522),(769,517),(785,503),2.5,'f8cf84')
# Tiny rider: a fluffy tail, small boots and a bright angular fox.
rider_transform = True
shape((535,425),[((510,430),(493,412),(500,392)),((502,376),(518,370),(529,378)),((508,381),(514,401),(540,400)),((556,406),(552,420),(535,425))],'e98b40')
shape((500,392),[((498,384),(512,372),(529,378)),((517,382),(514,388),(518,394)),((513,398),(508,398),(500,392))],'fff1cd')
polygon([(535,397),(553,393),(572,419),(567,438),(556,439),(555,418),(541,418)],'d87937')
polygon([(535,412),(545,412),(539,441),(526,448),(518,444),(531,434)],'163e49')
polygon([(560,426),(569,426),(579,442),(576,448),(562,443)],'163e49')
# Fox ears and head, looking eagerly up to the moon.
polygon([(532,377),(523,347),(543,358),(562,347),(566,321),(582,343),(590,360),(577,386),(550,394)],'f9a34c')
polygon([(529,354),(535,368),(542,361)],'713e3c')
polygon([(569,333),(568,352),(578,345)],'713e3c')
polygon([(545,376),(555,365),(565,374),(586,360),(580,379),(558,390)],'fff1cf')
polygon([(583,359),(591,357),(588,365)],'153b49')
curve((565,358),(567,356),(569,356),(571,357),2.5,'243a47')
# Scarf ribbons sweep to the left, making the leap's direction unmistakable.
shape((554,391),[((505,390),(478,344),(437,357)),((405,372),(381,351),(365,330)),((381,370),(410,392),(443,374)),((485,359),(511,414),(550,403)),((553,400),(555,396),(554,391))],'f34850')
shape((540,396),[((501,397),(474,432),(437,407)),((457,440),(493,433),(523,413)),((534,411),(546,410),(550,404)),((547,401),(544,398),(540,396))],'c92c49')
polygon([(543,386),(558,384),(563,394),(550,404),(539,399)],'ff5a56')
rider_transform = False
# Suspended water jewels placed along the launch arc.
def drop(x,y,size,angle):
    ux,uy=math.cos(angle),math.sin(angle)
    vx,vy=-uy,ux
    p=[]
    for a,b in [(0,-1.8),(-.65,-.1),(-.7,.55),(0,.9),(.7,.55),(.65,-.1)]:
        p.append((x+size*(a*vx+b*ux),y+size*(a*vy+b*uy)))
    polygon(p,'8bf5dd')
    circle(x-2,y-2,size*.19,'efffe5')
for d in [(194,574,12,-1),(255,511,8,-.9),(319,443,11,-.65),(405,399,6,-.6),(749,570,13,-1.4),(700,647,7,-1.1),(446,754,10,-1),(109,770,8,-1.3),(385,852,6,-1),(815,555,5,-1),(291,601,5,-.6)]: drop(*d)
for d in [(750,420,7,-1.1),(779,394,9,-1.2),(815,438,6,-1.4),(837,482,8,-1.3),(790,530,5,-1.2)]: drop(*d)
for x,y,r in [(181,809,4),(146,851,3),(333,883,4),(407,810,3),(229,623,3),(741,617,3),(296,472,3)]: circle(x,y,r,'c8ffe7')
# Broad, broken moon reflections in the dark foreground.
for x,y,rx,ry in [(803,852,51,2),(765,876,33,2),(825,899,65,3),(779,928,49,2),(852,956,81,3),(777,984,38,2)]: ellipse(x,y,rx,ry,'a99e63')
# Short irregular glints form a shimmering column directly under the moon.
for i in range(24):
    y = 792+i*9
    x = 794+math.sin(i*2.3)*(8+i*.55)
    width = 12+i*.8+(i%4)*4
    ellipse(x,y,width,1+(i%3)*.35,'d4b568')
    if i%3 == 0:
        ellipse(x+width+10,y+3,5,1,'f7d583')

# Resolve the supersampled RGB canvas and encode PNG without external libraries.
raw = bytearray()
for y in range(H):
    raw.append(0)  # PNG filter: none
    for x in range(W):
        k=((y*2)*N+x*2)*3
        for c in range(3):
            raw.append((pixels[k+c]+pixels[k+3+c]+pixels[k+N*3+c]+pixels[k+N*3+3+c]+2)//4)

def chunk(kind,data):
    return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)

png = b'\x89PNG\r\n\x1a\n'
png += chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0))
png += chunk(b'IDAT',zlib.compress(raw,9))
png += chunk(b'IEND',b'')
outdir=os.environ.get('MAKEFUN_OUTPUT_DIR','/output')
os.makedirs(outdir,exist_ok=True)
with open(os.path.join(outdir,'entry.png'),'wb') as f:
    f.write(png)
