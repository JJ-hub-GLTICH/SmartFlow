import pygame
from algorithms.traffic_optimizer import DIRECTIONS
from simulation.signal import GREEN, YELLOW

BG=(12,18,30); PANEL=(22,32,49); TEXT=(226,234,245); MUTED=(139,152,174); ACCENT=(70,190,255)
GREEN_C=(65,221,132); YELLOW_C=(255,207,72); RED_C=(255,82,82)

class Dashboard:
    def __init__(self):
        pygame.font.init()
        self.title=pygame.font.SysFont('arial',34,bold=True); self.h2=pygame.font.SysFont('arial',20,bold=True)
        self.font=pygame.font.SysFont('arial',16); self.small=pygame.font.SysFont('arial',14)
    def text(self,surf,msg,pos,color=TEXT,font=None): surf.blit((font or self.font).render(str(msg),True,color),pos)
    def panel(self,surf,rect,title):
        pygame.draw.rect(surf,PANEL,rect,border_radius=14); pygame.draw.rect(surf,(42,57,79),rect,1,border_radius=14)
        self.text(surf,title,(rect.x+18,rect.y+14),ACCENT,self.h2)
    def draw(self,surf,active,traditional,smart):
        w,h=surf.get_size(); surf.fill(BG)
        sim_rect=pygame.Rect(300,80,w-620,h-115); side=pygame.Rect(18,18,260,h-36); right=pygame.Rect(w-300,18,282,h-36)
        self.panel(surf,side,'SMARTFLOW'); self.text(surf,'Adaptive Traffic Management System',(36,60),MUTED,self.small)
        self.text(surf,f'Mode: {active.mode}',(36,96),GREEN_C if active.mode=='SMARTFLOW' else YELLOW_C,self.h2)
        self.text(surf,'Controls: SPACE pause | M mode | R reset',(36,130),MUTED,self.small)
        self.text(surf,'UP/DOWN speed  LEFT/RIGHT intensity',(36,150),MUTED,self.small)
        self.text(surf,f'Speed {active.speed:.1f}x   Intensity {active.intensity:.1f}x',(36,180),TEXT,self.font)
        self.panel(surf,pygame.Rect(28,220,240,250),'LIVE TRAFFIC')
        y=258; stats=active.road_stats()
        for d in DIRECTIONS:
            s=stats[d]; level='HIGH' if s['density']>.66 else 'MEDIUM' if s['density']>.33 else 'LOW'
            self.text(surf,f'{d:<6} {s["total"]:>2} vehicles', (44,y), TEXT)
            self.text(surf,level,(188,y), RED_C if level=='HIGH' else YELLOW_C if level=='MEDIUM' else GREEN_C)
            self.light(surf,(56,y+30),s['signal']); self.text(surf,f'{s["signal"]}  wait {s["avg_wait"]:.1f}s',(78,y+22),MUTED,self.small)
            y+=56
        self.panel(surf,pygame.Rect(28,495,240,170),'CURRENT DECISION')
        dec=active.decision; self.text(surf,f'Priority Road: {dec.direction}',(44,535),TEXT,self.font)
        self.text(surf,f'Green Time: {dec.green_time:.1f}s',(44,562),GREEN_C,self.font)
        self.text(surf,'Reason:',(44,594),MUTED,self.small); self.text(surf,dec.reason[:31],(44,614),TEXT,self.small)
        self.draw_intersection(surf,sim_rect,active)
        self.panel(surf,right,'PERFORMANCE')
        self.metrics_table(surf,right,traditional,smart)
        return sim_rect
    def light(self,surf,pos,state): pygame.draw.circle(surf, GREEN_C if state==GREEN else YELLOW_C if state==YELLOW else RED_C, pos, 7)
    def metrics_table(self,surf,rect,trad,smart):
        self.text(surf,'Metric          Traditional   SmartFlow',(rect.x+18,rect.y+58),MUTED,self.small)
        rows=[('Avg Wait',f'{trad.metrics.avg_wait:.1f}s',f'{smart.metrics.avg_wait:.1f}s'),('Waiting',sum(s['waiting'] for s in trad.road_stats().values()),sum(s['waiting'] for s in smart.road_stats().values())),('Cleared',trad.metrics.cleared,smart.metrics.cleared),('Max Wait',f'{trad.metrics.max_wait:.1f}s',f'{smart.metrics.max_wait:.1f}s'),('Changes',trad.metrics.signal_changes,smart.metrics.signal_changes)]
        y=104
        for name,a,b in rows:
            self.text(surf,f'{name:<11}',(rect.x+18,rect.y+y)); self.text(surf,str(a),(rect.x+135,rect.y+y)); self.text(surf,str(b),(rect.x+224,rect.y+y),GREEN_C); y+=34
        self.text(surf,'Metrics are measured from the running simulation.',(rect.x+18,rect.bottom-52),MUTED,self.small)
    def draw_intersection(self,surf,r,sim):
        pygame.draw.rect(surf,(15,23,36),r,border_radius=18); cx,cy=r.center; road=(55,62,74)
        pygame.draw.rect(surf,road,(cx-78,r.y,156,r.h)); pygame.draw.rect(surf,road,(r.x,cy-78,r.w,156))
        for off in (-24,24): pygame.draw.line(surf,(210,210,150),(cx+off,r.y),(cx+off,r.bottom),2); pygame.draw.line(surf,(210,210,150),(r.x,cy+off),(r.right,cy+off),2)
        pygame.draw.rect(surf,(35,45,58),(cx-78,cy-78,156,156)); pygame.draw.rect(surf,(95,110,126),(cx-86,cy-86,172,172),3)
        for v in sim.vehicles: v.draw(surf)
        positions={'NORTH':(cx-112,cy-112),'SOUTH':(cx+112,cy+112),'EAST':(cx+112,cy-112),'WEST':(cx-112,cy+112)}
        for d,p in positions.items(): self.light(surf,p,sim.signals[d].state); self.text(surf,d,(p[0]-24,p[1]-28),MUTED,self.small)
