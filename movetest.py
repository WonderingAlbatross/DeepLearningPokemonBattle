import numpy as np
import vector_converter as vc
from poke_env.environment.move import Move
'''
#priority v[0]
print(vc.move_vectorize("bulletpunch"))

#power and catagory v[1],v[2]

#standard error for multiple-hits v[3]
print(vc.move_vectorize("bulletseed"))
print(vc.move_vectorize("surgingstrikes"))
print(vc.move_vectorize("tripleaxel"))
print(vc.move_vectorize("bonemerang"))

#accuracy v[4]
print(vc.move_vectorize("magicalleaf"))
print(vc.move_vectorize("inferno"))

#CT rate (crit_ratio) v[5]
print(vc.move_vectorize("crosspoison"))
print(vc.move_vectorize("frostbreath"))

#self boost v[6]-v[12]
print(vc.move_vectorize("scaleshot"))
print(vc.move_vectorize("ancientpower"))
print(vc.move_vectorize("dracometeor"))
print(vc.move_vectorize("honeclaws"))
print(vc.move_vectorize("acupressure"))

#enemy boost v[13]-v[19]
print(vc.move_vectorize("screech"))
print(vc.move_vectorize("muddywater"))
print(vc.move_vectorize("defog"))
print(vc.move_vectorize("partingshot"))

#status condition v[20]-v[25]
print(vc.move_vectorize("bounce"))
print(vc.move_vectorize("toxic"))
print(vc.move_vectorize("firefang"))
print(vc.move_vectorize("triattack"))

# heal and recoil: self% v[26] damage% v[27]
print(vc.move_vectorize("moonlight"))
print(vc.move_vectorize("lifedew"))
print(vc.move_vectorize("steelbeam"))
print(vc.move_vectorize("oblivionwing"))
print(vc.move_vectorize("bravebird"))
print(vc.move_vectorize("highjumpkick"))
print(vc.move_vectorize("strengthsap"))

print(vc.move_vectorize(Move("thunder")))

'''

print(vc.boosts_to_multi(-6))