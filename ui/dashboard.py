import pygame
from algorithms.traffic_optimizer import DIRECTIONS
from simulation.signal import GREEN, YELLOW

BG=(12,18,30); PANEL=(22,32,49); TEXT=(226,234,245); MUTED=(139,152,174); ACCENT=(70,190,255)
GREEN_C=(65,221,132); YELLOW_C=(255,207,72); RED_C=(255,82,82)

class Dashboard:
    def __init__(self):
        pygame.font.init()
        self.title=pygame.font.SysFont('arial',34,bold=True)
        self.h2=pygame.font.SysFont('arial',21,bold=True)
        self.font=pygame.font.SysFont('arial',18)
        self.small=pygame.font.SysFont('arial',16)
        self.tiny=pygame.font.SysFont('arial',13)
        self.lab_buttons=[]
        self.result_buttons=[]

    def text(self,surf,msg,pos,color=TEXT,font=None):
        surf.blit((font or self.font).render(str(msg),True,color),pos)

    def panel(self,surf,rect,title):
        pygame.draw.rect(surf,PANEL,rect,border_radius=14)
        pygame.draw.rect(surf,(42,57,79),rect,1,border_radius=14)
        self.text(surf,title,(rect.x+18,rect.y+14),ACCENT,self.h2)

    def draw(self,surf,active,traditional,smart):
        w,h=surf.get_size()
        sim_rect=pygame.Rect(300,80,w-620,h-115)
        side=pygame.Rect(18,18,260,h-36)
        right=pygame.Rect(w-300,18,282,h-36)
        self.panel(surf,side,'SMARTFLOW')
        self.text(surf,'Adaptive Traffic Management System',(36,60),MUTED,self.small)
        self.text(surf,f'Mode: {active.mode}',(36,94),GREEN_C if active.mode=='SMARTFLOW' else YELLOW_C,self.h2)
        if active.rush_hour: self.text(surf,'RUSH HOUR ACTIVE',(36,121),YELLOW_C,self.font)
        if smart.emergency_active: self.text(surf,'EMERGENCY PRIORITY ACTIVE',(36,145),RED_C,self.small)
        self.text(surf,'SPACE pause | M mode | R reset',(36,172),MUTED,self.tiny)
        self.text(surf,'S scenario lab | H rush | E emergency',(36,190),MUTED,self.tiny)
        self.text(surf,f'Speed {active.speed:.1f}x   Intensity {active.intensity:.1f}x',(36,211),TEXT,self.small)

        self.panel(surf,pygame.Rect(28,240,240,265),'LIVE TRAFFIC')
        y=276
        stats=active.road_stats()
        for d in DIRECTIONS:
            s=stats[d]
            level='HIGH' if s['density']>.66 else 'MEDIUM' if s['density']>.33 else 'LOW'
            color=RED_C if level=='HIGH' else YELLOW_C if level=='MEDIUM' else GREEN_C
            self.text(surf,d,(44,y),TEXT,self.h2)
            self.text(surf,f'Vehicles: {s["total"]}',(44,y+25),TEXT,self.small)
            self.text(surf,f'Traffic: {level}',(144,y+25),color,self.small)
            self.light(surf,(52,y+53),s['signal'])
            flow='FLOWING' if s['signal']==GREEN else 'CAUTION' if s['signal']==YELLOW else 'WAITING'
            self.text(surf,f'Status: {flow}',(72,y+44),MUTED,self.small)
            y+=62

        self.panel(surf,pygame.Rect(28,530,240,150),'CURRENT DECISION')
        dec=active.decision
        score=dec.scores.get(dec.direction,0)
        self.text(surf,f'Priority Road: {dec.direction}',(44,568),TEXT,self.small)
        self.text(surf,f'Priority Score: {score:.1f}',(44,592),ACCENT,self.small)
        self.text(surf,f'Adaptive Green: {dec.green_time:.1f}s',(44,616),GREEN_C,self.small)
        self.text(surf,'Reason:',(44,640),MUTED,self.tiny)
        self.text(surf,dec.reason[:34],(44,658),TEXT,self.tiny)

        self.draw_intersection(surf,sim_rect,active)
        self.panel(surf,right,'PERFORMANCE')
        self.metrics_table(surf,right,traditional,smart)
        return sim_rect

    def light(self,surf,pos,state):
        pygame.draw.circle(surf,GREEN_C if state==GREEN else YELLOW_C if state==YELLOW else RED_C,pos,7)

    def metrics_table(self,surf,rect,trad,smart):
        self.text(surf,'Metric',(rect.x+18,rect.y+58),MUTED,self.small)
        self.text(surf,'Traditional',(rect.x+115,rect.y+58),YELLOW_C,self.small)
        self.text(surf,'SmartFlow',(rect.x+205,rect.y+58),GREEN_C,self.small)
        rows=[
            ('Avg Wait',f'{trad.metrics.avg_wait:.1f}s',f'{smart.metrics.avg_wait:.1f}s'),
            ('Waiting',sum(s['waiting'] for s in trad.road_stats().values()),sum(s['waiting'] for s in smart.road_stats().values())),
            ('Cleared',trad.metrics.cleared,smart.metrics.cleared),
            ('Max Wait',f'{trad.metrics.max_wait:.1f}s',f'{smart.metrics.max_wait:.1f}s'),
            ('Changes',trad.metrics.signal_changes,smart.metrics.signal_changes),
            ('Processed',trad.metrics.cleared+len(trad.vehicles),smart.metrics.cleared+len(smart.vehicles))]
        y=104
        for name,a,b in rows:
            self.text(surf,name,(rect.x+18,rect.y+y),TEXT,self.small)
            self.text(surf,str(a),(rect.x+125,rect.y+y),TEXT,self.small)
            self.text(surf,str(b),(rect.x+215,rect.y+y),GREEN_C,self.small)
            y+=31
        self.text(surf,'Measured live; results vary by traffic pattern.',(rect.x+18,rect.bottom-52),MUTED,self.tiny)

    def draw_intersection(self,surf,r,sim):
        pygame.draw.rect(surf,(10,16,27),r,border_radius=18)
        pygame.draw.rect(surf,(42,57,79),r,1,border_radius=18)
        old_clip=surf.get_clip(); surf.set_clip(r.inflate(-2,-2))
        cx,cy=r.center
        road=(48,55,66); road2=(58,66,79); line=(226,221,176); edge=(205,214,225)
        road_w=196; lane_w=49; inter=196
        pygame.draw.rect(surf,road,(cx-road_w//2,r.y,road_w,r.h))
        pygame.draw.rect(surf,road,(r.x,cy-road_w//2,r.w,road_w))
        pygame.draw.rect(surf,road2,(cx-road_w//2,cy-road_w//2,road_w,road_w))
        stats=sim.road_stats()
        overlays={'NORTH':(cx-road_w//2,r.y,road_w,cy-road_w//2-r.y),'SOUTH':(cx-road_w//2,cy+road_w//2,road_w,r.bottom-cy-road_w//2),'EAST':(cx+road_w//2,cy-road_w//2,r.right-cx-road_w//2,road_w),'WEST':(r.x,cy-road_w//2,cx-road_w//2-r.x,road_w)}
        for d,st in stats.items():
            if st['density']>.66: pygame.draw.rect(surf,(78,48,55),overlays[d])
            elif st['density']>.33: pygame.draw.rect(surf,(64,58,45),overlays[d])
        for x in (cx-road_w//2,cx+road_w//2):
            pygame.draw.line(surf,edge,(x,r.y),(x,cy-road_w//2),2); pygame.draw.line(surf,edge,(x,cy+road_w//2),(x,r.bottom),2)
        for y in (cy-road_w//2,cy+road_w//2):
            pygame.draw.line(surf,edge,(r.x,y),(cx-road_w//2,y),2); pygame.draw.line(surf,edge,(cx+road_w//2,y),(r.right,y),2)
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
        z=10; stops=sim.stop_lines(r)
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
        arrow=(202,211,222)
        def arr(points): pygame.draw.polygon(surf,arrow,points)
        arr([(cx-30,cy-170),(cx-42,cy-145),(cx-34,cy-145),(cx-34,cy-118),(cx-26,cy-118),(cx-26,cy-145),(cx-18,cy-145)])
        arr([(cx+30,cy+170),(cx+42,cy+145),(cx+34,cy+145),(cx+34,cy+118),(cx+26,cy+118),(cx+26,cy+145),(cx+18,cy+145)])
        arr([(cx+170,cy-30),(cx+145,cy-42),(cx+145,cy-34),(cx+118,cy-34),(cx+118,cy-26),(cx+145,cy-26),(cx+145,cy-18)])
        arr([(cx-170,cy+30),(cx-145,cy+42),(cx-145,cy+34),(cx-118,cy+34),(cx-118,cy+26),(cx-145,cy+26),(cx-145,cy+18)])
        for v in sim.vehicles: v.draw(surf)
        positions={'NORTH':(cx-128,cy-128),'SOUTH':(cx+128,cy+128),'EAST':(cx+128,cy-128),'WEST':(cx-128,cy+128)}
        for d,p in positions.items():
            self.light(surf,p,sim.signals[d].state); self.text(surf,d,(p[0]-24,p[1]-28),MUTED,self.small)
        if sim.emergency_active: self.text(surf,f'Emergency Route: {sim.emergency_direction}',(r.x+20,r.y+18),RED_C,self.h2)
        surf.set_clip(old_clip)

    def draw_scenario_overlay(self,surf,runner):
        from simulation.scenario import SCENARIOS
        self.lab_buttons=[]; self.result_buttons=[]
        if runner.state=="idle": return
        w,h=surf.get_size()
        # Blur and darken the live simulation so the scenario status card is the visual focus.
        snapshot=surf.copy()
        small=pygame.transform.smoothscale(snapshot,(max(1,w//8),max(1,h//8)))
        blurred=pygame.transform.smoothscale(small,(w,h))
        surf.blit(blurred,(0,0))
        shade=pygame.Surface((w,h),pygame.SRCALPHA); shade.fill((2,6,14,145)); surf.blit(shade,(0,0))
        if runner.state=="menu":
            box=pygame.Rect(w//2-330,h//2-245,660,490)
            pygame.draw.rect(surf,PANEL,box,border_radius=18); pygame.draw.rect(surf,ACCENT,box,2,border_radius=18)
            self.text(surf,"SMARTFLOW SCENARIO LAB",(box.x+72,box.y+32),ACCENT,self.title)
            self.text(surf,"Choose a traffic situation to test",(box.x+176,box.y+78),TEXT,self.font)
            y=box.y+128
            for key,sc in SCENARIOS.items():
                r=pygame.Rect(box.x+70,y,520,70); self.lab_buttons.append((r,key))
                pygame.draw.rect(surf,(30,45,68),r,border_radius=12); pygame.draw.rect(surf,(57,82,112),r,1,border_radius=12)
                self.text(surf,sc.title,(r.x+24,r.y+12),GREEN_C if key!='emergency' else RED_C,self.h2)
                self.text(surf,sc.subtitle,(r.x+24,r.y+39),MUTED,self.small); y+=82
            self.text(surf,"Pick one. SmartFlow runs the fair experiment automatically.",(box.x+108,box.bottom-38),MUTED,self.small)
        elif runner.state in {"intro","traditional","resetting","smartflow"}:
            sc=runner.scenario; box=pygame.Rect(w//2-260,34,520,126)
            pygame.draw.rect(surf,PANEL,box,border_radius=14); pygame.draw.rect(surf,ACCENT,box,1,border_radius=14)
            title=f"SCENARIO: {sc.title}" if runner.state=="intro" else "RESETTING SAME SCENARIO..." if runner.state=="resetting" else ("TRADITIONAL TEST" if runner.state=="traditional" else "SMARTFLOW TEST")
            sub="Same traffic conditions will be tested on both systems." if runner.state=="intro" else "Fixed-time signal control" if runner.state=="traditional" else "Adaptive traffic control" if runner.state=="smartflow" else "Restoring the exact same seed, vehicles, and events."
            self.text(surf,title,(box.x+28,box.y+20),ACCENT,self.h2); self.text(surf,sub,(box.x+28,box.y+52),TEXT,self.font)
            if runner.state in {"traditional","smartflow"}:
                pct=min(1,runner.active_sim.time/max(.1,sc.duration)); elapsed=max(0,runner.active_sim.time); remaining=max(0,sc.duration-elapsed)
                self.text(surf,f'Simulation time: {elapsed:.1f}s / {sc.duration:.0f}s  •  {remaining:.1f}s remaining',(box.x+28,box.y+78),MUTED,self.small)
                pygame.draw.rect(surf,(37,49,66),(box.x+28,box.y+105,464,9),border_radius=5)
                pygame.draw.rect(surf,GREEN_C if runner.state=="smartflow" else YELLOW_C,(box.x+28,box.y+105,int(464*pct),9),border_radius=5)
        elif runner.state=="results": self._draw_results(surf,runner)

    def _draw_results(self,surf,runner):
        sc=runner.scenario; t=runner.results.get("TRADITIONAL"); sm=runner.results.get("SMARTFLOW")
        w,h=surf.get_size(); box=pygame.Rect(w//2-395,h//2-315,790,630)
        pygame.draw.rect(surf,PANEL,box,border_radius=18); pygame.draw.rect(surf,ACCENT,box,2,border_radius=18)
        self.text(surf,f"{sc.title} — RESULTS",(box.x+34,box.y+22),ACCENT,self.title)
        self.text(surf,"Same traffic • same starting state • same simulation duration",(box.x+36,box.y+65),MUTED,self.small)
        card_y=98
        trad_card=pygame.Rect(box.x+34,box.y+card_y,340,190); smart_card=pygame.Rect(box.x+416,box.y+card_y,340,190)
        pygame.draw.rect(surf,(30,39,56),trad_card,border_radius=12); pygame.draw.rect(surf,(30,39,56),smart_card,border_radius=12)
        pygame.draw.rect(surf,YELLOW_C,trad_card,2,border_radius=12); pygame.draw.rect(surf,GREEN_C,smart_card,2,border_radius=12)
        self.text(surf,"TRADITIONAL",(trad_card.x+20,trad_card.y+15),YELLOW_C,self.h2); self.text(surf,"SMARTFLOW",(smart_card.x+20,smart_card.y+15),GREEN_C,self.h2)
        rows=[("Average Wait",f"{t.avg_wait:.1f}s",f"{sm.avg_wait:.1f}s"),("Vehicles Cleared",t.vehicles_cleared,sm.vehicles_cleared),("Still Waiting",t.vehicles_waiting,sm.vehicles_waiting),("Maximum Wait",f"{t.max_wait:.1f}s",f"{sm.max_wait:.1f}s")]
        if sc.key=="emergency": rows=[("Emergency Wait",f"{t.emergency_wait or 0:.1f}s",f"{sm.emergency_wait or 0:.1f}s"),("Emergency Clear",f"{t.emergency_clear_time or 0:.1f}s",f"{sm.emergency_clear_time or 0:.1f}s"),("Overall Avg Wait",f"{t.avg_wait:.1f}s",f"{sm.avg_wait:.1f}s"),("Vehicles Cleared",t.vehicles_cleared,sm.vehicles_cleared)]
        if sc.key=="changing": rows[-1]=("Priority Changes",t.priority_changes,sm.priority_changes)
        yy=trad_card.y+52
        for name,a,b in rows:
            self.text(surf,name,(trad_card.x+20,yy),MUTED,self.small); self.text(surf,str(a),(trad_card.x+235,yy),TEXT,self.small)
            self.text(surf,name,(smart_card.x+20,yy),MUTED,self.small); self.text(surf,str(b),(smart_card.x+235,yy),GREEN_C,self.small); yy+=31
        wait_delta=t.avg_wait-sm.avg_wait; pct=(wait_delta/t.avg_wait*100) if t.avg_wait else 0
        section_y=box.y+305
        self.text(surf,"WHY SMARTFLOW IS BETTER",(box.x+34,section_y),ACCENT,self.h2)
        self.text(surf,"Traditional:",(box.x+36,section_y+36),YELLOW_C,self.small); self.text(surf,"Uses a fixed signal schedule, even when traffic changes.",(box.x+120,section_y+36),TEXT,self.small)
        self.text(surf,"SmartFlow:",(box.x+36,section_y+62),GREEN_C,self.small)
        explanation=sc.explanation if len(sc.explanation)<=88 else sc.explanation[:85]+"..."
        self.text(surf,explanation,(box.x+120,section_y+62),TEXT,self.small)
        if wait_delta>0: result=f"SmartFlow cut average waiting by {pct:.0f}% in this test."
        elif sm.vehicles_cleared>t.vehicles_cleared: result=f"SmartFlow cleared {sm.vehicles_cleared-t.vehicles_cleared} more vehicles in this test."
        else: result="SmartFlow adapted to live traffic; this short test produced a similar average wait."
        pygame.draw.rect(surf,(27,55,46),pygame.Rect(box.x+34,section_y+96,722,42),border_radius=10)
        self.text(surf,"RESULT:",(box.x+50,section_y+108),GREEN_C,self.small); self.text(surf,result,(box.x+118,section_y+108),TEXT,self.small)
        self.text(surf,"WHAT SMARTFLOW DID",(box.x+34,section_y+160),ACCENT,self.h2)
        for i,step in enumerate(sm.smart_steps[:3],1): self.text(surf,f"{i}. {step}",(box.x+54,section_y+190+(i-1)*25),TEXT,self.small)
        labels=[("RUN AGAIN","again"),("CHOOSE ANOTHER SCENARIO","choose"),("RETURN TO LIVE SIMULATION","live")]
        bx=box.x+35
        for label,action in labels:
            r=pygame.Rect(bx,box.bottom-55,220,36); self.result_buttons.append((r,action))
            pygame.draw.rect(surf,(30,45,68),r,border_radius=10); pygame.draw.rect(surf,ACCENT,r,1,border_radius=10)
            self.text(surf,label,(r.x+14,r.y+9),TEXT,self.small); bx+=235
