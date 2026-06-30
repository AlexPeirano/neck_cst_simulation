skin = {'length': 1.4, 'NaCl': 5.39, 'TritonX100': 406.8, 'water': 614.1, 'quad': 0.05}

fat = {'length': 6.7, 'NaCl': 0.0, 'TritonX100': 1048, 'water': 12.4, 'quad': 2}

muscle  = {'length': 30, 'NaCl': 5.01, 'TritonX100': 240.3, 'water': 771.2, 'quad': 0.07}

bone  = {'length': 6.925, 'NaCl': 0.84, 'TritonX100': 888.2, 'water': 162.5, 'quad': 0.56}

csf  = {'length': 2.2, 'NaCl': 14.28, 'TritonX100': 79.7, 'water': 918.2, 'quad': 0.05}

spinal_cord  = {'length': 10, 'NaCl': 3.74, 'TritonX100': 530.2, 'water': 498.6, 'quad': 0.03}

matériaux = [skin, fat, muscle, bone, csf, spinal_cord]

radius = sum(i.get('length') for i in matériaux)

for mat in matériaux:
    mat['relative length'] = mat['length']/radius
    mat['relative NaCl'] = mat['NaCl']*mat['relative length']
    mat['relative TritonX100'] = mat['TritonX100']*mat['relative length']
    mat['relative water'] = mat['water']*mat['relative length']

NaCl = 0
TritonX100 = 0
water = 0

for mat in matériaux:
    NaCl += mat['relative NaCl']
    TritonX100 += mat['relative TritonX100']
    water += mat['relative water']
    
print(NaCl)
print(TritonX100)
print(water)


