def format_price(p):
    p = round(float(p), 2)
    p = str(p)
    pt_idx = p.index('.')
    while pt_idx > 3:
        pt_idx -= 3
        p = p[:pt_idx] + ',' + p[pt_idx:]
    if len(p.split('.')[1]) == 1:
        p += '0'
    return '$' + p

def format_perc(r):
    return str(round(100 * r)) + '%'
