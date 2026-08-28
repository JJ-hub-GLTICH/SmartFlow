import pygame
from algorithms.traffic_optimizer import DIRECTIONS
from simulation.signal import GREEN, YELLOW

BG=(12,18,30); PANEL=(22,32,49); TEXT=(226,234,245); MUTED=(139,152,174); ACCENT=(70,190,255)
GREEN_C=(65,221,132); YELLOW_C=(255,207,72); RED_C=(255,82,82)

class Dashboard:
    def __init__(self):
        pygame.font.init()
        self.title=pygame.font.SysFont('arial',34,bold=True); self.h2=pygame.font.SysFont('arial',21,bold=True)
        self.font=pygame.font.SysFont('arial',18); self.small=pygame.font.SysFont('arial',15); self.tiny=pygame.font.SysFont('arial',13)
    def text(self,surf,msg,pos,color=TEXT,font=None): surf.blit((font or self.font).render(str(msg),True,color),pos)
    def panel(self,surf,rect,title):
        pygame.draw.rect(surf,PANEL,rect,border_radius=14); pygame.draw.rect(surf,(42,57,79),rect,1,border_radius=14)
        self.text(surf,title,(rect.x+18,rect.y+14),ACCENT,self.h2)
    def draw(self,surf,active,traditional,smart):
        w,h=surf.get_size(); surf.fill(BG)
        sim_rect=pygame.Rect(300,80,w-620,h-115); side=pygame.Rect(18,18,260,h-36); right=pygame.Rect(w-300,18,282,h-36)
        self.panel(surf,side,'SMARTFLOW'); self.text(surf,'Adaptive Traffic Management System',(36,60),MUTED,self.small)
        self.text(surf,f'Mode: {active.mode}',(36,94),GREEN_C if active.mode=='SMARTFLOW' else YELLOW_C,self.h2)
        if active.rush_hour: self.text(surf,'RUSH HOUR ACTIVE',(36,121),YELLOW_C,self.font)
        if smart.emergency_active: self.text(surf,f'EMERGENCY PRIORITY ACTIVE', (36,145), RED_C, self.small)
        self.text(surf,'SPACE pause | M mode | R reset',(36,172),MUTED,self.tiny)
        self.text(surf,'H rush hour | E emergency | arrows tune',(36,190),MUTED,self.tiny)
        self.text(surf,f'Speed {active.speed:.1f}x   Intensity {active.intensity:.1f}x',(36,211),TEXT,self.small)
        self.panel(surf,pygame.Rect(28,240,240,265),'LIVE TRAFFIC')
        y=276; stats=active.road_stats()
        for d in DIRECTIONS:
            s=stats[d]; level='HIGH' if s['density']>.66 else 'MEDIUM' if s['density']>.33 else 'LOW'
            color= RED_C if level=='HIGH' else YELLOW_C if level=='MEDIUM' else GREEN_C
            self.text(surf,d,(44,y),TEXT,self.h2)
            self.text(surf,f'{s["total"]} vehicles', (44,y+24), TEXT,self.small)
            self.text(surf,level,(154,y+24), color,self.small)
            self.light(surf,(52,y+52),s['signal']); flow='Flowing' if s['signal']==GREEN else 'Caution' if s['signal']==YELLOW else 'Waiting'
            self.text(surf,f'{s["signal"]} • {flow}',(72,y+43),MUTED,self.small)
            y+=62
        self.panel(surf,pygame.Rect(28,530,240,150),'CURRENT DECISION')
        dec=active.decision; score=dec.scores.get(dec.direction,0)
        self.text(surf,f'Priority Road: {dec.direction}',(44,568),TEXT,self.small)
        self.text(surf,f'Priority Score: {score:.1f}',(44,592),ACCENT,self.small)
        self.text(surf,f'Adaptive Green: {dec.green_time:.1f}s',(44,616),GREEN_C,self.small)
        self.text(surf,'Reason:',(44,640),MUTED,self.tiny); self.text(surf,dec.reason[:34],(44,658),TEXT,self.tiny)
        self.draw_intersection(surf,sim_rect,active)
        self.panel(surf,right,'PERFORMANCE')
        self.metrics_table(surf,right,traditional,smart)
        return sim_rect
    def light(self,surf,pos,state): pygame.draw.circle(surf, GREEN_C if state==GREEN else YELLOW_C if state==YELLOW else RED_C, pos, 7)
    def metrics_table(self,surf,rect,trad,smart):
        self.text(surf,'Metric          Traditional   SmartFlow',(rect.x+18,rect.y+58),MUTED,self.small)
        rows=[('Avg Wait',f'{trad.metrics.avg_wait:.1f}s',f'{smart.metrics.avg_wait:.1f}s'),('Waiting',sum(s['waiting'] for s in trad.road_stats().values()),sum(s['waiting'] for s in smart.road_stats().values())),('Cleared',trad.metrics.cleared,smart.metrics.cleared),('Max Wait',f'{trad.metrics.max_wait:.1f}s',f'{smart.metrics.max_wait:.1f}s'),('Changes',trad.metrics.signal_changes,smart.metrics.signal_changes),('Processed',trad.metrics.cleared+len(trad.vehicles),smart.metrics.cleared+len(smart.vehicles))]
        y=104
        for name,a,b in rows:
            self.text(surf,f'{name:<11}',(rect.x+18,rect.y+y),TEXT,self.small); self.text(surf,str(a),(rect.x+135,rect.y+y),TEXT,self.small); self.text(surf,str(b),(rect.x+224,rect.y+y),GREEN_C,self.small); y+=31
        self.text(surf,'Measured live; results vary by traffic pattern.',(rect.x+18,rect.bottom-52),MUTED,self.tiny)
    def draw_intersection(self,surf,r,sim):
        pygame.draw.rect(surf,(10,16,27),r,border_radius=18)
        pygame.draw.rect(surf,(42,57,79),r,1,border_radius=18)
        old_clip = surf.get_clip(); surf.set_clip(r.inflate(-2,-2))
        cx,cy=r.center; road=(48,55,66); road2=(58,66,79); line=(226,221,176); edge=(205,214,225)
        road_w=196; lane_w=49; inter=196
        # asphalt approaches and subtle shoulders
        pygame.draw.rect(surf,road,(cx-road_w//2,r.y,road_w,r.h))
        pygame.draw.rect(surf,road,(r.x,cy-road_w//2,r.w,road_w))
        pygame.draw.rect(surf,road2,(cx-road_w//2,cy-road_w//2,road_w,road_w))
        # congestion wash inside road only
        stats=sim.road_stats()
        overlays={'NORTH':(cx-road_w//2,r.y,road_w,cy-road_w//2-r.y),'SOUTH':(cx-road_w//2,cy+road_w//2,road_w,r.bottom-cy-road_w//2),'EAST':(cx+road_w//2,cy-road_w//2,r.right-cx-road_w//2,road_w),'WEST':(r.x,cy-road_w//2,cx-road_w//2-r.x,road_w)}
        for d,st in stats.items():
            if st['density']>.66: pygame.draw.rect(surf,(78,48,55),overlays[d])
            elif st['density']>.33: pygame.draw.rect(surf,(64,58,45),overlays[d])
        # road edges
        for x in (cx-road_w//2,cx+road_w//2): pygame.draw.line(surf,edge,(x,r.y),(x,cy-road_w//2),2); pygame.draw.line(surf,edge,(x,cy+road_w//2),(x,r.bottom),2)
        for y in (cy-road_w//2,cy+road_w//2): pygame.draw.line(surf,edge,(r.x,y),(cx-road_w//2,y),2); pygame.draw.line(surf,edge,(cx+road_w//2,y),(r.right,y),2)
        # dashed lane dividers
        def dashed(a,b,vertical=True):
            step=36
            if vertical:
                y=a[1]
                while y<b[1]: pygame.draw.line(surf,line,(a[0],y),(a[0],min(y+18,b[1])),2); y+=step
            else:
                x=a[0]
                while x<b[0]: pygame.draw.line(surf,line,(x,a[1]),(min(x+18,b[0]),a[1]),2); x+=step
        for x in (cx-lane_w,cx,cx+lane_w): dashed((x,r.y),(x,cy-road_w//2)); dashed((x,cy+road_w//2),(x,r.bottom))
        for y in (cy-lane_w,cy,cy+lane_w): dashed((r.x,y),(cx-road_w//2,y),False); dashed((cx+road_w//2,y),(r.right,y),False)
        # stop lines and zebra crossings
        z=10
        stops=sim.stop_lines(r)
        pygame.draw.line(surf,(245,248,255),(cx-road_w//2,stops['NORTH']),(cx-3,stops['NORTH']),4)
        pygame.draw.line(surf,(245,248,255),(cx+3,stops['SOUTH']),(cx+road_w//2,stops['SOUTH']),4)
        pygame.draw.line(surf,(245,248,255),(stops['WEST'],cy+3),(stops['WEST'],cy+road_w//2),4)
        pygame.draw.line(surf,(245,248,255),(stops['EAST'],cy-road_w//2),(stops['EAST'],cy-3),4)
        for i in range(8):
            pygame.draw.rect(surf,(218,226,236),(cx-road_w//2+i*24,cy-road_w//2-34,13,z),border_radius=2)
            pygame.draw.rect(surf,(218,226,236),(cx-road_w//2+i*24,cy+road_w//2+24,13,z),border_radius=2)
            pygame.draw.rect(surf,(218,226,236),(cx-road_w//2-34,cy-road_w//2+i*24,z,13),border_radius=2)
            pygame.draw.rect(surf,(218,226,236),(cx+road_w//2+24,cy-road_w//2+i*24,z,13),border_radius=2)
        pygame.draw.rect(surf,(35,44,56),(cx-inter//2,cy-inter//2,inter,inter),3,border_radius=10)
        # direction arrows
        arrow=(202,211,222)
        def arr(points): pygame.draw.polygon(surf,arrow,points)
        arr([(cx-30,cy-170),(cx-42,cy-145),(cx-34,cy-145),(cx-34,cy-118),(cx-26,cy-118),(cx-26,cy-145),(cx-18,cy-145)])
        arr([(cx+30,cy+170),(cx+42,cy+145),(cx+34,cy+145),(cx+34,cy+118),(cx+26,cy+118),(cx+26,cy+145),(cx+18,cy+145)])
        arr([(cx+170,cy-30),(cx+145,cy-42),(cx+145,cy-34),(cx+118,cy-34),(cx+118,cy-26),(cx+145,cy-26),(cx+145,cy-18)])
        arr([(cx-170,cy+30),(cx-145,cy+42),(cx-145,cy+34),(cx-118,cy+34),(cx-118,cy+26),(cx-145,cy+26),(cx-145,cy+18)])
        for v in sim.vehicles: v.draw(surf)
        positions={'NORTH':(cx-128,cy-128),'SOUTH':(cx+128,cy+128),'EAST':(cx+128,cy-128),'WEST':(cx-128,cy+128)}
        for d,p in positions.items(): self.light(surf,p,sim.signals[d].state); self.text(surf,d,(p[0]-24,p[1]-28),MUTED,self.small)
        if sim.emergency_active: self.text(surf,f'Emergency Route: {sim.emergency_direction}',(r.x+20,r.y+18),RED_C,self.h2)
        surf.set_clip(old_clip)
