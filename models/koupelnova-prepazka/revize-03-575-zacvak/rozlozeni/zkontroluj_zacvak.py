"""Independent STL cross-sections and actual positive-E snap-region paths.

Requires Shapely. It does not alter geometry/G-code or certify physical fit.
"""
from collections import defaultdict
import json
from pathlib import Path
from shapely.geometry import LineString, Polygon, box
from shapely.ops import polygonize, unary_union
from vytvor_podlozku import read_stl


def section(vertices, triangles, z):
    """Intersect raw triangles away from layer boundaries; parity preserves holes."""
    lines = []
    for tri in triangles:
        points = [vertices[index] for index in tri]
        intersections = []
        for a,b in zip(points,points[1:]+points[:1]):
            if (a[2] < z < b[2]) or (b[2] < z < a[2]):
                t = (z-a[2])/(b[2]-a[2])
                intersections.append(tuple(round(a[i]+t*(b[i]-a[i]),7) for i in (0,1)))
        intersections = list(dict.fromkeys(intersections))
        if len(intersections)==2 and intersections[0]!=intersections[1]:
            lines.append(LineString(intersections))
    polygons = list(polygonize(lines))
    assert polygons, f'Empty/unclosed triangle section at Z{z}'
    result = Polygon()
    for polygon in polygons:
        result = result.symmetric_difference(Polygon(polygon.exterior))
    assert result.is_valid and result.area > 0
    return result


