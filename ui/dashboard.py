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
        pygame.draw.rect(surf,(15,23,36),r,border_radius=18); cx,cy=r.center; road=(55,62,74)
        pygame.draw.rect(surf,road,(cx-78,r.y,156,r.h)); pygame.draw.rect(surf,road,(r.x,cy-78,r.w,156))
        stats=sim.road_stats()
        for d,s in stats.items():
            if s['density']>.66:
                overlay={'NORTH':(cx-78,r.y,76,cy-r.y-86),'SOUTH':(cx+2,cy+86,76,r.bottom-cy-86),'EAST':(cx+86,cy-78,r.right-cx-86,76),'WEST':(r.x,cy+2,cx-r.x-86,76)}[d]
                pygame.draw.rect(surf,(86,55,62),overlay,border_radius=8)
        for off in (-24,24): pygame.draw.line(surf,(210,210,150),(cx+off,r.y),(cx+off,r.bottom),2); pygame.draw.line(surf,(210,210,150),(r.x,cy+off),(r.right,cy+off),2)
        pygame.draw.rect(surf,(35,45,58),(cx-78,cy-78,156,156)); pygame.draw.rect(surf,(95,110,126),(cx-86,cy-86,172,172),3)
        for v in sim.vehicles: v.draw(surf)
        positions={'NORTH':(cx-112,cy-112),'SOUTH':(cx+112,cy+112),'EAST':(cx+112,cy-112),'WEST':(cx-112,cy+112)}
        for d,p in positions.items(): self.light(surf,p,sim.signals[d].state); self.text(surf,d,(p[0]-24,p[1]-28),MUTED,self.small)
        if sim.emergency_active: self.text(surf,f'Emergency Route: {sim.emergency_direction}',(r.x+20,r.y+18),RED_C,self.h2)
