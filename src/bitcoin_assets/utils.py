def format_price(p):
    p = round(p, 2)
    p = str(p)
    pt_idx = p.index('.')
    while pt_idx > 3:
        pt_idx -= 3
        p = p[:pt_idx] + ',' + p[pt_idx:]
    if len(p.split('.')[1]) == 1:
        p += '0'
    return '$' + p
