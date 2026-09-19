#!/usr/bin/env python3
"""Geometrická závěra rovnoběžníku a servotáhla; čistý výpočet, žádný hardware."""
import math,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def mechanism(delta,h=15,kx=154,ky=44,arm=20,sx=184):
    t=math.radians(delta);length=math.hypot(kx+arm-sx+h,ky)
    ex,ey=kx+arm*math.cos(t),-ky+arm*math.sin(t)
    dx,dy=ex-sx,ey;r=math.hypot(dx,dy)
    c=(r*r+h*h-length*length)/(2*h*r)
    if not -1<=c<=1:raise ValueError('Vazbu nelze uzavřít')
    phi=math.atan2(dy,dx)-math.acos(c)+math.pi
    hx,hy=sx-h*math.cos(phi),-h*math.sin(phi)
    ux,uy=ex-hx,ey-hy
    ep=(-arm*math.sin(t),arm*math.cos(t));hp=(h*math.sin(phi),-h*math.cos(phi))
    ft=2*(ux*ep[0]+uy*ep[1]);fp=-2*(ux*hp[0]+uy*hp[1])
    if min(abs(ft),abs(fp))<1e-8:raise ValueError('Mrtvý bod')
    return {'wheel_deg':delta,'servo_deg':math.degrees(phi),'closure_mm':abs(math.hypot(ux,uy)-length),'d_wheel_d_servo':-fp/ft,'wheel_lever_mm':abs(ft)/(2*length),'servo_lever_mm':abs(fp)/(2*length),'length_mm':length}

def audit(h=15):
    points=[mechanism(i/100,h) for i in range(-2400,2401)]
    assert max(p['closure_mm'] for p in points)<1e-9
    assert all(p['d_wheel_d_servo']<0 for p in points)
    assert max(abs(p['servo_deg']) for p in points)<75
    assert all(a['servo_deg']>b['servo_deg'] for a,b in zip(points,points[1:]))
    return {'horn_radius_mm':h,'sample_count':len(points),'wheel_range_deg':[-24,24],'servo_range_deg':[points[-1]['servo_deg'],points[0]['servo_deg']],'working_endpoints':[mechanism(-20,h),mechanism(20,h)],'maximum_closure_error_mm':max(p['closure_mm'] for p in points),'minimum_wheel_moment_arm_mm':min(p['wheel_lever_mm'] for p in points),'minimum_servo_moment_arm_mm':min(p['servo_lever_mm'] for p in points),'derivative_range':[min(p['d_wheel_d_servo'] for p in points),max(p['d_wheel_d_servo'] for p in points)],'continuous_monotonic_same_branch':True,'no_dead_centre':True}
if __name__=='__main__':
    out={'nominal':audit(),'parameter_samples':[audit(14.5),audit(15.5)],'limit':'Ideální tuhé vazby a body, bez deformace, vůle nebo fyzické kalibrace serva.'}
    rejected=False
    try:audit(1)
    except (ValueError,AssertionError):rejected=True
    assert rejected
    out['impossible_horn_radius_1_mm_rejected']=rejected
    (ROOT/'kinematika.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(out['nominal'],ensure_ascii=False))