def audit_snap(geometry_audit, deposition, layer_z, out):
    by_layer = defaultdict(list)
    for move in deposition:
        if move['role']!='Brim':
            by_layer[move['layer']].append(move)
    reports=[]
    previews=[]
    for part in geometry_audit['parts']:
        vertices,triangles=read_stl(Path(__file__).resolve().parent.parent/part['stl'])
        tx,ty,_=part['translation_mm']
        length=part['nominal_cad_dimensions_mm'][0]
        sections={}
        layer_records=[]
        previous=None
        for number,z in layer_z.items():
            # Slicer samples each0.2mm layer at its middle plane.
            shape=section(vertices,triangles,z-0.1+1e-8)
            sections[number]=shape
            polygons=[shape] if shape.geom_type=='Polygon' else list(shape.geoms)
            components=len(polygons)
            # Rounded upper profiles may split a section while both regions
            # remain supported below. Only a newly unsupported component fails.
            unsupported_components=0 if previous is None else sum(polygon.intersection(previous).area<0.001 for polygon in polygons)
            assert unsupported_components==0, f"New unsupported island: {part['stl']} layer{number}"
            # All upper sections must remain supported within0.11mm XY of the
            # previous one. Female taper nominally advances0.10mm per layer.
            unsupported=0.0 if previous is None else shape.difference(previous.buffer(0.11, resolution=32)).area
            newly_exposed=0.0 if previous is None else shape.difference(previous).area
            assert unsupported<0.001, f"Overhang exceeds0.11mm/layer: {part['stl']} layer{number}: {unsupported}mm2"
            layer_records.append({'layer':number,'section_z_mm':z-0.1,'components':components,
                'new_unsupported_components':unsupported_components,
                'area_mm2':shape.area,'new_area_outside_previous_layer_mm2':newly_exposed,
                'area_beyond_previous_layer_plus_0_11mm_mm2':unsupported})
            previous=shape
        region_reports=[]
        for region in part['retention_audit_regions']:
            minimum=region.get('min_mm',region.get('min'))
            maximum=region.get('max_mm',region.get('max'))
            assert minimum and maximum, f'Unknown retention-region schema: {region}'
            roi=box(minimum[0],minimum[1],maximum[0],maximum[1])
            male=(minimum[0]+maximum[0])/2>length/2
            relevant=[]
            for number,z in layer_z.items():
                if z<minimum[2]-1e-6 or z>maximum[2]+1e-6: continue
                shape=sections[number]
                solid_roi=shape.intersection(roi)
                # Female ROI is intentionally a void: audit nearby cavity walls
                # in an expanded2mm box, requiring material only where STL has it.
                audited_roi=roi if male else roi.buffer(2,join_style=2).intersection(shape)
                moves=[]
                for move in by_layer[number]:
                    start=(move['start'][0]-tx,move['start'][1]-ty)
                    end=(move['end'][0]-tx,move['end'][1]-ty)
                    path=LineString([start,end])
                    if path.intersects(audited_roi):
                        clipped=path.intersection(audited_roi)
                        if clipped.length>1e-6: moves.append((clipped.length,move['role']))
                path_length=sum(item[0] for item in moves)
                assert path_length>0, f"Missing {'prong' if male else 'cavity-wall'} path: {part['stl']}, {region}, layer{number}"
                relevant.append({'layer':number,'z_mm':z,'solid_area_inside_exact_region_mm2':solid_roi.area,
                    'actual_depositing_centerline_length_in_audited_region_mm':path_length,
                    'roles':sorted(set(item[1] for item in moves))})
            region_reports.append({'region':region,'kind':'male retention prong' if male else 'female void plus adjacent cavity walls',
                'audited_region':'exact box' if male else 'box expanded2mm intersected with actual STL section; no extrusion required in void',
                'all_relevant_layers_have_actual_positive_e_paths':True,'layers':relevant})
        reports.append({'stl':part['stl'],'first_layer_components_on_bed':layer_records[0]['components'],
            'maximum_section_components':max(item['components'] for item in layer_records),
            'no_new_unsupported_components':True,
            'no_upper_layer_extends_beyond_previous_plus_0_11mm':True,'layers':layer_records,'retention_regions':region_reports})
        if part['retention_audit_regions']:
            for number in (1,6,14):
                shape=sections[number]
                for region in part['retention_audit_regions']:
                    minimum=region.get('min_mm',region.get('min')); maximum=region.get('max_mm',region.get('max'))
                    if (minimum[0]+maximum[0])/2>length/2:
                        previews.append((part,number,shape,(max(0,minimum[0]-8),min(length,maximum[0]+5))))
                        break
    result={'method':'Raw STL triangle sections at layer midpoint; actual G0/G1 positive-E moving centerlines only; no toolpath modification',
        'islands':'First layer starts on bed; every later section component overlaps material in the preceding layer. Multiple supported upper components are allowed.',
        'overhang':'Upper sections contained within previous section expanded0.11mm; nominal female taper0.1mm per0.2mm layer',
        'supports':'No detached starting islands or greater-than0.11mm/layer unsupported ledges found; experimental profile keeps support disabled',
        'parts':reports,'physical_limit':'No guarantee of TPU snap strength, friction, flex life or printability without a physical sample'}
    (out/'kontrola-zacvaknuti.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    render_prongs(previews,by_layer,layer_z,out)
    return {'report':'kontrola-zacvaknuti.json','parts_checked':len(reports),
        'all40_cross_sections_have_no_new_unsupported_components':True,'overhang_limit_mm_per_layer':0.11,
        'male_prongs_and_female_adjacent_walls_have_paths_every_relevant_layer':True}


def render_prongs(previews, by_layer, layer_z, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    count=len(previews)
    fig,axes=plt.subplots(3,count//3,figsize=(6*(count//3),10),squeeze=False,dpi=140)
    for i,(part,number,shape,xlim) in enumerate(previews):
        axis=axes[i%3][i//3]
        tx,ty,_=part['translation_mm']
        polygons=[shape] if shape.geom_type=='Polygon' else list(shape.geoms)
        for polygon in polygons:
            xs,ys=polygon.exterior.xy
            axis.plot(xs,ys,color='#999999',linewidth=0.6)
            for ring in polygon.interiors:
                xs,ys=ring.xy; axis.plot(xs,ys,color='#999999',linewidth=0.6)
        paths=[[(move['start'][0]-tx,move['start'][1]-ty),(move['end'][0]-tx,move['end'][1]-ty)] for move in by_layer[number]]
        axis.add_collection(LineCollection(paths,colors='#165c91',linewidths=0.65))
        axis.set(xlim=xlim,ylim=(5,20.5),aspect='equal',xlabel='místní X [mm]',ylabel='místní Y [mm]')
        axis.set_title(f"{part['stl']} · vrstva{number} · Z{layer_z[number]:g}mm")
        axis.grid(alpha=.2)
    fig.suptitle('Západky: skutečné extruzní dráhy a průřez STL',fontsize=16)
    fig.tight_layout(rect=(0,0,1,.95))
    fig.savefig(out/'nahled-drah-zapadek.png',facecolor='white')
    plt.close(fig)
