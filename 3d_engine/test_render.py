import sys
sys.path.insert(0, r'd:\ethan\games_in_python\3d_engine')
import _engine3d as engine
import time
import traceback

print('module file', engine.__file__)
try:
    print('binding -> about to call engine.render()')
    p1 = engine.Point(); p1.x=-200; p1.y=-200; p1.z=-200
    p2 = engine.Point(); p2.x=200; p2.y=-200; p2.z=-200
    p3 = engine.Point(); p3.x=0; p3.y=200; p3.z=200
    trigs = [engine.Triangle(p1,p2,p3,(255,0,0))]
    model = engine.Model(trigs, (0,0,0), (0,0,0))
    engine.add_model(model)
    engine.update_camera(engine.Camera((0,0,-500),(0,0,0),105))
    print('calling render() now')
    frame = engine.render()
    print('render returned')
    print('shape', frame.shape, 'dtype', frame.dtype, 'size', frame.size)
except Exception as e:
    print('exception:', e)
    traceback.print_exc()
    time.sleep(1)
print('done')
